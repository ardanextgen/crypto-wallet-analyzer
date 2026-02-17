# ============================================================================
# STRIPE_ROUTES.PY - Stripe Payment Integration
# ============================================================================
#
# Endpoints:
#   POST /api/stripe/create-checkout-session  - Erstellt Checkout Session
#   POST /api/stripe/webhook                   - Stripe Webhooks
#   POST /api/stripe/create-portal-session    - Customer Portal
#
# ============================================================================

import os
import stripe
from fastapi import APIRouter, HTTPException, Request, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import logging

from ..database.database import get_db
from ..database.models import User

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

router = APIRouter(prefix="/api/stripe", tags=["Stripe"])


# ============================================================================
# REQUEST MODELS
# ============================================================================
class CheckoutSessionRequest(BaseModel):
    """Request für Checkout Session"""
    price_id: str  # Stripe Price ID (z.B. price_...)
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class PortalSessionRequest(BaseModel):
    """Request für Customer Portal"""
    customer_id: str  # Stripe Customer ID
    return_url: Optional[str] = None


# ============================================================================
# CHECKOUT SESSION - Erstellt Stripe Checkout
# ============================================================================
@router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutSessionRequest):
    """
    Erstellt eine Stripe Checkout Session für Subscription.

    Flow:
    1. User klickt "Get Pro" Button
    2. Frontend ruft diesen Endpoint auf
    3. Backend erstellt Checkout Session
    4. Frontend redirected zu Stripe Checkout
    5. User zahlt
    6. Stripe redirected zurück zur success_url
    7. Webhook informiert uns über erfolgreiche Zahlung

    Args:
        request: CheckoutSessionRequest mit price_id

    Returns:
        JSON mit checkout_url und session_id
    """
    try:
        # Bestimme Success/Cancel URLs
        success_url = request.success_url or "http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = request.cancel_url or "http://localhost:3000/pricing"

        logger.info(f"Creating checkout session for price: {request.price_id}")

        # Erstelle Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",  # Recurring payments
            line_items=[
                {
                    "price": request.price_id,
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            # Optional: Erlaube Promo-Codes
            allow_promotion_codes=True,
            # Optional: Sammle Billing-Adresse
            billing_address_collection="auto",
            # Customer Email vorausfüllen (wenn user eingeloggt)
            # customer_email="user@example.com",  # TODO: Von Auth-System holen
            # Subscription Details
            subscription_data={
                "trial_period_days": 7,  # 7-Tage Trial
                "metadata": {
                    "app": "cryptoguard",
                    "tier": "pro",
                }
            },
        )

        logger.info(f"Checkout session created: {checkout_session.id}")

        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create checkout session: {str(e)}"
        )


# ============================================================================
# CUSTOMER PORTAL - Stripe Customer Portal für Subscription Management
# ============================================================================
@router.post("/create-portal-session")
async def create_portal_session(request: PortalSessionRequest):
    """
    Erstellt Customer Portal Session.

    Ermöglicht Kunden:
    - Subscription kündigen
    - Zahlungsmethode ändern
    - Rechnungen downloaden
    - Subscription upgraden/downgraden

    Args:
        request: PortalSessionRequest mit customer_id

    Returns:
        JSON mit portal_url
    """
    try:
        return_url = request.return_url or "http://localhost:3000/account"

        # Erstelle Portal Session
        portal_session = stripe.billing_portal.Session.create(
            customer=request.customer_id,
            return_url=return_url,
        )

        logger.info(f"Portal session created for customer: {request.customer_id}")

        return {
            "portal_url": portal_session.url
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(e)}"
        )


