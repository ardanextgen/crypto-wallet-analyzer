// ============================================================================
// CANCEL.JSX - Checkout Cancel Page
// ============================================================================

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import '../App.css'

function Cancel() {
  const [countdown, setCountdown] = useState(10)

  // Countdown Timer zum automatischen Redirect
  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          window.location.href = '/#pricing'
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

      {/* Cancel Content */}
      <section className="hero">
        <div className="container">
          <div className="success-content" style={{
            maxWidth: '600px',
            margin: '0 auto',
            textAlign: 'center',
            padding: '60px 20px'
          }}>
            {/* Cancel Icon */}
            <div style={{
              fontSize: '80px',
              marginBottom: '30px',
              animation: 'fadeIn 0.5s ease'
            }}>
              ❌
            </div>

            {/* Title */}
            <h1 className="hero-title" style={{ marginBottom: '20px' }}>
              Checkout <span className="gradient-text">Cancelled</span>
            </h1>

            {/* Subtitle */}
            <p className="hero-subtitle" style={{ marginBottom: '40px' }}>
              No worries! Your payment was not processed.
            </p>

            {/* Info Box */}
            <div className="result-card" style={{ marginBottom: '40px' }}>
              <div style={{ marginBottom: '20px' }}>
                <h3 style={{ fontSize: '18px', marginBottom: '10px', color: 'var(--text-primary)' }}>
                  💡 Still Interested in CryptoGuard Pro?
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.6' }}>
                  Our Pro plan unlocks unlimited analyses, AI-powered reports, and priority support.
                  Try it free for 7 days!
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
                  ✨ What You're Missing:
                </h4>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  textAlign: 'left',
                  color: 'var(--text-secondary)',
                  fontSize: '14px'
                }}>
                  <li style={{ padding: '8px 0', borderBottom: '1px solid var(--glass-border)' }}>
                    ⚡ Unlimited wallet analyses (vs 10/day)
                  </li>
                  <li style={{ padding: '8px 0', borderBottom: '1px solid var(--glass-border)' }}>
                    🤖 AI-powered risk reports
                  </li>
                  <li style={{ padding: '8px 0', borderBottom: '1px solid var(--glass-border)' }}>
                    🔌 API access for automation
                  </li>
                  <li style={{ padding: '8px 0', borderBottom: '1px solid var(--glass-border)' }}>
                    📊 Export to PDF & CSV
                  </li>
                  <li style={{ padding: '8px 0' }}>
                    🎯 Priority customer support
                  </li>
                </ul>
              </div>

              <div style={{
                padding: '15px',
                background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
                borderRadius: '12px',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                marginTop: '20px'
              }}>
                <p style={{ fontSize: '14px', color: 'var(--text-primary)', margin: 0 }}>
                  🎁 <strong>Special Offer:</strong> Start your 7-day free trial now – no credit card required!
                </p>
              </div>
            </div>

            {/* CTA Buttons */}
            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '30px' }}>
              <a
                href="/#pricing"
                className="analyze-btn"
                style={{ textDecoration: 'none' }}
              >
                Try Pro Free
              </a>
              <Link
                to="/"
                className="pricing-btn"
                style={{ textDecoration: 'none' }}
              >
                Continue with Free
              </Link>
              <a
                href="mailto:support@cryptoguard.io"
                className="pricing-btn"
                style={{ textDecoration: 'none', display: 'inline-block' }}
              >
                Ask Questions
              </a>
            </div>

            {/* Auto-redirect Notice */}
            <p style={{
              fontSize: '14px',
              color: 'var(--text-tertiary)',
              marginTop: '40px'
            }}>
              Redirecting to pricing in {countdown} seconds...
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
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}

export default Cancel
