from fastapi import APIRouter, Depends, HTTPException, Request
from security.user_managment import fastapi_users
from schemas.request.payment import CheckoutRequest
from fastapi.responses import JSONResponse
from api.services.product import ProductCrud
from core.config import settings, logger
import stripe
import json

ADMIN = fastapi_users.current_user(superuser=True)
router = APIRouter()

# TODO add saving in database with using payment crud and -amount from product if payment completed


def handle_checkout_session_completed(session):
    logger.info(f"Payment succeeded for session: object id: {session['data']['object']['id']}")
    print(session)


def handle_checkout_session_expired(session):
    logger.info(f"Session expired: object id: {session['data']['object']['id']}")



def handle_async_payment_succeeded(session):
    logger.info(f"Async payment succeeded: {session['data']['object']['id']}")



def handle_async_payment_failed(session):
    logger.warning(f"Async payment failed: object id: {session['data']['object']['id']}")
    # Логіка для обробки невдалої асинхронної оплати


@router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutRequest,
                                  crud: ProductCrud = Depends(ProductCrud),
                                  superuser=Depends(ADMIN)):
    product = await crud.get_one(request.product_id)
    if product:
        if request.quantity <= product.amount:
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[{
                        "price_data": {
                            "currency": "UAH",
                            "product_data": {
                                "name": product.name,
                            },
                            "unit_amount": int(product.price * 100),
                        },
                        "quantity": request.quantity,
                    }],
                    mode="payment",
                    success_url=request.success_url,
                    cancel_url=request.cancel_url,
                )
                return JSONResponse({"checkout_url": session.url})
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=400,
                            detail=f"Only {int(product.amount)} items are available in stock,"
                                   f" but you requested {request.quantity}.")


@router.post("/webhook")
async def stripe_webhook(request: Request):
    event = None
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = json.loads(payload)
    except json.decoder.JSONDecodeError as e:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return JSONResponse(content={"success": False}, status_code=200)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload {e}")
    except stripe.error.SignatureVerificationError as e:

        raise HTTPException(status_code=400, detail=f"Invalid signature {e}")

    event_handlers = {
        "checkout.session.completed": handle_checkout_session_completed,
        "checkout.session.expired": handle_checkout_session_expired,
        "checkout.session.async_payment_succeeded": handle_async_payment_succeeded,
        "checkout.session.async_payment_failed": handle_async_payment_failed
    }

    handler = event_handlers.get(event["type"])
    if handler:
        handler(event)
    else:
        logger.info(f"Unhandled event type: {event['type']}")

    return {"status": True}
