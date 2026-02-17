import { useState, useEffect } from 'react'
import './CookieBanner.css'

function CookieBanner() {
  const [showBanner, setShowBanner] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [preferences, setPreferences] = useState({
    necessary: true, // Always true, cannot be disabled
    analytics: false,
    marketing: false
  })

  useEffect(() => {
    // Check if user has already made a choice
    const consent = localStorage.getItem('cookieConsent')
    if (!consent) {
      // Show banner after 1 second
      setTimeout(() => setShowBanner(true), 1000)
    }
  }, [])

  const acceptAll = () => {
    const allAccepted = {
      necessary: true,
      analytics: true,
      marketing: true,
      timestamp: new Date().toISOString()
    }
    localStorage.setItem('cookieConsent', JSON.stringify(allAccepted))
    setShowBanner(false)

    // Initialize analytics if accepted
    if (allAccepted.analytics) {
      // TODO: Initialize Google Analytics
      console.log('Analytics initialized')
    }
  }

  const acceptNecessary = () => {
    const necessaryOnly = {
      necessary: true,
      analytics: false,
      marketing: false,
      timestamp: new Date().toISOString()
    }
    localStorage.setItem('cookieConsent', JSON.stringify(necessaryOnly))
    setShowBanner(false)
  }

  const savePreferences = () => {
    const consent = {
      ...preferences,
      timestamp: new Date().toISOString()
    }
    localStorage.setItem('cookieConsent', JSON.stringify(consent))
    setShowBanner(false)

    // Initialize analytics if accepted
    if (preferences.analytics) {
      // TODO: Initialize Google Analytics
      console.log('Analytics initialized')
    }
  }

  if (!showBanner) return null

  return (
    <div className="cookie-banner-overlay">
      <div className="cookie-banner">
        <div className="cookie-content">
          <h3>🍪 Cookies & Datenschutz</h3>

          {!showSettings ? (
            <>
              <p>
                Wir verwenden Cookies, um die Benutzererfahrung zu verbessern und anonyme Nutzungsstatistiken zu erheben.
                Ihre Daten werden niemals an Dritte verkauft.
              </p>

              <div className="cookie-buttons">
                <button className="btn-accept-all" onClick={acceptAll}>
                  ✓ Alle akzeptieren
                </button>
                <button className="btn-necessary" onClick={acceptNecessary}>
                  Nur notwendige
                </button>
                <button className="btn-settings" onClick={() => setShowSettings(true)}>
                  ⚙️ Einstellungen
                </button>
              </div>

              <p className="cookie-links">
                <a href="/datenschutz" target="_blank">Datenschutzerklärung</a>
                {' • '}
                <a href="/impressum" target="_blank">Impressum</a>
              </p>
            </>
          ) : (
            <>
              <div className="cookie-settings">
                <div className="cookie-option">
                  <div className="cookie-option-header">
                    <input
                      type="checkbox"
                      checked={preferences.necessary}
                      disabled
                      id="necessary"
                    />
                    <label htmlFor="necessary">
                      <strong>Notwendige Cookies</strong>
                      <span className="required-badge">Erforderlich</span>
                    </label>
                  </div>
                  <p>Ermöglichen grundlegende Funktionen wie Navigation und Sicherheit. Können nicht deaktiviert werden.</p>
                </div>

                <div className="cookie-option">
                  <div className="cookie-option-header">
                    <input
                      type="checkbox"
                      checked={preferences.analytics}
                      onChange={(e) => setPreferences({...preferences, analytics: e.target.checked})}
                      id="analytics"
                    />
                    <label htmlFor="analytics">
                      <strong>Analyse-Cookies</strong>
                    </label>
                  </div>
                  <p>Helfen uns zu verstehen, wie Besucher die Website nutzen (anonymisiert).</p>
                </div>

                <div className="cookie-option">
                  <div className="cookie-option-header">
                    <input
                      type="checkbox"
                      checked={preferences.marketing}
                      onChange={(e) => setPreferences({...preferences, marketing: e.target.checked})}
                      id="marketing"
                    />
                    <label htmlFor="marketing">
                      <strong>Marketing-Cookies</strong>
                    </label>
                  </div>
                  <p>Ermöglichen personalisierte Werbung und Tracking über mehrere Websites.</p>
                </div>
              </div>

              <div className="cookie-buttons">
                <button className="btn-accept-all" onClick={acceptAll}>
                  Alle akzeptieren
                </button>
                <button className="btn-save" onClick={savePreferences}>
                  Auswahl speichern
                </button>
                <button className="btn-back" onClick={() => setShowSettings(false)}>
                  Zurück
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default CookieBanner
