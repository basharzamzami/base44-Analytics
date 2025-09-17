import React, { useState, useEffect } from 'react'
import { Card, Form, Select, Input, Button, Table, Tag, message, Modal } from 'antd'
import { PlusOutlined, SyncOutlined, DeleteOutlined } from '@ant-design/icons'
import api from '../services/api'

const { Option } = Select

function ConnectorSetup() {
  const [connectors, setConnectors] = useState([])
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()
  const [isModalVisible, setIsModalVisible] = useState(false)

  useEffect(() => {
    loadConnectors()
  }, [])

  const loadConnectors = async () => {
    try {
      setLoading(true)
      const response = await api.get('/connectors')
      setConnectors(response.data)
    } catch (error) {
      message.error('Failed to load connectors')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateConnector = async (values) => {
    try {
      await api.post('/connectors', values)
      message.success('Connector created successfully')
      setIsModalVisible(false)
      form.resetFields()
      loadConnectors()
    } catch (error) {
      message.error('Failed to create connector')
    }
  }

  const handleSync = async (connectorId) => {
    try {
      const response = await api.post(`/connectors/${connectorId}/sync`)
      message.success(`Sync completed: ${response.data.records_ingested} records ingested`)
      loadConnectors()
    } catch (error) {
      message.error('Sync failed')
    }
  }

  const handleDelete = async (connectorId) => {
    try {
      await api.delete(`/connectors/${connectorId}`)
      message.success('Connector deleted successfully')
      loadConnectors()
    } catch (error) {
      message.error('Failed to delete connector')
    }
  }

  const columns = [
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type) => <Tag color="blue">{type.toUpperCase()}</Tag>
    },
    {
      title: 'Status',
      dataIndex: 'last_sync_at',
      key: 'status',
      render: (lastSync) => (
        <Tag color={lastSync ? 'green' : 'orange'}>
          {lastSync ? 'Synced' : 'Never Synced'}
        </Tag>
      )
    },
    {
      title: 'Last Sync',
      dataIndex: 'last_sync_at',
      key: 'last_sync_at',
      render: (date) => date ? new Date(date).toLocaleString() : 'Never'
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <div>
          <Button
            type="primary"
            size="small"
            icon={<SyncOutlined />}
            onClick={() => handleSync(record.id)}
            style={{ marginRight: 8 }}
          >
            Sync
          </Button>
          <Button
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            Delete
          </Button>
        </div>
      )
    }
  ]

  return (
    <div className="connector-setup">
      <Card
        title="Data Connectors"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setIsModalVisible(true)}
          >
            Add Connector
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={connectors}
          loading={loading}
          rowKey="id"
          pagination={false}
        />
      </Card>

      <Modal
        title="Add New Connector"
        visible={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateConnector}
        >
          <Form.Item
            name="type"
            label="Connector Type"
            rules={[{ required: true, message: 'Please select connector type' }]}
          >
            <Select placeholder="Select connector type">
              <Option value="csv">CSV Upload</Option>
              <Option value="hubspot">HubSpot</Option>
              <Option value="google_ads">Google Ads</Option>
              <Option value="salesforce">Salesforce</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="config_json"
            label="Configuration"
            initialValue={{}}
          >
            <Input.TextArea
              placeholder='{"delimiter": ",", "has_header": true}'
              rows={4}
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Create Connector
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ConnectorSetup

