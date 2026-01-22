/**
 * FK94 Security Platform - Stripe Client
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface CheckoutResponse {
  session_id: string;
  url: string;
}

export interface PortalResponse {
  url: string;
}

/**
 * Create a checkout session for Pro subscription
 */
export async function createCheckoutSession(
  userEmail: string,
  userId: string
): Promise<CheckoutResponse> {
  const response = await fetch(`${API_BASE}/stripe/create-checkout`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_email: userEmail,
      user_id: userId,
      success_url: `${window.location.origin}/dashboard?success=true`,
      cancel_url: `${window.location.origin}/pricing?cancelled=true`,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create checkout session');
  }

  return response.json();
}

/**
 * Create a customer portal session for managing subscription
 */
export async function createPortalSession(
  customerId: string
): Promise<PortalResponse> {
  const response = await fetch(`${API_BASE}/stripe/create-portal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      customer_id: customerId,
      return_url: `${window.location.origin}/dashboard`,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create portal session');
  }

  return response.json();
}

/**
 * Redirect to Stripe Checkout
 */
export async function redirectToCheckout(
  userEmail: string,
  userId: string
): Promise<void> {
  const { url } = await createCheckoutSession(userEmail, userId);
  window.location.href = url;
}

/**
 * Redirect to Stripe Customer Portal
 */
export async function redirectToPortal(customerId: string): Promise<void> {
  const { url } = await createPortalSession(customerId);
  window.location.href = url;
}
