import json
import time
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from products.models import Product
from profiles.models import UserProfile

from .models import Order, OrderLineItem



class StripeWH_Handler:
    """ Handles webhooks from Stripe """

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handles generic/unknown/unexpetced webhook event
        """
        return HttpResponse(
            content=f'Unhandled Webhook recevied: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handles payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.basket
        save_info = intent.metadata.save_info
        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount /100, 2)

        # clean data in shipping details
        for field, value in shipping_details.address.items():
            if value == '':
                shipping_details.address[field] = None

        #Update profile information if save_info was checked
        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = shipping_details.phone,
                profile.default_street_address1 = shipping_details.address.line1,
                profile.default_street_address2 = shipping_details.address.line2,
                profile.default_street_address3 = shipping_details.address.line3,
                profile.default_town_or_city = shipping_details.address.city,
                profile.default_county = shipping_details.address.county,
                profile.default_country = shipping_details.address.country,
                profile.default_post_code = shipping_details.address.postal_code,
                profile.save()

        order_exists = False
        attempts = 1

        while attempts <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    street_address3__iexact=shipping_details.address.line3,
                    town_or_city__iexact=shipping_details.address.city,
                    county__iexact=shipping_details.address.county,
                    country__iexact=shipping_details.address.country,
                    post_code__iexact=shipping_details.address.postal_code,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempts += 1
                time.sleep(1)

        if order_exists:
            return HttpResponse(
                content=f'Webhook recevied: {event["type"]} \
                         | SUCCESS: Verified order already exists in database',
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email__iexact=billing_details.email,
                    phone_number=shipping_details.phone,
                    street_address=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    street_address3=shipping_details.address.line3,
                    town_or_city=shipping_details.address.city,
                    county=shipping_details.address.county,
                    country=shipping_details.address.country,
                    post_code=shipping_details.address.postal_code,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = get_object_or_404(Product, pk=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook recevied: {event["type"]} | ERROR: {e}',
                    status=500)

        return HttpResponse(
            content=f'Webhook recevied: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)


    def handle_payment_intent_payment_failed(self, event):
        """
        Handles payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook recevied: {event["type"]}',
            status=200)
