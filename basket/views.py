from django.shortcuts import render, redirect, reverse, HttpResponse


def view_basket(request):
    """ A view to return the shopping basket page """

    return render(request, 'basket/basket.html')


def add_to_basket(request, item_id):
    """ A view to add products to a shopping basket """

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
            else:
                bag[item_id]['items_by_size'][size] = quantity
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}
    else:
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity

    request.session['basket'] = bag
    return redirect(redirect_url)


def update_basket(request, item_id):
    """ A view to update product quantities in the shopping basket """

    quantity = int(request.POST.get('quantity'))
    size = None

    if 'product_size' in request.POST:
        size = request.POST['product_size']

    bag = request.session.get('basket', {})

    if size:
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
        else:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
    else:
        if quantity > 0:
            bag[item_id] = quantity
        else:
            bag.pop(item_id)

    request.session['basket'] = bag
    return redirect(reverse('view_basket'))

def remove_item_from_basket(request, item_id):
    """ A view to update product quantities in the shopping basket """

    size = None
    try:  
        if 'product_size' in request.POST:
            size = request.POST['product_size']

        bag = request.session.get('basket', {})

        if size:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
        else:
            bag.pop(item_id)

        request.session['basket'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        return HttpResponse(status=500)