# ============================================================================
# WEBHOOKS - Stripe Event Handler
# ============================================================================
@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Stripe Webhook Handler.

    Empfängt Events von Stripe wenn:
    - Zahlung erfolgreich
    - Subscription erstellt/aktualisiert/gekündigt
    - Zahlung fehlgeschlagen

    WICHTIG: Webhook Secret validieren!

    Events:
    - checkout.session.completed: Zahlung erfolgreich
    - customer.subscription.created: Subscription erstellt
    - customer.subscription.updated: Subscription geändert
    - customer.subscription.deleted: Subscription gekündigt
    - invoice.paid: Rechnung bezahlt
    - invoice.payment_failed: Zahlung fehlgeschlagen
    """
    payload = await request.body()

    # Verify webhook signature (WICHTIG für Security!)
    if not STRIPE_WEBHOOK_SECRET:
        logger.warning("STRIPE_WEBHOOK_SECRET not set - skipping verification")
        # In Production: NIEMALS ohne Verification!
        event = stripe.Event.construct_from(
            stripe.util.json.loads(payload), stripe.api_key
        )
    else:
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            logger.error("Invalid payload")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature")
            raise HTTPException(status_code=400, detail="Invalid signature")

    # Event Type
    event_type = event["type"]
    logger.info(f"Received webhook: {event_type}")

    # Handle different event types
    if event_type == "checkout.session.completed":
        # Zahlung erfolgreich!
        session = event["data"]["object"]
        await handle_checkout_completed(session, db)

    elif event_type == "customer.subscription.created":
        subscription = event["data"]["object"]
        await handle_subscription_created(subscription, db)

    elif event_type == "customer.subscription.updated":
        subscription = event["data"]["object"]
        await handle_subscription_updated(subscription, db)

    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        await handle_subscription_deleted(subscription, db)

    elif event_type == "invoice.paid":
        invoice = event["data"]["object"]
        await handle_invoice_paid(invoice, db)

    elif event_type == "invoice.payment_failed":
        invoice = event["data"]["object"]
        await handle_payment_failed(invoice, db)

    else:
        logger.info(f"Unhandled event type: {event_type}")

    return JSONResponse({"status": "success"})


# ============================================================================
# WEBHOOK EVENT HANDLERS
# ============================================================================
async def handle_checkout_completed(session, db: Session):
    """
    Handle successful checkout.

    Updates user in database to Pro status.
    """
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    customer_email = session.get("customer_details", {}).get("email")

    logger.info(f"Checkout completed: {customer_id}, {subscription_id}, {customer_email}")

    if not customer_email:
        logger.error("No customer email in checkout session!")
        return

    # Find user by email
    user = db.query(User).filter(User.email == customer_email).first()

    if user:
        # Update existing user
        user.subscription_status = "pro"
        user.stripe_customer_id = customer_id
        user.stripe_subscription_id = subscription_id
        db.commit()

        logger.info(f"✅ User upgraded to Pro: {user.email}")
        print(f"✅ User upgraded: {user.email} → Pro (Subscription: {subscription_id})")

    else:
        logger.warning(f"⚠️ No user found with email: {customer_email}")
        print(f"⚠️ Checkout successful but no user found: {customer_email}")
        print(f"   User should sign up first before purchasing!")


async def handle_subscription_created(subscription, db: Session):
    """Handle new subscription"""
    customer_id = subscription.get("customer")
    status = subscription.get("status")

    logger.info(f"Subscription created: {subscription['id']}, status: {status}")

    # User should already be updated by checkout.session.completed
    # This is just a confirmation


async def handle_subscription_updated(subscription, db: Session):
    """Handle subscription changes"""
    subscription_id = subscription["id"]
    customer_id = subscription.get("customer")
    status = subscription.get("status")
    cancel_at_period_end = subscription.get("cancel_at_period_end")

    logger.info(f"Subscription updated: {subscription_id}, status: {status}")

    # Find user
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
        # Update status if changed (e.g. from trialing to active)
        if status == "active" or status == "trialing":
            user.subscription_status = "pro"
        elif status == "past_due":
            logger.warning(f"Subscription past due: {user.email}")
        elif status == "canceled" or status == "unpaid":
            user.subscription_status = "free"

        db.commit()
        logger.info(f"User subscription updated: {user.email} → {user.subscription_status}")

    if cancel_at_period_end:
        logger.info(f"Subscription {subscription_id} will cancel at period end")


async def handle_subscription_deleted(subscription, db: Session):
    """Handle subscription cancellation"""
    customer_id = subscription.get("customer")

    logger.info(f"Subscription deleted: {subscription['id']}")

    # Downgrade user to Free tier
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()

    if user:
        user.subscription_status = "free"
        user.stripe_subscription_id = None
        db.commit()

        logger.info(f"✅ User downgraded to Free: {user.email}")
        print(f"❌ Subscription canceled: {user.email} → Free")


async def handle_invoice_paid(invoice, db: Session):
    """Handle successful payment"""
    subscription_id = invoice.get("subscription")
    customer_id = invoice.get("customer")
    amount_paid = invoice.get("amount_paid") / 100  # Convert cents to dollars

    logger.info(f"Invoice paid: {invoice['id']}, amount: ${amount_paid}")

    # Ensure user is still Pro (in case of renewal)
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user and user.subscription_status != "pro":
        user.subscription_status = "pro"
        db.commit()
        logger.info(f"User reactivated to Pro: {user.email}")


async def handle_payment_failed(invoice, db: Session):
    """Handle failed payment"""
    customer_id = invoice.get("customer")

    logger.error(f"Payment failed for customer: {customer_id}")

    # TODO: Send payment failure email
    # For now, just log it
    # User will remain Pro until subscription is actually canceled

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        logger.warning(f"⚠️ Payment failed for: {user.email}")
        print(f"⚠️ Payment failed for: {user.email} - Subscription at risk!")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
@router.get("/config")
async def get_stripe_config():
    """
    Returns Stripe Publishable Key für Frontend.
    PUBLIC endpoint - kein Secret Key!
    """
    publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")

    if not publishable_key:
        raise HTTPException(
            status_code=500,
            detail="Stripe not configured"
        )

    return {
        "publishable_key": publishable_key
    }
