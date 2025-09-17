import React, { useState, useEffect } from 'react'
import { Layout, Card, Row, Col, Statistic, Alert, Button, List, Typography, Spin } from 'antd'
import { 
  DashboardOutlined, 
  AlertOutlined, 
  CheckCircleOutlined, 
  ExclamationCircleOutlined,
  PlusOutlined,
  EyeOutlined
} from '@ant-design/icons'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

const { Header, Content, Sider } = Layout
const { Title, Text } = Typography

function Dashboard() {
  const { user, logout } = useAuth()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [alerts, setAlerts] = useState([])
  const [kpis, setKpis] = useState([])

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load dashboard data
      const dashboardResponse = await api.get(`/dashboard/${user.tenant_id}`)
      setDashboardData(dashboardResponse.data)
      
      // Load alerts
      const alertsResponse = await api.get('/alerts')
      setAlerts(alertsResponse.data)
      
      // Load KPIs
      const kpisResponse = await api.get('/kpis')
      setKpis(kpisResponse.data)
      
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTask = (alertId) => {
    // TODO: Implement task creation
    console.log('Create task for alert:', alertId)
  }

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
        <p>Loading dashboard...</p>
      </div>
    )
  }

  return (
    <Layout className="dashboard-layout">
      <Header className="dashboard-header">
        <div className="header-content">
          <Title level={3} style={{ color: 'white', margin: 0 }}>
            <DashboardOutlined /> Base44 Dashboard
          </Title>
          <div className="header-actions">
            <Text style={{ color: 'white', marginRight: 16 }}>
              Welcome, {user?.email}
            </Text>
            <Button onClick={logout}>Logout</Button>
          </div>
        </div>
      </Header>
      
      <Layout>
        <Sider width={300} className="dashboard-sider">
          <div className="sider-content">
            <Title level={4}>Quick Actions</Title>
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              block 
              style={{ marginBottom: 16 }}
            >
              Add Connector
            </Button>
            <Button 
              icon={<EyeOutlined />} 
              block 
              style={{ marginBottom: 16 }}
            >
              View Data
            </Button>
            
            <Title level={4}>Active Alerts</Title>
            <List
              size="small"
              dataSource={alerts.slice(0, 5)}
              renderItem={(alert) => (
                <List.Item>
                  <Alert
                    message={alert.rule_json?.name || 'Alert'}
                    type={alert.severity === 'high' ? 'error' : 'warning'}
                    size="small"
                    action={
                      <Button 
                        size="small" 
                        onClick={() => handleCreateTask(alert.id)}
                      >
                        Create Task
                      </Button>
                    }
                  />
                </List.Item>
              )}
            />
          </div>
        </Sider>
        
        <Content className="dashboard-content">
          <Row gutter={[16, 16]}>
            {/* KPI Cards */}
            {kpis.map((kpi) => (
              <Col xs={24} sm={12} md={8} lg={6} key={kpi.id}>
                <Card>
                  <Statistic
                    title={kpi.name}
                    value={75.5} // Mock value
                    precision={1}
                    suffix="%"
                    valueStyle={{ color: '#3f8600' }}
                    prefix={<CheckCircleOutlined />}
                  />
                </Card>
              </Col>
            ))}
            
            {/* Recent Alerts */}
            <Col xs={24} lg={12}>
              <Card title="Recent Alerts" extra={<Button type="link">View All</Button>}>
                <List
                  dataSource={alerts.slice(0, 3)}
                  renderItem={(alert) => (
                    <List.Item
                      actions={[
                        <Button 
                          key="ack" 
                          size="small"
                          onClick={() => handleCreateTask(alert.id)}
                        >
                          Create Task
                        </Button>
                      ]}
                    >
                      <List.Item.Meta
                        avatar={
                          <ExclamationCircleOutlined 
                            style={{ 
                              color: alert.severity === 'high' ? '#ff4d4f' : '#faad14' 
                            }} 
                          />
                        }
                        title={alert.rule_json?.name || 'Alert'}
                        description={`Severity: ${alert.severity} - ${alert.triggered_at}`}
                      />
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
            
            {/* System Status */}
            <Col xs={24} lg={12}>
              <Card title="System Status">
                <Row gutter={16}>
                  <Col span={12}>
                    <Statistic
                      title="Data Sources"
                      value={2}
                      prefix={<CheckCircleOutlined />}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="Active KPIs"
                      value={kpis.length}
                      prefix={<DashboardOutlined />}
                    />
                  </Col>
                </Row>
                <div style={{ marginTop: 16 }}>
                  <Alert
                    message="System Healthy"
                    description="All services are running normally"
                    type="success"
                    showIcon
                  />
                </div>
              </Card>
            </Col>
          </Row>
        </Content>
      </Layout>
    </Layout>
  )
}

export default Dashboard

