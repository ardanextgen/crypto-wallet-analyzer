import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './App.css'
import CookieBanner from './components/CookieBanner'
import AuthModal from './components/AuthModal'
import { useAuth } from './context/AuthContext'
import { startCheckout } from './services/stripe'

function App() {
  const [address, setAddress] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [expandedFeature, setExpandedFeature] = useState(null)
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authModalMode, setAuthModalMode] = useState('login')

  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()

  // Stripe Checkout Handler
  const handleProCheckout = async () => {
    // TODO: Replace with your actual Stripe Price ID from dashboard
    // Get this from: https://dashboard.stripe.com/test/products
    const STRIPE_PRICE_ID = import.meta.env.VITE_STRIPE_PRO_PRICE_ID || 'price_YOUR_PRICE_ID_HERE'

    if (STRIPE_PRICE_ID === 'price_YOUR_PRICE_ID_HERE') {
      alert('⚠️ Stripe not configured yet! Please add VITE_STRIPE_PRO_PRICE_ID to your .env file.')
      return
    }

    await startCheckout(STRIPE_PRICE_ID)
  }

  const analyzeWallet = async () => {
    if (!address.trim()) {
      setError('Please enter a wallet address')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/analyze-multichain/${address}`)
      const data = await response.json()

      if (!response.ok) throw new Error(data.detail || 'Analysis failed')

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (score) => {
    if (score <= 30) return '#10b981'
    if (score <= 60) return '#f59e0b'
    return '#ef4444'
  }

  const getRiskLabel = (level) => {
    const labels = {
      low: '✅ Low Risk',
      medium: '⚠️ Medium Risk',
      high: '🚨 High Risk'
    }
    return labels[level] || level
  }

  const features = [
    {
      id: 1,
      icon: '🌐',
      title: 'Multi-Chain Support',
      short: 'Analyze across all major blockchains',
      details: 'Our platform supports Ethereum, Solana, BSC, and Bitcoin. Simply paste any wallet address and we automatically detect the blockchain. No need to manually select - our AI does it for you instantly.'
    },
    {
      id: 2,
      icon: '⚡',
      title: 'Instant Analysis',
      short: 'Results in seconds, not minutes',
      details: 'Get comprehensive risk reports in under 5 seconds. Our advanced algorithms scan transaction history, token holdings, and interaction patterns across the entire blockchain to provide instant insights.'
    },
    {
      id: 3,
      icon: '🛡️',
      title: 'Scam Detection',
      short: 'Protect yourself from fraud',
      details: 'We maintain a constantly updated database of known scam addresses, malicious contracts, and suspicious patterns. Our 6-factor risk engine identifies red flags like mixer usage, pump-and-dump schemes, and honeypot tokens.'
    },
    {
      id: 4,
      icon: '📊',
      title: 'Detailed Reports',
      short: 'Complete wallet transparency',
      details: 'Access full transaction history, token portfolio analysis, wallet age metrics, and interaction patterns. Export reports for compliance, due diligence, or personal records. Premium users get AI-powered summaries.'
    }
  ]

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
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            {isAuthenticated ? (
              <>
                <a href="/dashboard" className="btn-primary" style={{ background: 'var(--glass-bg)' }}>
                  Dashboard
                </a>
                <button onClick={logout} className="btn-primary" style={{ background: '#ef4444' }}>
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => {
                    setAuthModalMode('login')
                    setAuthModalOpen(true)
                  }}
                  className="btn-primary"
                  style={{ background: 'var(--glass-bg)' }}
                >
                  Login
                </button>
                <button
                  onClick={() => {
                    setAuthModalMode('signup')
                    setAuthModalOpen(true)
                  }}
                  className="btn-primary"
                >
                  Get Started
                </button>
              </>
            )}
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">
              Multi-Chain Wallet
              <span className="gradient-text"> Risk Analyzer</span>
            </h1>
            <p className="hero-subtitle">
              Analyze crypto wallets across Ethereum, Solana, BSC & Bitcoin.
              Detect scams before they happen.
            </p>

            {/* Analyzer Widget */}
            <div className="analyzer-widget">
              <div className="input-group">
                <input
                  type="text"
                  className="wallet-input"
                  placeholder="Enter wallet address (ETH, SOL, BTC...)"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && analyzeWallet()}
                />
                <button
                  className="analyze-btn"
                  onClick={analyzeWallet}
                  disabled={loading}
                >
                  <svg className="analyze-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="2"/>
                    <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  {loading ? 'Analyzing...' : 'Analyze Now'}
                </button>
              </div>

              {error && (
                <div className="alert alert-error">
                  ❌ {error}
                </div>
              )}

              {result && (
                <div className="result-card">
                  <div className="result-header">
                    <div className="chain-badge">
                      {result.chain?.toUpperCase()} Chain
                    </div>
                    <div className="address-display">
                      {result.address?.substring(0, 10)}...{result.address?.substring(result.address.length - 8)}
                    </div>
                  </div>

                  <div className="risk-display">
                    <div className="risk-score-circle" style={{ borderColor: getRiskColor(result.risk_score?.total) }}>
                      <span className="risk-number">{result.risk_score?.total || 0}</span>
                      <span className="risk-max">/100</span>
                    </div>
                    <div className="risk-label" style={{ color: getRiskColor(result.risk_score?.total) }}>
                      {getRiskLabel(result.risk_score?.level)}
                    </div>
                  </div>

                  <div className="stats-grid">
                    <div className="stat">
                      <div className="stat-label">Balance</div>
                      <div className="stat-value">{result.balance?.toFixed(4)} {result.native_token}</div>
                    </div>
                    <div className="stat">
                      <div className="stat-label">Transactions</div>
                      <div className="stat-value">{result.transaction_count || 0}</div>
                    </div>
                  </div>

                  {result.risk_score?.factors && result.risk_score.factors.length > 0 && (
                    <div className="risk-factors">
                      <div className="factors-title">⚠️ Risk Factors:</div>
                      {result.risk_score.factors.map((factor, i) => (
                        <div key={i} className="factor-item">{factor}</div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Supported Chains */}
            <div className="supported-chains">
              <span className="chains-label">Supported:</span>
              <span className="chain-badge">Ethereum</span>
              <span className="chain-badge">Solana</span>
              <span className="chain-badge">BSC</span>
              <span className="chain-badge">Bitcoin</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features - Single Row with Accordion */}
      <section id="features" className="features">
        <div className="container">
          <h2 className="section-title">Why CryptoGuard?</h2>

          {/* Features Grid - All in One Row */}
          <div className="features-row">
            {features.map((feature) => (
              <div key={feature.id} className="feature-compact">
                <div
                  className="feature-compact-card"
                  onClick={() => setExpandedFeature(expandedFeature === feature.id ? null : feature.id)}
                >
                  <div className="feature-icon">{feature.icon}</div>
                  <h3>{feature.title}</h3>
                  <p>{feature.short}</p>
                  <div className="expand-indicator">
                    {expandedFeature === feature.id ? '−' : '+'}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Expanded Feature Details */}
          {expandedFeature && (
            <div className="feature-expanded">
              <div className="feature-expanded-content">
                <div className="feature-expanded-icon">
                  {features.find(f => f.id === expandedFeature)?.icon}
                </div>
                <h3>{features.find(f => f.id === expandedFeature)?.title}</h3>
                <p>{features.find(f => f.id === expandedFeature)?.details}</p>
                <button
                  className="close-expanded"
                  onClick={() => setExpandedFeature(null)}
                >
                  Close ✕
                </button>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="pricing">
        <div className="container">
          <h2 className="section-title">Simple Pricing</h2>
          <div className="pricing-grid">
            <div className="pricing-card">
              <h3>Free</h3>
              <div className="price">$0<span>/month</span></div>
              <ul className="features-list">
                <li>10 analyses per day</li>
                <li>Basic risk scoring</li>
                <li>Multi-chain support</li>
                <li>Community support</li>
              </ul>
              <button
                className="pricing-btn"
                onClick={() => {
                  setAuthModalMode('signup')
                  setAuthModalOpen(true)
                }}
              >
                Get Started
              </button>
            </div>

            <div className="pricing-card featured">
              <div className="featured-badge">MOST POPULAR</div>
              <h3>Pro</h3>
              <div className="price">$29<span>/month</span></div>
              <ul className="features-list">
                <li>Unlimited analyses</li>
                <li>AI-powered reports</li>
                <li>API access</li>
                <li>Priority support</li>
                <li>Export features</li>
              </ul>
              <button className="pricing-btn primary" onClick={handleProCheckout}>
                Start Free Trial
              </button>
              <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginTop: '10px' }}>
                7-day free trial • Cancel anytime
              </p>
            </div>

            <div className="pricing-card">
              <h3>Enterprise</h3>
              <div className="price">Custom</div>
              <ul className="features-list">
                <li>White-label solution</li>
                <li>Dedicated support</li>
                <li>Custom integrations</li>
                <li>SLA guarantees</li>
                <li>Bulk analysis</li>
              </ul>
              <button className="pricing-btn">Contact Sales</button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <p>© 2026 CryptoGuard. Protect your crypto investments.</p>
            <div className="footer-links">
              <a href="/impressum" target="_blank">Impressum</a>
              <span>•</span>
              <a href="/datenschutz" target="_blank">Datenschutz</a>
              <span>•</span>
              <a href="mailto:info@cryptoguard.io">Contact</a>
            </div>
          </div>
        </div>
      </footer>

      {/* Cookie Banner */}
      <CookieBanner />

      {/* Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialMode={authModalMode}
      />
    </div>
  )
}

export default App
