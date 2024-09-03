from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.template.loader import render_to_string
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
    our_picks = Watch.objects.filter(our_pick=True).order_by('date_added_to_our_pick')[:3]
    timeless = Watch.objects.filter(timeless=True).order_by('date_added_to_timeless')[:3]
    rare_and_iconic = Watch.objects.filter(rare_and_iconic=True).order_by('date_added_to_rare_and_iconic')[:3]
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

        date_added_to_our_pick = None
        date_added_to_timeless = None
        date_added_to_rare_and_iconic = None

        our_picks = request.POST.get('our_picks', False)
        if our_picks != False:
            our_picks = True
            date_added_to_our_pick = datetime.now()
        timeless = request.POST.get('timeless', False)
        if timeless != False:
            timeless = True
            date_added_to_timeless = datetime.now()
        rare_and_iconic = request.POST.get('rare_and_iconic', False)
        if rare_and_iconic != False:
            rare_and_iconic = True
            date_added_to_rare_and_iconic = datetime.now()

        watch = Watch.objects.create(name=name, price=price, year=year, image=image, condition=condition, contents=contents, details=details, our_pick=our_picks, timeless=timeless, rare_and_iconic=rare_and_iconic, date_added_to_our_pick=date_added_to_our_pick, date_added_to_timeless=date_added_to_timeless, date_added_to_rare_and_iconic=date_added_to_rare_and_iconic)
        
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
        if our_picks != False:
            watch.our_pick = True
            watch.date_added_to_our_pick = datetime.now()
        else:
            watch.our_pick = False
        
        timeless = request.POST.get('timeless', False)
        if timeless != False:
            watch.timeless = True
            watch.date_added_to_timeless = datetime.now()
        else:
            watch.timeless = False
        
        rare_and_iconic = request.POST.get('rare_and_iconic', False)
        if rare_and_iconic != False:
            watch.rare_and_iconic = True
            watch.date_added_to_rare_and_iconic = datetime.now()
        else:
            watch.rare_and_iconic = False
        
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
        return render(request, 'website/checkout.html')
    elif request.method == 'POST':
        contact = request.POST['contact']
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        address = request.POST['address']
        address2 = request.POST['address2']
        city = request.POST['city']
        state = request.POST['state']
        zip_code = request.POST['zip']
        country = "United States"

        shipping_same_as_billing = request.POST.get('sameAddress', False)
        if shipping_same_as_billing == False:
            billing_first_name = request.POST['billingFirstName']
            billing_last_name = request.POST['billingLastName']
            billing_address = request.POST['billingAddress']
            billing_address2 = request.POST['billingAddress2']
            billing_city = request.POST['billingCity']
            billing_state = request.POST['billingState']
            billing_zip_code = request.POST['billingZip']
            billing_country = "United States"

        payment_method = request.POST['paymentMethod']

        header = f"{first_name} {last_name} placed an order."
        message = f"{header}\n\n--\n\n"
        message += f"Contact: {contact}\nFirst Name: {first_name}\nLast Name: {last_name}\nAddress: {address}\nApartment: {address2}\nCity: {city}\nState: {state}\nZip Code: {zip_code}\nCountry: {country}\n\n"
        if shipping_same_as_billing == False:
            message += f"Billing First Name: {billing_first_name}\nBilling Last Name: {billing_last_name}\nBilling Address: {billing_address}\nBilling Address Apartment: {billing_address2}\nBilling City: {billing_city}\nBilling State: {billing_state}\nBilling Zip Code: {billing_zip_code}\nBilling Country: {billing_country}\n\n"
        message += f"Payment Method: {payment_method}\n\n"
        message += "Items:\n"
        cart = request.session.get('cart', [])
        watches_in_cart = Watch.objects.filter(id__in=cart)
        total = sum([watch.price for watch in watches_in_cart])
        for watch in watches_in_cart:
            # link to the watch
            message += f"{watch.name} - ${watch.price} - {request.get_host()}{watch.get_absolute_url()}\n"
        message += f"\nTotal: ${total}"
        
        load_dotenv('./website/keys.env')

        try:
            send_mail(
                f'New order from {first_name} {last_name}',
                message,
                os.getenv('EMAIL_HOST_USER'),
                [os.getenv('EMAIL_HOST_RECEIVER')],
                fail_silently=False
            )
            status_message_for_user = "Order placed successfully! We will get back to you as soon as possible."
            messages.success(request, status_message_for_user)
        except Exception as e:
            status_message_for_user = f"Order failed to send. We aren't sure what went wrong. We are very sorry. Please give us a call instead (870) 351-9816"
            messages.error(request, status_message_for_user)

        request.session['cart'] = []

        return redirect('index')
    
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
    
    return redirect(request.META.get('HTTP_REFERER'))

def remove_from_cart(request, watch_id):
    cart = request.session.get('cart', [])
    if watch_id in cart:
        cart.remove(watch_id)
        request.session['cart'] = cart

    redirect_url = request.META.get('HTTP_REFERER')
    return redirect(redirect_url)

def add_or_remove_from_cart(request, watch_id, action):
    cart = request.session.get('cart', [])
    if action == 'add':
        if watch_id not in cart:
            cart.append(watch_id)
    elif action == 'remove':
        if watch_id in cart:
            cart.remove(watch_id)
    request.session['cart'] = cart
    watches_in_cart = Watch.objects.filter(id__in=cart)
    total = sum([watch.price for watch in watches_in_cart])
    cart_length = len(watches_in_cart)
    
    context = {'request': request, 'cart': watches_in_cart, 'total': total, "watch": Watch.objects.get(id=watch_id)}

    cart_modal = render_to_string('website/cart.html', context, request=request)
    cart_accordion = render_to_string('website/cart_accordion.html', context, request=request)
    add_to_cart_button = render_to_string('website/add_to_cart_button.html', context, request=request)
    checkout_button = render_to_string('website/checkout_button.html', context, request=request)

    return JsonResponse({
        'success': True,
        'cart_modal': cart_modal,
        'cart_accordion': cart_accordion,
        'cart_length': cart_length,
        'add_to_cart_button': add_to_cart_button,
        'checkout_button': checkout_button
    })
    
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