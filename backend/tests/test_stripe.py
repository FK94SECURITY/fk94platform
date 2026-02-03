"""
FK94 Security Platform - Stripe Service Tests
Tests with mocked Stripe API calls.
"""
import pytest
from unittest.mock import patch, MagicMock
import stripe

from app.services.stripe_service import StripeService


@pytest.fixture
def stripe_svc():
    svc = StripeService()
    svc.is_configured = True
    return svc


@pytest.fixture
def unconfigured_svc():
    svc = StripeService()
    svc.is_configured = False
    return svc


# === Unconfigured ===

@pytest.mark.asyncio
async def test_checkout_unconfigured(unconfigured_svc):
    result = await unconfigured_svc.create_checkout_session("a@b.com", "u1", "http://ok", "http://cancel")
    assert "error" in result
    assert "not configured" in result["error"]


@pytest.mark.asyncio
async def test_portal_unconfigured(unconfigured_svc):
    result = await unconfigured_svc.create_portal_session("cus_123", "http://return")
    assert "error" in result


@pytest.mark.asyncio
async def test_product_unconfigured(unconfigured_svc):
    result = await unconfigured_svc.get_or_create_product()
    assert "error" in result


@pytest.mark.asyncio
async def test_subscription_unconfigured(unconfigured_svc):
    result = await unconfigured_svc.get_customer_subscription("cus_123")
    assert result is None


# === Webhook Handling ===

@pytest.mark.asyncio
async def test_webhook_checkout_completed(stripe_svc):
    """Checkout completed webhook is handled."""
    mock_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": "user_123",
                "customer": "cus_abc"
            }
        }
    }

    with patch("stripe.Webhook.construct_event", return_value=mock_event):
        result = await stripe_svc.handle_webhook(b"payload", "sig_header")

    assert result["handled"] is True
    assert result["action"] == "upgrade_to_pro"
    assert result["user_id"] == "user_123"
    assert result["customer_id"] == "cus_abc"


@pytest.mark.asyncio
async def test_webhook_subscription_deleted(stripe_svc):
    """Subscription deleted webhook is handled."""
    mock_event = {
        "type": "customer.subscription.deleted",
        "data": {"object": {"customer": "cus_abc"}}
    }

    with patch("stripe.Webhook.construct_event", return_value=mock_event):
        result = await stripe_svc.handle_webhook(b"payload", "sig")

    assert result["handled"] is True
    assert result["action"] == "downgrade_to_free"


@pytest.mark.asyncio
async def test_webhook_subscription_updated_active(stripe_svc):
    """Subscription updated to active."""
    mock_event = {
        "type": "customer.subscription.updated",
        "data": {"object": {"customer": "cus_abc", "status": "active"}}
    }

    with patch("stripe.Webhook.construct_event", return_value=mock_event):
        result = await stripe_svc.handle_webhook(b"payload", "sig")

    assert result["handled"] is True
    assert result["action"] == "subscription_active"


@pytest.mark.asyncio
async def test_webhook_payment_failed(stripe_svc):
    """Payment failed webhook."""
    mock_event = {
        "type": "invoice.payment_failed",
        "data": {"object": {"customer": "cus_abc"}}
    }

    with patch("stripe.Webhook.construct_event", return_value=mock_event):
        result = await stripe_svc.handle_webhook(b"payload", "sig")

    assert result["handled"] is True
    assert result["action"] == "payment_failed"


@pytest.mark.asyncio
async def test_webhook_invalid_signature(stripe_svc):
    """Invalid signature returns error."""
    with patch("stripe.Webhook.construct_event", side_effect=stripe.error.SignatureVerificationError("bad sig", "sig")):
        result = await stripe_svc.handle_webhook(b"payload", "bad_sig")

    assert "error" in result
    assert "signature" in result["error"].lower()


@pytest.mark.asyncio
async def test_webhook_invalid_payload(stripe_svc):
    """Invalid payload returns error."""
    with patch("stripe.Webhook.construct_event", side_effect=ValueError("bad")):
        result = await stripe_svc.handle_webhook(b"bad", "sig")

    assert "error" in result
    assert "payload" in result["error"].lower()


@pytest.mark.asyncio
async def test_webhook_no_secret():
    """No webhook secret configured returns error."""
    svc = StripeService()
    svc.is_configured = True
    from app.core.config import settings
    original = settings.STRIPE_WEBHOOK_SECRET
    settings.STRIPE_WEBHOOK_SECRET = ""
    result = await svc.handle_webhook(b"payload", "sig")
    settings.STRIPE_WEBHOOK_SECRET = original

    assert "error" in result


@pytest.mark.asyncio
async def test_webhook_unhandled_event(stripe_svc):
    """Unknown event type returns handled=False."""
    mock_event = {
        "type": "some.unknown.event",
        "data": {"object": {}}
    }

    with patch("stripe.Webhook.construct_event", return_value=mock_event):
        result = await stripe_svc.handle_webhook(b"payload", "sig")

    assert result["handled"] is False


# === Product & Checkout (mocked Stripe API) ===

@pytest.mark.asyncio
async def test_get_or_create_product_existing(stripe_svc):
    """Finds existing product and price."""
    mock_product = MagicMock()
    mock_product.id = "prod_123"
    mock_product.name = "FK94 Pro"

    mock_price = MagicMock()
    mock_price.id = "price_123"
    mock_price.unit_amount = 1000
    mock_price.currency = "usd"

    with patch("stripe.Product.list", return_value=MagicMock(data=[mock_product])):
        with patch("stripe.Price.list", return_value=MagicMock(data=[mock_price])):
            result = await stripe_svc.get_or_create_product()

    assert result["product_id"] == "prod_123"
    assert result["price_id"] == "price_123"
    assert result["amount"] == 10.0


@pytest.mark.asyncio
async def test_create_checkout_session(stripe_svc):
    """Creates checkout session."""
    mock_session = MagicMock()
    mock_session.id = "cs_123"
    mock_session.url = "https://checkout.stripe.com/cs_123"

    # Need product setup first
    mock_product = MagicMock()
    mock_product.id = "prod_123"
    mock_product.name = "FK94 Pro"
    mock_price = MagicMock()
    mock_price.id = "price_123"
    mock_price.unit_amount = 1000
    mock_price.currency = "usd"

    with patch("stripe.Product.list", return_value=MagicMock(data=[mock_product])):
        with patch("stripe.Price.list", return_value=MagicMock(data=[mock_price])):
            with patch("stripe.checkout.Session.create", return_value=mock_session):
                result = await stripe_svc.create_checkout_session(
                    "user@test.com", "user_1", "http://ok", "http://cancel"
                )

    assert result["session_id"] == "cs_123"
    assert "url" in result
