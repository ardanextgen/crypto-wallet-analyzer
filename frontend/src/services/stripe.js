// ============================================================================
// STRIPE.JS - Stripe Checkout Integration
// ============================================================================

import { loadStripe } from '@stripe/stripe-js'

// Stripe Publishable Key aus .env laden
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)

/**
 * Startet Stripe Checkout für Pro-Plan
 *
 * Flow:
 * 1. Backend-API aufrufen (/api/stripe/create-checkout-session)
 * 2. Checkout URL bekommen
 * 3. User zu Stripe Checkout redirecten
 * 4. User zahlt
 * 5. Stripe redirected zurück zu /success oder /cancel
 *
 * @param {string} priceId - Stripe Price ID (z.B. price_...)
 * @returns {Promise<void>}
 */
export const startCheckout = async (priceId) => {
  try {
    // Backend-API URL
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

    // Erstelle Checkout Session über Backend
    const response = await fetch(`${apiUrl}/api/stripe/create-checkout-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        price_id: priceId,
        success_url: `${window.location.origin}/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${window.location.origin}/pricing`,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Checkout failed')
    }

    const { checkout_url } = await response.json()

    // Redirect zu Stripe Checkout
    window.location.href = checkout_url

  } catch (error) {
    console.error('Checkout Error:', error)
    alert('Payment failed. Please try again.')
  }
}

/**
 * Öffnet Stripe Customer Portal (für bestehende Kunden)
 *
 * Ermöglicht:
 * - Subscription kündigen
 * - Zahlungsmethode ändern
 * - Rechnungen downloaden
 *
 * @param {string} customerId - Stripe Customer ID
 * @returns {Promise<void>}
 */
export const openCustomerPortal = async (customerId) => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

    const response = await fetch(`${apiUrl}/api/stripe/create-portal-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        customer_id: customerId,
        return_url: `${window.location.origin}/account`,
      }),
    })

    if (!response.ok) {
      throw new Error('Failed to open portal')
    }

    const { portal_url } = await response.json()
    window.location.href = portal_url

  } catch (error) {
    console.error('Portal Error:', error)
    alert('Failed to open customer portal')
  }
}

/**
 * Lädt Stripe Publishable Key vom Backend
 * (für zusätzliche Sicherheit - Key nicht im Frontend hardcoden)
 *
 * @returns {Promise<string>}
 */
export const getStripeConfig = async () => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const response = await fetch(`${apiUrl}/api/stripe/config`)

    if (!response.ok) {
      throw new Error('Failed to get Stripe config')
    }

    const { publishable_key } = await response.json()
    return publishable_key

  } catch (error) {
    console.error('Config Error:', error)
    return null
  }
}
