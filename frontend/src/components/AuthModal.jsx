// ============================================================================
// AUTHMODAL.JSX - Login/Signup Modal
// ============================================================================

import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import './AuthModal.css'

function AuthModal({ isOpen, onClose, initialMode = 'login' }) {
  const [mode, setMode] = useState(initialMode) // 'login' or 'signup'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { login, signup } = useAuth()

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validierung
    if (!email || !password) {
      setError('Please fill in all fields')
      return
    }

    if (mode === 'signup') {
      if (password.length < 8) {
        setError('Password must be at least 8 characters')
        return
      }

      if (password !== confirmPassword) {
        setError('Passwords do not match')
        return
      }
    }

    setLoading(true)

    // Login oder Signup
    const result = mode === 'login'
      ? await login(email, password)
      : await signup(email, password)

    setLoading(false)

    if (result.success) {
      // Success → Close Modal
      onClose()
      // Reset Form
      setEmail('')
      setPassword('')
      setConfirmPassword('')
    } else {
      setError(result.error)
    }
  }

  const switchMode = () => {
    setMode(mode === 'login' ? 'signup' : 'login')
    setError('')
    setPassword('')
    setConfirmPassword('')
  }

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        {/* Close Button */}
        <button className="auth-modal-close" onClick={onClose}>✕</button>

        {/* Header */}
        <div className="auth-modal-header">
          <div className="logo-icon" style={{ fontSize: '40px', marginBottom: '10px' }}>🛡️</div>
          <h2>{mode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            {mode === 'login'
              ? 'Login to access your dashboard'
              : 'Start analyzing wallets for free'}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="auth-form">
          {/* Email */}
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              autoComplete="email"
              disabled={loading}
            />
          </div>

          {/* Password */}
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={mode === 'signup' ? 'At least 8 characters' : '••••••••'}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              disabled={loading}
            />
          </div>

          {/* Confirm Password (nur bei Signup) */}
          {mode === 'signup' && (
            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="new-password"
                disabled={loading}
              />
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="auth-error">
              ⚠️ {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className="auth-submit-btn"
            disabled={loading}
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Login' : 'Sign Up'}
          </button>
        </form>

        {/* Switch Mode */}
        <div className="auth-switch">
          {mode === 'login' ? (
            <p>
              Don't have an account?{' '}
              <button onClick={switchMode} className="auth-switch-btn">
                Sign up
              </button>
            </p>
          ) : (
            <p>
              Already have an account?{' '}
              <button onClick={switchMode} className="auth-switch-btn">
                Login
              </button>
            </p>
          )}
        </div>

        {/* Features Info (nur bei Signup) */}
        {mode === 'signup' && (
          <div className="auth-features">
            <div className="auth-feature-item">✅ 10 free analyses per day</div>
            <div className="auth-feature-item">✅ Multi-chain support</div>
            <div className="auth-feature-item">✅ Risk scoring</div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AuthModal
