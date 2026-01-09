import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_product(course_title):
    product = stripe.Product.create(name=course_title)
    return product

def create_stripe_price(amount, product_id):
    price = stripe.Price.create(
        unit_amount=int(amount * 100),
        currency="usd",
        product=product_id,
    )
    return price

def create_stripe_session(price_id):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
        success_url="https://127.0.0.1:8000/")
    return session

def get_stripe_session_status(session_id):
    return stripe.checkout.Session.retrieve(session_id)