from ..models import *

def cart_processor(request):
    cart = request.session.get('cart', [])
    watches_in_cart = Watch.objects.filter(id__in=cart)
    total = str(sum([watch.price for watch in watches_in_cart])) + " + shipping"
    return {'cart': watches_in_cart, 'total': total}