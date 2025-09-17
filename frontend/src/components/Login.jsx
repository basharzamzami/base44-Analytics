import React, { useState } from 'react'
import { Form, Input, Button, Card, Tabs, message } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined, BuildingOutlined } from '@ant-design/icons'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

const { TabPane } = Tabs

function Login() {
  const [loading, setLoading] = useState(false)
  const { login, register } = useAuth()
  const navigate = useNavigate()

  const onLogin = async (values) => {
    setLoading(true)
    const result = await login(values.email, values.password)
    setLoading(false)
    
    if (result.success) {
      message.success('Login successful!')
      navigate('/')
    } else {
      message.error(result.error)
    }
  }

  const onRegister = async (values) => {
    setLoading(true)
    const result = await register(
      {
        name: values.tenantName,
        plan: values.plan || 'starter'
      },
      {
        email: values.email,
        password: values.password,
        role: 'owner'
      }
    )
    setLoading(false)
    
    if (result.success) {
      message.success('Registration successful!')
      navigate('/')
    } else {
      message.error(result.error)
    }
  }

  return (
    <div className="login-container">
      <div className="login-content">
        <Card className="login-card">
          <div className="login-header">
            <h1>Base44</h1>
            <p>Palantir for SMBs</p>
          </div>
          
          <Tabs defaultActiveKey="login" centered>
            <TabPane tab="Login" key="login">
              <Form
                name="login"
                onFinish={onLogin}
                layout="vertical"
                size="large"
              >
                <Form.Item
                  name="email"
                  rules={[
                    { required: true, message: 'Please input your email!' },
                    { type: 'email', message: 'Please enter a valid email!' }
                  ]}
                >
                  <Input
                    prefix={<MailOutlined />}
                    placeholder="Email"
                  />
                </Form.Item>
                
                <Form.Item
                  name="password"
                  rules={[{ required: true, message: 'Please input your password!' }]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="Password"
                  />
                </Form.Item>
                
                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    block
                  >
                    Login
                  </Button>
                </Form.Item>
              </Form>
            </TabPane>
            
            <TabPane tab="Register" key="register">
              <Form
                name="register"
                onFinish={onRegister}
                layout="vertical"
                size="large"
              >
                <Form.Item
                  name="tenantName"
                  rules={[{ required: true, message: 'Please input your organization name!' }]}
                >
                  <Input
                    prefix={<BuildingOutlined />}
                    placeholder="Organization Name"
                  />
                </Form.Item>
                
                <Form.Item
                  name="email"
                  rules={[
                    { required: true, message: 'Please input your email!' },
                    { type: 'email', message: 'Please enter a valid email!' }
                  ]}
                >
                  <Input
                    prefix={<MailOutlined />}
                    placeholder="Email"
                  />
                </Form.Item>
                
                <Form.Item
                  name="password"
                  rules={[
                    { required: true, message: 'Please input your password!' },
                    { min: 8, message: 'Password must be at least 8 characters!' }
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="Password"
                  />
                </Form.Item>
                
                <Form.Item
                  name="confirmPassword"
                  dependencies={['password']}
                  rules={[
                    { required: true, message: 'Please confirm your password!' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('password') === value) {
                          return Promise.resolve()
                        }
                        return Promise.reject(new Error('Passwords do not match!'))
                      },
                    }),
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="Confirm Password"
                  />
                </Form.Item>
                
                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    block
                  >
                    Register
                  </Button>
                </Form.Item>
              </Form>
            </TabPane>
          </Tabs>
        </Card>
      </div>
    </div>
  )
}

export default Login

