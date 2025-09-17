import React, { useState } from 'react'
import { Card, Input, Button, List, Typography, Tag, message, Spin } from 'antd'
import { SendOutlined, RobotOutlined, BulbOutlined, LinkOutlined } from '@ant-design/icons'
import api from '../services/api'

const { TextArea } = Input
const { Title, Text } = Typography

function Assistant() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversation, setConversation] = useState([])

  const handleAsk = async () => {
    if (!question.trim()) {
      message.warning('Please enter a question')
      return
    }

    try {
      setLoading(true)
      const response = await api.post('/ask', { question })
      const data = response.data
      
      const newMessage = {
        id: Date.now(),
        question,
        answer: data.answer,
        suggestedActions: data.suggested_actions || [],
        sources: data.sources || [],
        confidence: data.confidence_score || 0,
        timestamp: new Date().toLocaleString()
      }
      
      setConversation(prev => [...prev, newMessage])
      setQuestion('')
    } catch (error) {
      message.error('Failed to get response from assistant')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleAsk()
    }
  }

  const handleActionClick = (action) => {
    // TODO: Implement action handling
    message.info(`Action: ${action.title}`)
  }

  return (
    <div className="assistant">
      <Card 
        title={
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <RobotOutlined style={{ marginRight: 8 }} />
            AI Assistant
          </div>
        }
        style={{ height: '80vh' }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          {/* Conversation Area */}
          <div style={{ flex: 1, overflowY: 'auto', marginBottom: 16 }}>
            {conversation.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#666' }}>
                <RobotOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <div>Ask me anything about your data, KPIs, or business insights!</div>
                <div style={{ fontSize: '12px', marginTop: '8px' }}>
                  Try: "What are my current KPIs?" or "Show me recent alerts"
                </div>
              </div>
            ) : (
              <List
                dataSource={conversation}
                renderItem={(message) => (
                  <List.Item style={{ border: 'none', padding: '16px 0' }}>
                    <div style={{ width: '100%' }}>
                      {/* Question */}
                      <div style={{ marginBottom: '12px' }}>
                        <Text strong>You:</Text>
                        <div style={{ 
                          background: '#f0f0f0', 
                          padding: '8px 12px', 
                          borderRadius: '8px',
                          marginTop: '4px'
                        }}>
                          {message.question}
                        </div>
                      </div>
                      
                      {/* Answer */}
                      <div style={{ marginBottom: '12px' }}>
                        <Text strong>Assistant:</Text>
                        <div style={{ 
                          background: '#e6f7ff', 
                          padding: '8px 12px', 
                          borderRadius: '8px',
                          marginTop: '4px'
                        }}>
                          {message.answer}
                        </div>
                        <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                          Confidence: <Tag color={message.confidence > 0.8 ? 'green' : message.confidence > 0.6 ? 'orange' : 'red'}>
                            {(message.confidence * 100).toFixed(0)}%
                          </Tag>
                        </div>
                      </div>
                      
                      {/* Suggested Actions */}
                      {message.suggestedActions.length > 0 && (
                        <div style={{ marginBottom: '12px' }}>
                          <Text strong>Suggested Actions:</Text>
                          <div style={{ marginTop: '8px' }}>
                            {message.suggestedActions.map((action, index) => (
                              <Button
                                key={index}
                                type="primary"
                                size="small"
                                icon={<BulbOutlined />}
                                onClick={() => handleActionClick(action)}
                                style={{ marginRight: '8px', marginBottom: '4px' }}
                              >
                                {action.title}
                              </Button>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* Sources */}
                      {message.sources.length > 0 && (
                        <div>
                          <Text strong>Sources:</Text>
                          <div style={{ marginTop: '4px' }}>
                            {message.sources.map((source, index) => (
                              <Tag key={index} icon={<LinkOutlined />} style={{ marginBottom: '4px' }}>
                                {source}
                              </Tag>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <div style={{ fontSize: '12px', color: '#999', marginTop: '8px' }}>
                        {message.timestamp}
                      </div>
                    </div>
                  </List.Item>
                )}
              />
            )}
          </div>
          
          {/* Input Area */}
          <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: '16px' }}>
            <TextArea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your data... (Ctrl+Enter to send)"
              autoSize={{ minRows: 2, maxRows: 4 }}
              style={{ marginBottom: '8px' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                Press Ctrl+Enter to send
              </Text>
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleAsk}
                loading={loading}
                disabled={!question.trim()}
              >
                Ask
              </Button>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default Assistant

