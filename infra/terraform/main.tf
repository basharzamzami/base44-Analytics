# Base44 Infrastructure - AWS ECS + RDS

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
resource "aws_vpc" "base44_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "base44-vpc"
  }
}

resource "aws_internet_gateway" "base44_igw" {
  vpc_id = aws_vpc.base44_vpc.id

  tags = {
    Name = "base44-igw"
  }
}

resource "aws_subnet" "base44_public_subnet" {
  count             = 2
  vpc_id            = aws_vpc.base44_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "base44-public-subnet-${count.index + 1}"
  }
}

resource "aws_subnet" "base44_private_subnet" {
  count             = 2
  vpc_id            = aws_vpc.base44_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "base44-private-subnet-${count.index + 1}"
  }
}

# RDS Subnet Group
resource "aws_db_subnet_group" "base44_db_subnet_group" {
  name       = "base44-db-subnet-group"
  subnet_ids = aws_subnet.base44_private_subnet[*].id

  tags = {
    Name = "base44-db-subnet-group"
  }
}

# Security Groups
resource "aws_security_group" "base44_web_sg" {
  name_prefix = "base44-web-"
  vpc_id      = aws_vpc.base44_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "base44-web-sg"
  }
}

resource "aws_security_group" "base44_db_sg" {
  name_prefix = "base44-db-"
  vpc_id      = aws_vpc.base44_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.base44_web_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "base44-db-sg"
  }
}

# RDS Instance
resource "aws_db_instance" "base44_postgres" {
  identifier = "base44-postgres"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "base44"
  username = "base44"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.base44_db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.base44_db_subnet_group.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = true

  tags = {
    Name = "base44-postgres"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "base44_redis_subnet_group" {
  name       = "base44-redis-subnet-group"
  subnet_ids = aws_subnet.base44_private_subnet[*].id
}

resource "aws_elasticache_replication_group" "base44_redis" {
  replication_group_id       = "base44-redis"
  description                = "Base44 Redis cluster"

  node_type            = "cache.t3.micro"
  port                 = 6379
  parameter_group_name = "default.redis7"

  num_cache_clusters = 1

  subnet_group_name  = aws_elasticache_subnet_group.base44_redis_subnet_group.name
  security_group_ids = [aws_security_group.base44_redis_sg.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {
    Name = "base44-redis"
  }
}

resource "aws_security_group" "base44_redis_sg" {
  name_prefix = "base44-redis-"
  vpc_id      = aws_vpc.base44_vpc.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.base44_web_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "base44-redis-sg"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "base44_cluster" {
  name = "base44-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "base44-cluster"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "base44_backend" {
  family                   = "base44-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "base44-backend"
      image = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/base44-backend:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.base44_postgres.endpoint}:5432/${aws_db_instance.base44_postgres.db_name}"
        },
        {
          name  = "REDIS_URL"
          value = "redis://${aws_elasticache_replication_group.base44_redis.primary_endpoint_address}:6379"
        }
      ]

      secrets = [
        {
          name      = "SECRET_KEY"
          valueFrom = aws_secretsmanager_secret.base44_secret.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.base44_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "backend"
        }
      }
    }
  ])

  tags = {
    Name = "base44-backend-task"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "base44_logs" {
  name              = "/ecs/base44"
  retention_in_days = 30

  tags = {
    Name = "base44-logs"
  }
}

# Secrets Manager
resource "aws_secretsmanager_secret" "base44_secret" {
  name = "base44/secret-key"
}

resource "aws_secretsmanager_secret_version" "base44_secret_version" {
  secret_id     = aws_secretsmanager_secret.base44_secret.id
  secret_string = var.secret_key
}

# IAM Role for ECS
resource "aws_iam_role" "ecs_execution_role" {
  name = "base44-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

