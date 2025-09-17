import React, { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../services/api'

const AuthContext = createContext()

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [tenant, setTenant] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      // Verify token and get user info
      api.get('/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(response => {
        setUser(response.data)
        setLoading(false)
      })
      .catch(() => {
        localStorage.removeItem('token')
        setToken(null)
        setLoading(false)
      })
    } else {
      setLoading(false)
    }
  }, [token])

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', {
        username: email,
        password: password
      })
      
      const { access_token, tenant_id, user_id } = response.data
      
      localStorage.setItem('token', access_token)
      setToken(access_token)
      
      // Get user details
      const userResponse = await api.get('/auth/me', {
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      })
      
      setUser(userResponse.data)
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  const register = async (tenantData, userData) => {
    try {
      const response = await api.post('/auth/register', {
        tenant: tenantData,
        user: userData
      })
      
      const { access_token, tenant_id, user_id } = response.data
      
      localStorage.setItem('token', access_token)
      setToken(access_token)
      
      // Get user details
      const userResponse = await api.get('/auth/me', {
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      })
      
      setUser(userResponse.data)
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    setTenant(null)
  }

  const value = {
    user,
    tenant,
    token,
    isAuthenticated: !!token,
    loading,
    login,
    register,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

