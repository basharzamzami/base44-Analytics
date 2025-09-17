import React, { useState, useEffect } from 'react'
import { Card, Button, Select, Input, Row, Col, Typography, message } from 'antd'
import { SearchOutlined, ExpandOutlined, ShrinkOutlined } from '@ant-design/icons'

const { Option } = Select
const { Title, Text } = Typography

function GraphExplorer() {
  const [selectedNode, setSelectedNode] = useState(null)
  const [graphData, setGraphData] = useState({
    nodes: [],
    edges: []
  })
  const [loading, setLoading] = useState(false)

  // Mock data for demonstration
  const mockNodes = [
    { id: '1', label: 'Lead: John Doe', type: 'lead', properties: { email: 'john@example.com', status: 'qualified' } },
    { id: '2', label: 'Campaign: Google Ads', type: 'campaign', properties: { budget: 5000, status: 'active' } },
    { id: '3', label: 'Ad: Search Campaign', type: 'ad', properties: { platform: 'google', clicks: 150 } },
    { id: '4', label: 'Lead: Jane Smith', type: 'lead', properties: { email: 'jane@example.com', status: 'converted' } },
    { id: '5', label: 'Campaign: Facebook', type: 'campaign', properties: { budget: 3000, status: 'paused' } }
  ]

  const mockEdges = [
    { id: 'e1', source: '2', target: '1', type: 'generates', properties: { weight: 0.8 } },
    { id: 'e2', source: '3', target: '1', type: 'generates', properties: { weight: 0.9 } },
    { id: 'e3', source: '2', target: '3', type: 'contains', properties: { weight: 1.0 } },
    { id: 'e4', source: '5', target: '4', type: 'generates', properties: { weight: 0.7 } }
  ]

  useEffect(() => {
    setGraphData({
      nodes: mockNodes,
      edges: mockEdges
    })
  }, [])

  const handleNodeClick = (node) => {
    setSelectedNode(node)
  }

  const handleExpandNode = (nodeId) => {
    // TODO: Implement node expansion
    message.info(`Expanding node ${nodeId}`)
  }

  const handleSearch = (query) => {
    // TODO: Implement graph search
    message.info(`Searching for: ${query}`)
  }

  return (
    <div className="graph-explorer">
      <Row gutter={16}>
        <Col span={18}>
          <Card title="Graph Visualization" extra={
            <div>
              <Input.Search
                placeholder="Search nodes..."
                onSearch={handleSearch}
                style={{ width: 200, marginRight: 8 }}
              />
              <Button icon={<ExpandOutlined />} style={{ marginRight: 8 }}>
                Expand All
              </Button>
              <Button icon={<ShrinkOutlined />}>
                Collapse All
              </Button>
            </div>
          }>
            <div className="graph-container" style={{ 
              height: '600px', 
              border: '1px solid #d9d9d9', 
              borderRadius: '6px',
              padding: '20px',
              textAlign: 'center',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexDirection: 'column'
            }}>
              <div style={{ marginBottom: '20px' }}>
                <Text type="secondary">
                  Graph visualization will be implemented with a proper graph library
                </Text>
              </div>
              
              {/* Mock graph representation */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                {graphData.nodes.map(node => (
                  <div
                    key={node.id}
                    onClick={() => handleNodeClick(node)}
                    style={{
                      padding: '8px 16px',
                      border: '2px solid #1890ff',
                      borderRadius: '20px',
                      cursor: 'pointer',
                      backgroundColor: selectedNode?.id === node.id ? '#e6f7ff' : 'white',
                      margin: '5px'
                    }}
                  >
                    {node.label}
                  </div>
                ))}
              </div>
              
              <div style={{ marginTop: '20px', fontSize: '12px', color: '#666' }}>
                Click on nodes to select them
              </div>
            </div>
          </Card>
        </Col>
        
        <Col span={6}>
          <Card title="Node Details">
            {selectedNode ? (
              <div>
                <Title level={5}>{selectedNode.label}</Title>
                <Text type="secondary">Type: {selectedNode.type}</Text>
                <div style={{ marginTop: '16px' }}>
                  <Title level={5}>Properties:</Title>
                  {Object.entries(selectedNode.properties).map(([key, value]) => (
                    <div key={key} style={{ marginBottom: '8px' }}>
                      <Text strong>{key}:</Text> {value}
                    </div>
                  ))}
                </div>
                <Button 
                  type="primary" 
                  block 
                  style={{ marginTop: '16px' }}
                  onClick={() => handleExpandNode(selectedNode.id)}
                >
                  Expand Node
                </Button>
              </div>
            ) : (
              <Text type="secondary">Select a node to view details</Text>
            )}
          </Card>
          
          <Card title="Graph Statistics" style={{ marginTop: '16px' }}>
            <div style={{ marginBottom: '8px' }}>
              <Text strong>Nodes:</Text> {graphData.nodes.length}
            </div>
            <div style={{ marginBottom: '8px' }}>
              <Text strong>Edges:</Text> {graphData.edges.length}
            </div>
            <div style={{ marginBottom: '8px' }}>
              <Text strong>Connected Components:</Text> 2
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default GraphExplorer

