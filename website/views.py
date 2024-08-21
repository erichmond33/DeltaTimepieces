from django.shortcuts import render
from .models import *
from django.shortcuts import redirect
from datetime import datetime

# Create your views here.
def index(request):
    # get the 6 latest watches
    watches = Watch.objects.all().order_by('-id')[:6]
    return render(request, 'website/index.html', {'watches': watches})

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
        
        watch.save()

        return render(request, 'website/edit.html', {'watch': watch})
    elif request.method == 'GET':
        watch = Watch.objects.get(id=watch_id)
        print(watch.name)
        return render(request, 'website/edit.html', {'watch': watch})

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