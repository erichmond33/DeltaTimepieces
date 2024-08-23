from django.shortcuts import render
from .models import *
from django.shortcuts import redirect
from datetime import datetime

# Create your views here.
def index(request):
    # get the 6 latest watches
    newest_watches = Watch.objects.all().order_by('-id')[:3]
    our_picks = Watch.objects.filter(our_pick=True)
    timeless = Watch.objects.filter(timeless=True)
    rare_and_iconic = Watch.objects.filter(rare_and_iconic=True)
    return render(request, 'website/index.html', {'newest_watches': newest_watches, 'our_picks': our_picks, 'timeless': timeless, 'rare_and_iconic': rare_and_iconic})

def add_view(request):
    if request.method == 'POST':
        image = request.FILES['image']
        name = request.POST['name']
        price = request.POST['price'].replace(',', '')
        year = request.POST['year']

        watch = Watch.objects.create(name=name, price=price, year=year, image=image)
        
        try: 
            images = request.FILES.getlist('images')
            for image in images:
                WatchSecondaryImage.objects.create(watch=watch, image=image)
        except:
            pass

        return redirect('edit', watch.id)
    elif request.method == 'GET':
        return render(request, 'website/add.html')

def edit_view(request, watch_id):
    if request.method == 'POST':
        watch = Watch.objects.get(id=watch_id)

        try:
            image = request.FILES['image']
            if image:
                watch.image = image
        except:
            pass

        try: 
            images = request.FILES.getlist('images')
            for image in images:
                WatchSecondaryImage.objects.create(watch=watch, image=image)
        except:
            pass
        name = request.POST['name']
        if name:
            watch.name = name
        price = request.POST['price'].replace(',', '')
        if price:
            watch.price = price
        year = request.POST['year']
        if year:
            watch.year = year

        our_picks = request.POST.get('our_picks', False)
        watch.our_pick = True if our_picks != False else False
        
        timeless = request.POST.get('timeless', False)
        watch.timeless = True if timeless != False else False
        
        rare_and_iconic = request.POST.get('rare_and_iconic', False)
        watch.rare_and_iconic = True if rare_and_iconic != False else False
        
        watch.save()

        return redirect('edit', watch_id)
    elif request.method == 'GET':
        watch = Watch.objects.get(id=watch_id)
        
        our_picks = Watch.objects.filter(our_pick=True)
        allow_our_picks = True if len(our_picks) < 3 else watch.our_pick
        timeless = Watch.objects.filter(timeless=True)
        allow_timeless = True if len(timeless) < 3 else watch.timeless
        rare_and_iconic = Watch.objects.filter(rare_and_iconic=True)
        allow_rare_and_iconic = True if len(rare_and_iconic) < 3 else watch.rare_and_iconic

        if watch.our_pick:
            print('our pick')

        return render(request, 'website/edit.html', {'watch': watch, 'allow_our_picks': allow_our_picks, 'allow_timeless': allow_timeless, 'allow_rare_and_iconic': allow_rare_and_iconic})

def checkout_view(request):
    if request.method == 'GET':
        cart = request.session.get('cart', [])
        watches_in_cart = Watch.objects.filter(id__in=cart)
        total = sum([watch.price for watch in watches_in_cart])

        return render(request, 'website/checkout.html', {'cart': watches_in_cart, 'total': total})
    
def add_to_cart(request, watch_id):
        cart = request.session.get('cart', [])
        if watch_id not in cart:
            cart.append(watch_id)
            request.session['cart'] = cart

        return redirect('checkout')

def remove_from_cart(request, watch_id):
    cart = request.session.get('cart', [])
    if watch_id in cart:
        cart.remove(watch_id)
        request.session['cart'] = cart

    return redirect('checkout')
    
def inventory_view(request):
    watches = Watch.objects.all()
    return render(request, 'website/inventory.html', {'watches': watches})

def watch_view(request, watch_id):
    watch = Watch.objects.get(id=watch_id)
    images = [watch.image] + [image.image for image in watch.secondary_images.all()]
    return render(request, 'website/watch.html', {'watch': watch, 'images': images})

def delete_image(request, image_id):
    if request.method == 'POST':
        image = WatchSecondaryImage.objects.get(id=image_id)
        watch_id = image.watch.id
        image.delete()
        return redirect('edit', watch_id)

def delete_watch(request, watch_id):
    if request.method == 'POST':
        watch = Watch.objects.get(id=watch_id)
        watch.delete()
        return redirect('inventory')