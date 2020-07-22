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
            content=f'Webhook recevied: {event['type']}',
            status=200)
