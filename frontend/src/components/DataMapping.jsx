import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Tag, message, Select, Input, Row, Col } from 'antd'
import { CheckOutlined, CloseOutlined, EyeOutlined } from '@ant-design/icons'
import api from '../services/api'

const { Option } = Select

function DataMapping() {
  const [mappings, setMappings] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedConnector, setSelectedConnector] = useState(null)
  const [connectors, setConnectors] = useState([])

  useEffect(() => {
    loadConnectors()
  }, [])

  const loadConnectors = async () => {
    try {
      const response = await api.get('/connectors')
      setConnectors(response.data)
    } catch (error) {
      message.error('Failed to load connectors')
    }
  }

  const loadMappingPreview = async (connectorId) => {
    try {
      setLoading(true)
      const response = await api.get(`/connectors/${connectorId}/map_preview`)
      setMappings(response.data.suggested_mappings || [])
    } catch (error) {
      message.error('Failed to load mapping preview')
    } finally {
      setLoading(false)
    }
  }

  const handleAcceptMapping = (mappingIndex) => {
    const newMappings = [...mappings]
    newMappings[mappingIndex].accepted = true
    setMappings(newMappings)
    message.success('Mapping accepted')
  }

  const handleRejectMapping = (mappingIndex) => {
    const newMappings = [...mappings]
    newMappings[mappingIndex].accepted = false
    setMappings(newMappings)
    message.success('Mapping rejected')
  }

  const columns = [
    {
      title: 'Source Field',
      dataIndex: 'source_field',
      key: 'source_field',
      render: (field) => <Tag color="blue">{field}</Tag>
    },
    {
      title: 'Target Field',
      dataIndex: 'target_field',
      key: 'target_field',
      render: (field) => <Tag color="green">{field}</Tag>
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (confidence) => (
        <Tag color={confidence > 0.8 ? 'green' : confidence > 0.6 ? 'orange' : 'red'}>
          {(confidence * 100).toFixed(0)}%
        </Tag>
      )
    },
    {
      title: 'Transformation',
      dataIndex: 'suggested_transformation',
      key: 'suggested_transformation',
      render: (transformation) => transformation || 'none'
    },
    {
      title: 'Status',
      dataIndex: 'accepted',
      key: 'status',
      render: (accepted, _, index) => {
        if (accepted === true) {
          return <Tag color="green" icon={<CheckOutlined />}>Accepted</Tag>
        } else if (accepted === false) {
          return <Tag color="red" icon={<CloseOutlined />}>Rejected</Tag>
        } else {
          return (
            <div>
              <Button
                type="primary"
                size="small"
                icon={<CheckOutlined />}
                onClick={() => handleAcceptMapping(index)}
                style={{ marginRight: 8 }}
              >
                Accept
              </Button>
              <Button
                danger
                size="small"
                icon={<CloseOutlined />}
                onClick={() => handleRejectMapping(index)}
              >
                Reject
              </Button>
            </div>
          )
        }
      }
    }
  ]

  return (
    <div className="data-mapping">
      <Card title="Data Field Mapping">
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={12}>
            <Select
              placeholder="Select a connector"
              style={{ width: '100%' }}
              onChange={(value) => {
                setSelectedConnector(value)
                loadMappingPreview(value)
              }}
            >
              {connectors.map(connector => (
                <Option key={connector.id} value={connector.id}>
                  {connector.type.toUpperCase()} - {connector.id}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={12}>
            <Button
              type="primary"
              icon={<EyeOutlined />}
              onClick={() => selectedConnector && loadMappingPreview(selectedConnector)}
              disabled={!selectedConnector}
            >
              Preview Mapping
            </Button>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={mappings}
          loading={loading}
          rowKey={(record, index) => index}
          pagination={false}
          locale={{
            emptyText: selectedConnector 
              ? 'Click "Preview Mapping" to see suggested mappings'
              : 'Select a connector to see field mappings'
          }}
        />

        {mappings.length > 0 && (
          <div style={{ marginTop: 16, textAlign: 'right' }}>
            <Button type="primary" size="large">
              Apply All Accepted Mappings
            </Button>
          </div>
        )}
      </Card>
    </div>
  )
}

export default DataMapping

