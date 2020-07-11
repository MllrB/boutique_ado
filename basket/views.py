from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product


def view_basket(request):
    """ A view to return the shopping basket page """

    return render(request, 'basket/basket.html')


def add_to_basket(request, item_id):
    """ A view to add products to a shopping basket """

    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    size = None

    if 'product_size' in request.POST:
        size = request.POST['product_size']

    bag = request.session.get('basket', {})

    if size:
        if item_id in list(bag.keys()):
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
                messages.success(request, f'Changed quantity of {product.name} in size {size.upper()} to {bag[item_id]["items_by_size"][size]}')
            else:
                bag[item_id]['items_by_size'][size] = quantity
                messages.success(request, f'Added {quantity} x {product.name} in size {size.upper()} to your basket')
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}
            messages.success(request, f'Added {quantity} x {product.name} in size {size.upper()} to your basket')
    else:
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
            messages.success(request, f'Changed quantity of {product.name} to {bag[item_id]}')
        else:
            bag[item_id] = quantity
            messages.success(request, f'Added {product.name} to your basket')

    request.session['basket'] = bag
    return redirect(redirect_url)


def update_basket(request, item_id):
    """ A view to update product quantities in the shopping basket """

    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    size = None

    if 'product_size' in request.POST:
        size = request.POST['product_size']

    bag = request.session.get('basket', {})

    if size:
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'Changed quantity of {product.name} to {bag[item_id]["items_by_size"][size]}')
        else:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your basket')
    else:
        if quantity > 0:
            bag[item_id] = quantity
            messages.success(request, f'Changed quantity of {product.name} to {bag[item_id]}')
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your basket')

    request.session['basket'] = bag
    return redirect(reverse('view_basket'))

def remove_item_from_basket(request, item_id):
    """ A view to update product quantities in the shopping basket """

    size = None
    try:
        product = get_object_or_404(Product, pk=item_id)
        if 'product_size' in request.POST:
            size = request.POST['product_size']

        bag = request.session.get('basket', {})

        if size:
            messages.success(request, f'Removed {product.name} in size {size.upper()} from your basket')
            del bag[item_id]['items_by_size'][size]            
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your basket')

        request.session['basket'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, "Something went wrong, could not remove that product from your basket")
        return HttpResponse(status=500)
