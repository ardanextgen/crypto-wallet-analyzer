// ============================================================================
// SUCCESS.JSX - Checkout Success Page
// ============================================================================

import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import '../App.css'

function Success() {
  const [searchParams] = useSearchParams()
  const sessionId = searchParams.get('session_id')
  const [countdown, setCountdown] = useState(10)

  // Countdown Timer zum automatischen Redirect
  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          window.location.href = '/'
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [])

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
            <Link to="/" className="btn-primary">Back to Home</Link>
          </nav>
        </div>
      </header>

      {/* Success Content */}
      <section className="hero">
        <div className="container">
          <div className="success-content" style={{
            maxWidth: '600px',
            margin: '0 auto',
            textAlign: 'center',
            padding: '60px 20px'
          }}>
            {/* Success Icon */}
            <div style={{
              fontSize: '80px',
              marginBottom: '30px',
              animation: 'scaleIn 0.5s ease'
            }}>
              ✅
            </div>

            {/* Title */}
            <h1 className="hero-title" style={{ marginBottom: '20px' }}>
              Payment <span className="gradient-text">Successful!</span>
            </h1>

            {/* Subtitle */}
            <p className="hero-subtitle" style={{ marginBottom: '40px' }}>
              Welcome to CryptoGuard Pro! Your subscription is now active.
            </p>

            {/* Info Box */}
            <div className="result-card" style={{ marginBottom: '40px' }}>
              <div style={{ marginBottom: '20px' }}>
                <h3 style={{ fontSize: '18px', marginBottom: '10px', color: 'var(--text-primary)' }}>
                  🎉 What's Next?
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.6' }}>
                  Check your email for your receipt and welcome guide.
                  You now have unlimited access to all Pro features!
                </p>
              </div>

              <div style={{
                padding: '20px',
                background: 'var(--glass-bg)',
                borderRadius: '12px',
                border: '1px solid var(--glass-border)',
                marginBottom: '20px'
              }}>
                <h4 style={{ fontSize: '16px', marginBottom: '15px', color: 'var(--text-primary)' }}>
                  ✨ Your Pro Benefits:
                </h4>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  textAlign: 'left',
                  color: 'var(--text-secondary)',
                  fontSize: '14px'
                }}>
                  <li style={{ padding: '8px 0', borderBottom: '1px solid var(--glass-border)' }}>
                    ✅ Unlimited wallet analyses
                  </li>
                  <li style={{ padding: '8px 0', borderBottom: '1px solid var(--glass-border)' }}>
                    🤖 AI-powered risk reports
                  </li>
                  <li style={{ padding: '8px 0', borderBottom: '1px solid var(--glass-border)' }}>
                    🔌 API access for integrations
                  </li>
                  <li style={{ padding: '8px 0', borderBottom: '1px solid var(--glass-border)' }}>
                    📊 Export features (PDF, CSV)
                  </li>
                  <li style={{ padding: '8px 0' }}>
                    ⚡ Priority support
                  </li>
                </ul>
              </div>

              {sessionId && (
                <div style={{
                  fontSize: '12px',
                  color: 'var(--text-tertiary)',
                  marginTop: '20px',
                  padding: '10px',
                  background: 'var(--glass-bg)',
                  borderRadius: '8px'
                }}>
                  <strong>Session ID:</strong> {sessionId.substring(0, 20)}...
                </div>
              )}
            </div>

            {/* CTA Buttons */}
            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', marginBottom: '30px' }}>
              <Link to="/" className="analyze-btn" style={{ textDecoration: 'none' }}>
                Start Analyzing
              </Link>
              <a
                href="mailto:support@cryptoguard.io"
                className="pricing-btn"
                style={{ textDecoration: 'none', display: 'inline-block' }}
              >
                Contact Support
              </a>
            </div>

            {/* Auto-redirect Notice */}
            <p style={{
              fontSize: '14px',
              color: 'var(--text-tertiary)',
              marginTop: '40px'
            }}>
              Redirecting to homepage in {countdown} seconds...
            </p>
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

      <style>{`
        @keyframes scaleIn {
          from {
            transform: scale(0);
            opacity: 0;
          }
          to {
            transform: scale(1);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  )
}

export default Success
