from ..models import *

def cart_processor(request):
    cart = request.session.get('cart', [])
    watches_in_cart = Watch.objects.filter(id__in=cart)
    total = sum([watch.price for watch in watches_in_cart])
    return {'cart': watches_in_cart, 'total': total}