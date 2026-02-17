// ============================================================================
// AUTHCONTEXT.JSX - Authentication State Management
// ============================================================================
//
// Verwaltet:
// - User Login/Logout State
// - JWT Token Storage
// - Auto-Login bei Page Reload
// - Protected Route Logic
//
// ============================================================================

import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  // API URL
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  // ============================================================================
  // INIT - Auto-Login bei Page Load
  // ============================================================================
  useEffect(() => {
    const storedToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }

    setLoading(false)
  }, [])

  // ============================================================================
  // SIGNUP - Neuen User registrieren
  // ============================================================================
  const signup = async (email, password) => {
    try {
      const response = await fetch(`${apiUrl}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Signup failed')
      }

      const data = await response.json()

      // Save token & user
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))

      setToken(data.access_token)
      setUser(data.user)

      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  // ============================================================================
  // LOGIN - User einloggen
  // ============================================================================
  const login = async (email, password) => {
    try {
      const response = await fetch(`${apiUrl}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }

      const data = await response.json()

      // Save token & user
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))

      setToken(data.access_token)
      setUser(data.user)

      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  // ============================================================================
  // LOGOUT - User ausloggen
  // ============================================================================
  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  // ============================================================================
  // REFRESH USER - Holt aktuelle User-Daten vom Server
  // ============================================================================
  const refreshUser = async () => {
    if (!token) return

    try {
      const response = await fetch(`${apiUrl}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        // Token ungültig → Logout
        logout()
        return
      }

      const userData = await response.json()
      setUser(userData)
      localStorage.setItem('user', JSON.stringify(userData))
    } catch (error) {
      console.error('Refresh user failed:', error)
      logout()
    }
  }

  // ============================================================================
  // CONTEXT VALUE
  // ============================================================================
  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    signup,
    login,
    logout,
    refreshUser
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// ============================================================================
// HOOK - useAuth()
// ============================================================================
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
