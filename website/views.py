from django.shortcuts import render
from .models import Watch
from django.shortcuts import redirect

# Create your views here.
def index(request):
    # get the 6 latest watches
    watches = Watch.objects.all().order_by('-id')[:6]
    return render(request, 'website/index.html', {'watches': watches})

def add_view(request):
    if request.method == 'POST':
        image = request.FILES['image']
        name = request.POST['name']
        price = request.POST['price']
        year = request.POST['year']

        watch = Watch.objects.create(name=name, price=price, year=year, image=image)

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
        name = request.POST['name']
        if name:
            watch.name = name
        price = request.POST['price']
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
        return render(request, 'website/checkout.html')
    
def inventory_view(request):
    watches = Watch.objects.all()
    return render(request, 'website/inventory.html', {'watches': watches})