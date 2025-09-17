"""
Graph Analysis Service with Neo4j Integration
Provides graph analysis capabilities with fallback to in-memory implementation
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.graph import GraphNode, GraphEdge
from app.models.connector import NormalizedRecord

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

class MockGraphService:
    """Graph analysis service with Neo4j integration and in-memory fallback"""
    
    def __init__(self, neo4j_uri: str = None, neo4j_user: str = None, neo4j_password: str = None):
        self.neo4j_available = NEO4J_AVAILABLE and neo4j_uri
        self.neo4j_driver = None
        
        if self.neo4j_available:
            try:
                self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
                # Test connection
                with self.neo4j_driver.session() as session:
                    session.run("RETURN 1")
            except Exception as e:
                print(f"Neo4j connection failed: {e}")
                self.neo4j_available = False
        
        self.mock_graph_data = self._load_mock_graph_data()
    
    def _load_mock_graph_data(self) -> Dict[str, List[Dict]]:
        """Load mock graph data for different verticals"""
        return {
            "marketing_agency": {
                "nodes": [
                    {
                        "id": "campaign_1",
                        "type": "campaign",
                        "properties": {
                            "name": "Google Ads Search Campaign",
                            "budget": 5000,
                            "status": "active",
                            "platform": "google"
                        }
                    },
                    {
                        "id": "ad_1",
                        "type": "ad",
                        "properties": {
                            "headline": "Best Marketing Software",
                            "clicks": 150,
                            "impressions": 5000,
                            "ctr": 0.03
                        }
                    },
                    {
                        "id": "lead_1",
                        "type": "lead",
                        "properties": {
                            "email": "john@example.com",
                            "company": "TechCorp",
                            "status": "qualified",
                            "value": 2500
                        }
                    },
                    {
                        "id": "lead_2",
                        "type": "lead",
                        "properties": {
                            "email": "jane@example.com",
                            "company": "StartupIO",
                            "status": "converted",
                            "value": 5000
                        }
                    },
                    {
                        "id": "conversion_1",
                        "type": "conversion",
                        "properties": {
                            "amount": 5000,
                            "date": "2024-01-15",
                            "type": "sale"
                        }
                    }
                ],
                "edges": [
                    {
                        "source": "campaign_1",
                        "target": "ad_1",
                        "type": "contains",
                        "properties": {"weight": 1.0}
                    },
                    {
                        "source": "ad_1",
                        "target": "lead_1",
                        "type": "generates",
                        "properties": {"weight": 0.8, "timestamp": "2024-01-10"}
                    },
                    {
                        "source": "ad_1",
                        "target": "lead_2",
                        "type": "generates",
                        "properties": {"weight": 0.9, "timestamp": "2024-01-12"}
                    },
                    {
                        "source": "lead_2",
                        "target": "conversion_1",
                        "type": "converts_to",
                        "properties": {"weight": 1.0, "timestamp": "2024-01-15"}
                    }
                ]
            },
            "urgent_clinic": {
                "nodes": [
                    {
                        "id": "patient_1",
                        "type": "patient",
                        "properties": {
                            "first_name": "John",
                            "last_name": "Smith",
                            "age": 35,
                            "insurance": "BlueCross"
                        }
                    },
                    {
                        "id": "visit_1",
                        "type": "visit",
                        "properties": {
                            "chief_complaint": "Chest pain",
                            "wait_time": 25,
                            "treatment_time": 30,
                            "cost": 150
                        }
                    },
                    {
                        "id": "provider_1",
                        "type": "provider",
                        "properties": {
                            "name": "Dr. Johnson",
                            "specialty": "Emergency Medicine",
                            "experience": 10
                        }
                    },
                    {
                        "id": "diagnosis_1",
                        "type": "diagnosis",
                        "properties": {
                            "code": "R06.02",
                            "description": "Shortness of breath",
                            "severity": "moderate"
                        }
                    }
                ],
                "edges": [
                    {
                        "source": "patient_1",
                        "target": "visit_1",
                        "type": "has_visit",
                        "properties": {"weight": 1.0}
                    },
                    {
                        "source": "provider_1",
                        "target": "visit_1",
                        "type": "treats",
                        "properties": {"weight": 1.0}
                    },
                    {
                        "source": "visit_1",
                        "target": "diagnosis_1",
                        "type": "results_in",
                        "properties": {"weight": 0.9}
                    }
                ]
            },
            "local_police": {
                "nodes": [
                    {
                        "id": "incident_1",
                        "type": "incident",
                        "properties": {
                            "type": "Theft",
                            "location": "123 Main St",
                            "severity": "medium",
                            "status": "investigating"
                        }
                    },
                    {
                        "id": "officer_1",
                        "type": "officer",
                        "properties": {
                            "name": "Officer Smith",
                            "badge": "12345",
                            "experience": 5,
                            "department": "Patrol"
                        }
                    },
                    {
                        "id": "suspect_1",
                        "type": "suspect",
                        "properties": {
                            "name": "John Doe",
                            "age": 28,
                            "prior_convictions": 2
                        }
                    },
                    {
                        "id": "evidence_1",
                        "type": "evidence",
                        "properties": {
                            "type": "Fingerprint",
                            "location": "Scene",
                            "status": "analyzed"
                        }
                    }
                ],
                "edges": [
                    {
                        "source": "officer_1",
                        "target": "incident_1",
                        "type": "responds_to",
                        "properties": {"weight": 1.0, "response_time": 5}
                    },
                    {
                        "source": "incident_1",
                        "target": "suspect_1",
                        "type": "involves",
                        "properties": {"weight": 0.8}
                    },
                    {
                        "source": "incident_1",
                        "target": "evidence_1",
                        "type": "has_evidence",
                        "properties": {"weight": 0.9}
                    }
                ]
            }
        }
    
    def build_entity_graph(self, tenant_id: int, normalized_records: List[NormalizedRecord], 
                          vertical: str) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Build entity graph from normalized records"""
        
        nodes = []
        edges = []
        
        # Get mock graph data for this vertical
        mock_data = self.mock_graph_data.get(vertical, {"nodes": [], "edges": []})
        
        # Create nodes
        for node_data in mock_data["nodes"]:
            node = GraphNode(
                tenant_id=tenant_id,
                node_type=node_data["type"],
                props_json=node_data["properties"]
            )
            nodes.append(node)
        
        # Create edges (simplified for demo)
        for i, edge_data in enumerate(mock_data["edges"]):
            # Find corresponding nodes
            source_node = next((n for n in nodes if n.props_json.get("id") == edge_data["source"]), None)
            target_node = next((n for n in nodes if n.props_json.get("id") == edge_data["target"]), None)
            
            if source_node and target_node:
                edge = GraphEdge(
                    tenant_id=tenant_id,
                    src_node_id=source_node.id,
                    dst_node_id=target_node.id,
                    rel_type=edge_data["type"],
                    props_json=edge_data["properties"]
                )
                edges.append(edge)
        
        return nodes, edges
    
    def query_graph(self, tenant_id: int, query: str, vertical: str = None) -> Dict:
        """Query the graph with natural language or Cypher"""
        
        if self.neo4j_available:
            return self._query_neo4j(tenant_id, query)
        else:
            return self._query_mock_graph(tenant_id, query, vertical)
    
    def _query_neo4j(self, tenant_id: int, query: str) -> Dict:
        """Query Neo4j database"""
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(query)
                records = [dict(record) for record in result]
                
                return {
                    "success": True,
                    "results": records,
                    "count": len(records),
                    "query": query
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "count": 0
            }
    
    def _query_mock_graph(self, tenant_id: int, query: str, vertical: str) -> Dict:
        """Query mock graph data"""
        
        # Simple query parsing for demo
        query_lower = query.lower()
        
        if "shortest path" in query_lower:
            return self._find_shortest_path(tenant_id, query, vertical)
        elif "neighbors" in query_lower or "connected" in query_lower:
            return self._find_neighbors(tenant_id, query, vertical)
        elif "community" in query_lower or "cluster" in query_lower:
            return self._find_communities(tenant_id, query, vertical)
        elif "central" in query_lower or "important" in query_lower:
            return self._find_central_nodes(tenant_id, query, vertical)
        else:
            return self._general_graph_query(tenant_id, query, vertical)
    
    def _find_shortest_path(self, tenant_id: int, query: str, vertical: str) -> Dict:
        """Find shortest path between nodes"""
        mock_data = self.mock_graph_data.get(vertical, {"nodes": [], "edges": []})
        
        # Simple path finding (for demo)
        paths = [
            {
                "path": ["campaign_1", "ad_1", "lead_1"],
                "length": 2,
                "weight": 0.8,
                "description": "Campaign → Ad → Lead path"
            },
            {
                "path": ["patient_1", "visit_1", "diagnosis_1"],
                "length": 2,
                "weight": 0.9,
                "description": "Patient → Visit → Diagnosis path"
            }
        ]
        
        return {
            "success": True,
            "results": paths,
            "count": len(paths),
            "query_type": "shortest_path"
        }
    
    def _find_neighbors(self, tenant_id: int, query: str, vertical: str) -> Dict:
        """Find neighbors of a node"""
        mock_data = self.mock_graph_data.get(vertical, {"nodes": [], "edges": []})
        
        neighbors = []
        for edge in mock_data["edges"]:
            neighbors.append({
                "source": edge["source"],
                "target": edge["target"],
                "relationship": edge["type"],
                "weight": edge["properties"].get("weight", 1.0)
            })
        
        return {
            "success": True,
            "results": neighbors,
            "count": len(neighbors),
            "query_type": "neighbors"
        }
    
    def _find_communities(self, tenant_id: int, query: str, vertical: str) -> Dict:
        """Find communities/clusters in the graph"""
        
        communities = [
            {
                "community_id": 1,
                "nodes": ["campaign_1", "ad_1", "lead_1", "lead_2"],
                "size": 4,
                "description": "Marketing campaign cluster"
            },
            {
                "community_id": 2,
                "nodes": ["patient_1", "visit_1", "provider_1", "diagnosis_1"],
                "size": 4,
                "description": "Patient care cluster"
            }
        ]
        
        return {
            "success": True,
            "results": communities,
            "count": len(communities),
            "query_type": "communities"
        }
    
    def _find_central_nodes(self, tenant_id: int, query: str, vertical: str) -> Dict:
        """Find most central/important nodes"""
        
        central_nodes = [
            {
                "node_id": "ad_1",
                "centrality_score": 0.85,
                "node_type": "ad",
                "description": "High-performing ad with many connections"
            },
            {
                "node_id": "visit_1",
                "centrality_score": 0.78,
                "node_type": "visit",
                "description": "Key visit connecting patient and provider"
            }
        ]
        
        return {
            "success": True,
            "results": central_nodes,
            "count": len(central_nodes),
            "query_type": "centrality"
        }
    
    def _general_graph_query(self, tenant_id: int, query: str, vertical: str) -> Dict:
        """General graph query handler"""
        mock_data = self.mock_graph_data.get(vertical, {"nodes": [], "edges": []})
        
        # Return all nodes and edges for general queries
        all_data = {
            "nodes": mock_data["nodes"],
            "edges": mock_data["edges"],
            "statistics": {
                "total_nodes": len(mock_data["nodes"]),
                "total_edges": len(mock_data["edges"]),
                "node_types": list(set(node["type"] for node in mock_data["nodes"])),
                "edge_types": list(set(edge["type"] for edge in mock_data["edges"]))
            }
        }
        
        return {
            "success": True,
            "results": [all_data],
            "count": 1,
            "query_type": "general"
        }
    
    def get_graph_statistics(self, tenant_id: int, vertical: str = None) -> Dict:
        """Get graph statistics"""
        mock_data = self.mock_graph_data.get(vertical, {"nodes": [], "edges": []})
        
        node_types = {}
        edge_types = {}
        
        for node in mock_data["nodes"]:
            node_type = node["type"]
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        for edge in mock_data["edges"]:
            edge_type = edge["type"]
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        return {
            "total_nodes": len(mock_data["nodes"]),
            "total_edges": len(mock_data["edges"]),
            "node_types": node_types,
            "edge_types": edge_types,
            "density": len(mock_data["edges"]) / max(1, len(mock_data["nodes"]) * (len(mock_data["nodes"]) - 1) / 2),
            "average_degree": 2 * len(mock_data["edges"]) / max(1, len(mock_data["nodes"]))
        }
    
    def close(self):
        """Close Neo4j connection"""
        if self.neo4j_driver:
            self.neo4j_driver.close()

# Global instance
graph_service = MockGraphService()

