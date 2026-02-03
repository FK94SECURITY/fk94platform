"""
FK94 Security Platform - Stripe Payment Service
"""
import asyncio
import logging
import stripe
from collections import OrderedDict
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class _IdempotencyCache:
    """LRU cache of processed Stripe event IDs to prevent duplicate handling."""

    def __init__(self, maxsize: int = 1000):
        self._cache: OrderedDict[str, dict] = OrderedDict()
        self._maxsize = maxsize

    def get(self, event_id: str) -> Optional[dict]:
        if event_id in self._cache:
            self._cache.move_to_end(event_id)
            return self._cache[event_id]
        return None

    def put(self, event_id: str, result: dict) -> None:
        self._cache[event_id] = result
        self._cache.move_to_end(event_id)
        while len(self._cache) > self._maxsize:
            self._cache.popitem(last=False)


class StripeService:
    def __init__(self):
        self.is_configured = bool(settings.STRIPE_SECRET_KEY)
        self._price_pro_monthly: Optional[str] = None
        self._price_lock = asyncio.Lock()
        self._webhook_cache = _IdempotencyCache()

    async def get_or_create_product(self) -> dict:
        """Get or create the FK94 Pro product and price"""
        if not self.is_configured:
            return {"error": "Stripe not configured"}

        async with self._price_lock:
            # Search for existing product
            products = stripe.Product.list(limit=10)
            pro_product = None

            for product in products.data:
                if product.name == "FK94 Pro":
                    pro_product = product
                    break

            # Create product if doesn't exist
            if not pro_product:
                pro_product = stripe.Product.create(
                    name="FK94 Pro",
                    description="Unlimited security scans, dark web monitoring, and priority support",
                    metadata={"plan": "pro"}
                )

            # Get or create price
            prices = stripe.Price.list(product=pro_product.id, active=True)

            if prices.data:
                price = prices.data[0]
            else:
                price = stripe.Price.create(
                    product=pro_product.id,
                    unit_amount=1000,  # $10.00 in cents
                    currency="usd",
                    recurring={"interval": "month"}
                )

            self._price_pro_monthly = price.id

        return {
            "product_id": pro_product.id,
            "price_id": price.id,
            "amount": price.unit_amount / 100,
            "currency": price.currency
        }

    async def create_checkout_session(
        self,
        user_email: str,
        user_id: str,
        success_url: str,
        cancel_url: str
    ) -> dict:
        """Create a Stripe Checkout session for Pro subscription"""
        if not self.is_configured:
            return {"error": "Stripe not configured"}

        # Ensure product exists
        if not self._price_pro_monthly:
            await self.get_or_create_product()

        try:
            session = stripe.checkout.Session.create(
                mode="subscription",
                payment_method_types=["card"],
                line_items=[{
                    "price": self._price_pro_monthly,
                    "quantity": 1
                }],
                customer_email=user_email,
                client_reference_id=user_id,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": user_id,
                    "plan": "pro"
                }
            )

            return {
                "session_id": session.id,
                "url": session.url
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    async def create_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> dict:
        """Create a Stripe Customer Portal session for managing subscription"""
        if not self.is_configured:
            return {"error": "Stripe not configured"}

        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return {"url": session.url}
        except stripe.error.StripeError as e:
            return {"error": str(e)}

    async def handle_webhook(self, payload: bytes, sig_header: str) -> dict:
        """Handle Stripe webhook events with idempotency."""
        if not settings.STRIPE_WEBHOOK_SECRET:
            return {"error": "Webhook secret not configured"}

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return {"error": "Invalid payload"}
        except stripe.error.SignatureVerificationError:
            return {"error": "Invalid signature"}

        # Idempotency: skip already-processed events
        event_id = event.get("id", "")
        cached = self._webhook_cache.get(event_id)
        if cached is not None:
            logger.info(f"Stripe webhook event {event_id} already processed, returning cached result")
            return cached

        event_type = event.get("type", "")
        data = event.get("data", {}).get("object", {})

        result = {"event": event_type, "handled": False}

        # Handle subscription events
        if event_type == "checkout.session.completed":
            # User completed checkout
            user_id = data.get("client_reference_id")
            customer_id = data.get("customer")
            result["user_id"] = user_id
            result["customer_id"] = customer_id
            result["action"] = "upgrade_to_pro"
            result["handled"] = True

        elif event_type == "customer.subscription.deleted":
            # Subscription cancelled
            customer_id = data.get("customer")
            result["customer_id"] = customer_id
            result["action"] = "downgrade_to_free"
            result["handled"] = True

        elif event_type == "customer.subscription.updated":
            # Subscription updated (could be upgrade/downgrade/payment issue)
            status = data.get("status")
            customer_id = data.get("customer")
            result["customer_id"] = customer_id
            result["status"] = status
            if status == "active":
                result["action"] = "subscription_active"
            elif status in ["past_due", "unpaid"]:
                result["action"] = "payment_failed"
            result["handled"] = True

        elif event_type == "invoice.payment_failed":
            customer_id = data.get("customer")
            result["customer_id"] = customer_id
            result["action"] = "payment_failed"
            result["handled"] = True

        # Cache the result for idempotency
        if event_id:
            self._webhook_cache.put(event_id, result)

        return result

    async def get_customer_subscription(self, customer_id: str) -> Optional[dict]:
        """Get customer's active subscription"""
        if not self.is_configured:
            return None

        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status="active",
                limit=1
            )

            if subscriptions.data:
                sub = subscriptions.data[0]
                return {
                    "id": sub.id,
                    "status": sub.status,
                    "current_period_end": sub.current_period_end,
                    "cancel_at_period_end": sub.cancel_at_period_end
                }
            return None
        except stripe.error.StripeError:
            return None


# Singleton
stripe_service = StripeService()
