from django.http import HttpResponse


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
        return HttpResponse(
            content=f'Webhook recevied: {event["type"]}',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handles payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook recevied: {event["type"]}',
            status=200)
