import stripe
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentService:
    """Service class for handling Stripe payments"""
    
    @staticmethod
    def create_checkout_session(order, payment, request):
        """Create a Stripe Checkout session"""
        try:
            # Get the current site domain
            current_site = get_current_site(request)
            domain = request.build_absolute_uri('/')
            
            # Create line items
            line_items = []
            for item in order.items.all():
                line_items.append({
                    'price_data': {
                        'currency': 'kes',
                        'product_data': {
                            'name': item.product_name,
                        },
                        'unit_amount': int(item.unit_price * 100),
                    },
                    'quantity': item.quantity,
                })
            
            # Add shipping if applicable
            if order.shipping_cost > 0:
                line_items.append({
                    'price_data': {
                        'currency': 'kes',
                        'product_data': {
                            'name': 'Shipping',
                        },
                        'unit_amount': int(order.shipping_cost * 100),
                    },
                    'quantity': 1,
                })
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=domain + reverse('payments:success') + f'?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=domain + reverse('payments:cancel'),
                client_reference_id=str(order.id),
                metadata={
                    'order_id': str(order.id),
                    'payment_id': str(payment.id)
                },
                shipping_address_collection={
                    'allowed_countries': ['KE', 'US', 'GB', 'CA', 'AU', 'IN', 'NG', 'ZA', 'EG', 'GH']
                }
            )
            
            return checkout_session
            
        except Exception as e:
            raise Exception(f"Stripe checkout creation failed: {str(e)}")
    
    @staticmethod
    def retrieve_session(session_id):
        """Retrieve a Stripe session"""
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except Exception as e:
            raise Exception(f"Failed to retrieve Stripe session: {str(e)}")
    
    @staticmethod
    def create_payment_intent(amount, currency='kes', metadata=None):
        """Create a Stripe Payment Intent"""
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency,
                metadata=metadata or {},
            )
            return payment_intent
        except Exception as e:
            raise Exception(f"Failed to create payment intent: {str(e)}")
    
    @staticmethod
    def confirm_payment(payment_intent_id):
        """Confirm a payment intent"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return payment_intent
        except Exception as e:
            raise Exception(f"Failed to confirm payment: {str(e)}")
    
    @staticmethod
    def refund_payment(payment_intent_id, amount=None):
        """Refund a payment"""
        try:
            refund = stripe.Refund.create(
                payment_intent=payment_intent_id,
                amount=int(amount * 100) if amount else None,
            )
            return refund
        except Exception as e:
            raise Exception(f"Failed to refund payment: {str(e)}")
    
    @staticmethod
    def verify_webhook_signature(payload, sig_header):
        """Verify Stripe webhook signature"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError:
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid signature")