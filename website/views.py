from django.shortcuts import render
from .models import *
from django.shortcuts import redirect
from datetime import datetime
from django.core.mail import send_mail
from dotenv import load_dotenv
import os
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    # get the 6 latest watches
    newest_watches = Watch.objects.all().order_by('-id')[:3]
    our_picks = Watch.objects.filter(our_pick=True)
    timeless = Watch.objects.filter(timeless=True)
    rare_and_iconic = Watch.objects.filter(rare_and_iconic=True)
    return render(request, 'website/index.html', {'newest_watches': newest_watches, 'our_picks': our_picks, 'timeless': timeless, 'rare_and_iconic': rare_and_iconic})

@login_required
def add_view(request):
    if request.method == 'POST':
        image = request.FILES['image']
        name = request.POST['name']
        price = request.POST['price'].replace(',', '')
        year = request.POST['year']
        condition = request.POST['condition']
        contents = request.POST['contents']
        details = request.POST['details']

        our_picks = request.POST.get('our_picks', False)
        our_pick = True if our_picks != False else False
        timeless = request.POST.get('timeless', False)
        timeless = True if timeless != False else False
        rare_and_iconic = request.POST.get('rare_and_iconic', False)
        rare_and_iconic = True if rare_and_iconic != False else False

        watch = Watch.objects.create(name=name, price=price, year=year, image=image, condition=condition, contents=contents, details=details, our_pick=our_pick, timeless=timeless, rare_and_iconic=rare_and_iconic)
        
        try: 
            images = request.FILES.getlist('images')
            for image in images:
                WatchSecondaryImage.objects.create(watch=watch, image=image)
        except:
            pass

        return redirect('edit', watch.id)
    elif request.method == 'GET':
        allow_our_picks = True if len(Watch.objects.filter(our_pick=True)) < 3 else False
        allow_timeless = True if len(Watch.objects.filter(timeless=True)) < 3 else False
        allow_rare_and_iconic = True if len(Watch.objects.filter(rare_and_iconic=True)) < 3 else False

        return render(request, 'website/add.html', {'allow_our_picks': allow_our_picks, 'allow_timeless': allow_timeless, 'allow_rare_and_iconic': allow_rare_and_iconic})

@login_required
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
        condition = request.POST['condition']
        if condition:
            watch.condition = condition
        contents = request.POST['contents']
        if contents:
            watch.contents = contents
        details = request.POST['details']
        if details:
            watch.details = details

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
    
def contact_view(request, form_name):
    if request.method == 'POST':

        name = request.POST['name']
        phone = request.POST['phone']
        email = request.POST['email']
        message = request.POST['message']

        header=""
        if form_name == "find_watch":
            header = f"{name} replied to the \"Don't see what you are looking for?\" form."
            short_header = "Find a watch form"
        elif form_name == "general":
            header = f"{name} replied to the \"General Inquiry\" form."
            short_header = "General Inquiry form"

        load_dotenv('./website/keys.env')

        try:
            send_mail(
                f'New message from {name} ({short_header})',
                f'{header}\n\n--\n\n{message}\n\nPhone number: {phone}\nEmail: {email}',
                os.getenv('EMAIL_HOST_USER'),
                [os.getenv('EMAIL_HOST_RECEIVER')],
                fail_silently=False
            )
            status_message_for_user = "Message sent successfully! We will get back to you as soon as possible."
            messages.success(request, status_message_for_user)
        except Exception as e:
            status_message_for_user = f"Message failed to send. We aren't sure what went wrong. We are very sorry. Please give us a call instead (870) 351-9816"
            messages.error(request, status_message_for_user)

        return redirect('index')
    elif request.method == 'GET':
        return render(request, 'website/contact.html')
    
def add_to_cart(request, watch_id):
    cart = request.session.get('cart', [])
    if watch_id not in cart:
        cart.append(watch_id)
        request.session['cart'] = cart

    referer = request.META.get('HTTP_REFERER')
    if '#' in referer:
        base_url, _ = referer.split('#', 1)
        redirect_url = f"{base_url}#watch-{watch_id}"
    else:
        redirect_url = f"{referer}#watch-{watch_id}"
    
    return redirect(redirect_url)

def remove_from_cart(request, watch_id):
    cart = request.session.get('cart', [])
    if watch_id in cart:
        cart.remove(watch_id)
        request.session['cart'] = cart

    redirect_url = request.META.get('HTTP_REFERER')
    return redirect(redirect_url)
    
def inventory_view(request):
    watches = Watch.objects.all().order_by('-timestamp')
    sort_by_tags = ['Newest', 'Oldest', 'Price, low to high', 'Price, high to low', 'Year, old to new', 'Year, new to old']
    sort_by_tag = 'Newest'


    sort_by = request.GET.get('sort_by')
    if sort_by == 'Oldest':
        watches = watches.order_by('timestamp')
        sort_by_tag = "Oldest"
    elif sort_by == 'Price, low to high':
        watches = watches.order_by('price')
        sort_by_tag = "Price, low to high"
    elif sort_by == 'Price, high to low':
        watches = watches.order_by('-price')
        sort_by_tag = "Price, high to low"
    elif sort_by == 'Year, old to new':
        watches = watches.order_by('year')
        sort_by_tag = "Year, old to new"
    elif sort_by == 'Year, new to old':
        watches = watches.order_by('-year')
        sort_by_tag = "Year, new to old"

    scroll = True if request.GET.get('sort_by') else False

    return render(request, 'website/inventory.html', {'watches': watches, 'sort_by_tag': sort_by_tag, 'sort_by_tags': sort_by_tags, 'scroll': scroll})

def watch_view(request, watch_id):
    watch = Watch.objects.get(id=watch_id)
    images = [watch.image] + [image.image for image in watch.secondary_images.all()]
    return render(request, 'website/watch.html', {'watch': watch, 'images': images})

@login_required
def delete_image(request, image_id):
    if request.method == 'POST':
        image = WatchSecondaryImage.objects.get(id=image_id)
        watch_id = image.watch.id
        image.delete()
        return redirect('edit', watch_id)

@login_required
def delete_watch(request, watch_id):
    if request.method == 'POST':
        watch = Watch.objects.get(id=watch_id)
        watch.delete()
        return redirect('inventory')
    
def privacy(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('privacy')
    elif request.method == "GET":
        return render(request, "website/privacy.html")
    
def logout_view(request):
    logout(request)
    return redirect('index')