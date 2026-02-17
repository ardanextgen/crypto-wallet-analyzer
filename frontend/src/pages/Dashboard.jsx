// ============================================================================
// DASHBOARD.JSX - User Dashboard
// ============================================================================

import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { startCheckout } from '../services/stripe'
import '../App.css'

function Dashboard() {
  const { user, logout, isAuthenticated, refreshUser } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    // Redirect wenn nicht eingeloggt
    if (!isAuthenticated) {
      navigate('/')
      return
    }

    // Refresh user data
    refreshUser()
  }, [isAuthenticated, navigate])

  if (!user) {
    return (
      <div className="app">
        <div className="container" style={{ padding: '60px 20px', textAlign: 'center' }}>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  const isPro = user.subscription_status === 'pro'
  const isFree = user.subscription_status === 'free'

  const handleUpgrade = async () => {
    const STRIPE_PRICE_ID = import.meta.env.VITE_STRIPE_PRO_PRICE_ID || 'price_YOUR_PRICE_ID_HERE'

    if (STRIPE_PRICE_ID === 'price_YOUR_PRICE_ID_HERE') {
      alert('⚠️ Stripe not configured yet!')
      return
    }

    await startCheckout(STRIPE_PRICE_ID)
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="logo">
            <span className="logo-icon">🛡️</span>
            <span className="logo-text">CryptoGuard</span>
          </div>
          <nav className="nav">
            <a href="/">Home</a>
            <a href="#" className="btn-primary" style={{ background: 'var(--glass-bg)' }}>{user.email}</a>
            <button onClick={logout} className="btn-primary" style={{ background: '#ef4444' }}>
              Logout
            </button>
          </nav>
        </div>
      </header>

      {/* Dashboard Content */}
      <section className="hero">
        <div className="container">
          <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px' }}>
            {/* Welcome */}
            <h1 className="hero-title" style={{ marginBottom: '10px' }}>
              Welcome Back! 👋
            </h1>
            <p className="hero-subtitle" style={{ marginBottom: '40px' }}>
              {user.email}
            </p>

            {/* Stats Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '40px' }}>
              {/* Subscription Status */}
              <div className="result-card">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '40px', marginBottom: '10px' }}>
                    {isPro ? '💎' : '⭐'}
                  </div>
                  <h3 style={{ fontSize: '16px', color: 'var(--text-secondary)', marginBottom: '5px' }}>
                    Plan
                  </h3>
                  <p style={{ fontSize: '24px', fontWeight: '700', color: 'var(--text-primary)' }}>
                    {user.subscription_status.toUpperCase()}
                  </p>
                </div>
              </div>

              {/* Usage Stats */}
              <div className="result-card">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '40px', marginBottom: '10px' }}>📊</div>
                  <h3 style={{ fontSize: '16px', color: 'var(--text-secondary)', marginBottom: '5px' }}>
                    Analyses Today
                  </h3>
                  <p style={{ fontSize: '24px', fontWeight: '700', color: 'var(--text-primary)' }}>
                    {user.usage_count} {isFree ? '/ 10' : ''}
                  </p>
                  {isFree && user.usage_count >= 10 && (
                    <p style={{ fontSize: '12px', color: '#ef4444', marginTop: '5px' }}>
                      Daily limit reached
                    </p>
                  )}
                </div>
              </div>

              {/* Account Age */}
              <div className="result-card">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '40px', marginBottom: '10px' }}>📅</div>
                  <h3 style={{ fontSize: '16px', color: 'var(--text-secondary)', marginBottom: '5px' }}>
                    Member Since
                  </h3>
                  <p style={{ fontSize: '18px', fontWeight: '600', color: 'var(--text-primary)' }}>
                    {new Date(user.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      year: 'numeric'
                    })}
                  </p>
                </div>
              </div>
            </div>

            {/* Upgrade CTA (nur für Free-User) */}
            {isFree && (
              <div className="result-card" style={{
                background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                padding: '30px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '48px', marginBottom: '15px' }}>🚀</div>
                <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '10px', color: 'var(--text-primary)' }}>
                  Upgrade to Pro
                </h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '20px', fontSize: '15px' }}>
                  Unlock unlimited analyses, AI-powered reports, and priority support
                </p>

                <div style={{
                  display: 'flex',
                  gap: '20px',
                  marginBottom: '25px',
                  justifyContent: 'center',
                  flexWrap: 'wrap'
                }}>
                  <div style={{ flex: '1', minWidth: '200px', textAlign: 'left' }}>
                    <div style={{ marginBottom: '10px' }}>✅ Unlimited wallet analyses</div>
                    <div style={{ marginBottom: '10px' }}>✅ AI-powered risk reports</div>
                    <div style={{ marginBottom: '10px' }}>✅ API access</div>
                  </div>
                  <div style={{ flex: '1', minWidth: '200px', textAlign: 'left' }}>
                    <div style={{ marginBottom: '10px' }}>✅ Priority support</div>
                    <div style={{ marginBottom: '10px' }}>✅ Export to PDF/CSV</div>
                    <div style={{ marginBottom: '10px' }}>✅ 7-day free trial</div>
                  </div>
                </div>

                <button onClick={handleUpgrade} className="analyze-btn" style={{ fontSize: '16px' }}>
                  Start Free Trial - $29/month
                </button>
              </div>
            )}

            {/* Pro Features (nur für Pro-User) */}
            {isPro && (
              <div className="result-card" style={{ padding: '30px', textAlign: 'center' }}>
                <div style={{ fontSize: '48px', marginBottom: '15px' }}>🎉</div>
                <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '10px', color: 'var(--text-primary)' }}>
                  You're a Pro Member!
                </h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
                  Enjoy unlimited analyses and all premium features
                </p>
                <a href="/#" className="pricing-btn">
                  Start Analyzing
                </a>
              </div>
            )}

            {/* Quick Actions */}
            <div style={{ marginTop: '40px', display: 'flex', gap: '15px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <a href="/" className="pricing-btn">
                🏠 Home
              </a>
              <a href="/#pricing" className="pricing-btn">
                💳 View Pricing
              </a>
              <a href="mailto:support@cryptoguard.io" className="pricing-btn">
                💬 Contact Support
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <p>© 2026 CryptoGuard. Protect your crypto investments.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Dashboard
