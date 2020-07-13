from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm


def checkout(request):
    """ A view to show the checkout """

    bag = request.session.get('basket', {})
    if not bag:
        messages.error(request, "You haven't added anything to your basket!")
        return redirect(reverse('products'))
    
    order_form = OrderForm()
    template = 'checkout/checkout.html'

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': 'clients secret key',
    }

    return render(request, template, context)