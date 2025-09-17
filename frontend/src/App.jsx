import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import ConnectorSetup from './components/ConnectorSetup'
import DataMapping from './components/DataMapping'
import GraphExplorer from './components/GraphExplorer'
import Assistant from './components/Assistant'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import './styles/main.css'

function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <AuthProvider>
        <Router>
          <div className="app">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={<ProtectedRoute />}>
                <Route index element={<Dashboard />} />
                <Route path="connectors" element={<ConnectorSetup />} />
                <Route path="mapping" element={<DataMapping />} />
                <Route path="graph" element={<GraphExplorer />} />
                <Route path="assistant" element={<Assistant />} />
              </Route>
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ConfigProvider>
  )
}

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px'
      }}>
        Loading...
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default App

