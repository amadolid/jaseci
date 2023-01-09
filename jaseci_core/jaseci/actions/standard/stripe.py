"""Built in actions for Jaseci"""
from jaseci.svc import MetaService
from jaseci.svc.stripe import STRIPE_ERR_MSG
from datetime import datetime
from jaseci.actions.live_actions import jaseci_action


@jaseci_action()
def create_product(name: str, description: str, metadata: dict = {}):
    """create product"""
    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Product.create(name=name, description=description, metadata=metadata)
    )


@jaseci_action()
def create_product_price(
    productId: str,
    amount: int,
    currency: str,
    interval: str,
    metadata: dict = {},
):
    """modify product price"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Price.create(
            product=productId,
            unit_amount=amount,
            currency=currency,
            recurring={"interval": interval},
            metadata=metadata,
        )
    )


@jaseci_action()
def product_list(detailed: bool):
    """retrieve all producs"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Product.list(**{"active": True} if detailed else {})
    )


@jaseci_action()
def create_customer(
    email: str,
    name: str,
    address: dict,
    payment_method_id: str,
    metadata: dict = {},
):
    """create customer"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Customer.create(
            email=email,
            name=name,
            address=address,
            payment_method=payment_method_id,
            invoice_settings={"default_payment_method": payment_method_id},
            metadata=metadata,
        )
    )


@jaseci_action()
def get_customer(customer_id: str):
    """retrieve customer information"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Customer.retrieve(id=customer_id)
    )


@jaseci_action()
def attach_payment_method(payment_method_id: str, customer_id: str):
    """attach payment method to customer"""

    paymentMethods = get_payment_methods(customer_id)

    paymentMethod = (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .PaymentMethod.attach(payment_method=payment_method_id, customer=customer_id)
    )

    is_default = True
    if paymentMethods.get("data"):
        update_default_payment_method(customer_id, payment_method_id)
        is_default = False

    paymentMethod.is_default = is_default

    return paymentMethod


@jaseci_action()
def delete_payment_method(payment_method_id: str):
    """detach payment method from customer"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .PaymentMethod.detach(payment_method=payment_method_id)
    )


@jaseci_action()
def get_payment_methods(customer_id: str):
    """get customer list of payment methods"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .PaymentMethod.list(
            customer=customer_id,
            type="card",
        )
    )


@jaseci_action()
def update_default_payment_method(customer_id: str, payment_method_id: str):
    """update default payment method of customer"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Customer.modify(
            customer=customer_id,
            invoice_settings={"default_payment_method": payment_method_id},
        )
    )


@jaseci_action()
def create_invoice(customer_id: str, metadata: dict = {}):
    """create customer invoice"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Invoice.create(customer=customer_id, metadata=metadata)
    )


@jaseci_action()
def get_invoice_list(
    customer_id: str,
    subscription_id: str,
    starting_after: str = "",
    limit: int = 10,
):
    """retrieve customer list of invoices"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Invoice.list(
            customer=customer_id,
            limit=limit,
            subscription=subscription_id,
            **{"starting_after": starting_after} if starting_after else {}
        )
    )


@jaseci_action()
def get_payment_intents(customer_id: str, starting_after: str = "", limit: int = 10):
    """get customer payment intents"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .PaymentIntent.list(
            customer=customer_id,
            limit=limit,
            **{"starting_after": starting_after} if starting_after else {}
        )
    )


@jaseci_action()
def create_payment_intents(
    customer_id: str,
    amount: int,
    currency: str,
    payment_method_types: str = "card",
    metadata: dict = {},
):
    """Create customer payment"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .PaymentIntent.create(
            customer=customer_id,
            amount=amount,
            currency=currency,
            payment_method_types=[payment_method_types],
            metadata=metadata,
        )
    )


@jaseci_action()
def get_customer_subscription(customer_id: str):
    """retrieve customer subcription list"""

    subscription = (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Subscription.list(customer=customer_id)
    )

    if not subscription.data:
        return {"status": "inactive", "message": "Customer has no subscription"}

    return subscription


@jaseci_action()
def create_payment_method(card_type: str, card: dict, metadata: dict = {}):
    """create payment method"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .PaymentMethod.create(type=card_type, card=card, metadata=metadata)
    )


@jaseci_action()
def create_trial_subscription(
    payment_method_id: str,
    customer_id: str,
    items: list,
    trial_period_days: int = 14,
    expand: list = [],
    metadata: dict = {},
):
    """create customer trial subscription"""

    # attach payment method to customer
    attach_payment_method(payment_method_id, customer_id)

    # set card to default payment method
    update_default_payment_method(customer_id, payment_method_id)

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Subscription.create(
            customer=customer_id,
            items=items,
            trial_period_days=trial_period_days,
            expand=expand,
            metadata=metadata,
        )
    )


@jaseci_action()
def create_subscription(
    payment_method_id: str,
    items: list,
    customer_id: str,
    metadata: dict = {},
):
    """create customer subscription"""

    # attach payment method to customer
    attach_payment_method(payment_method_id, customer_id)

    # set card to default payment method
    update_default_payment_method(customer_id, payment_method_id)

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Subscription.create(customer=customer_id, items=items, metadata=metadata)
    )


@jaseci_action()
def cancel_subscription(subscription_id: str, metadata: dict = {}):
    """cancel customer subscription"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Subscription.delete(sid=subscription_id)
    )


@jaseci_action()
def get_subscription(subscription_id: str):
    """retrieve customer subcription details"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Subscription.retrieve(id=subscription_id)
    )


@jaseci_action()
def update_subscription(
    subscription_id: str,
    subscription_item_id: str,
    price_id: str,
    metadata: dict = {},
):
    """update subcription details"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Subscription.modify(
            sid=subscription_id,
            cancel_at_period_end=False,
            items=[
                {
                    "id": subscription_item_id,
                    "price": price_id,
                },
            ],
            metadata=metadata,
        )
    )


@jaseci_action()
def get_invoice(invoice_id: str):
    """get invoice information"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .Invoice.retrieve(id=invoice_id)
    )


@jaseci_action()
def create_usage_report(subscription_item_id: str, quantity: int):
    """Create usage record"""

    return (
        MetaService()
        .get_service("stripe")
        .poke(STRIPE_ERR_MSG)
        .SubscriptionItem.create_usage_record(
            id=subscription_item_id,
            quantity=quantity,
            timestamp=datetime.now(),
        )
    )
