"""
URL configuration for delta project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from website.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("add/", add_view, name="add"),
    path("edit/<int:watch_id>/", edit_view, name="edit"),
    path("inventory/", inventory_view, name="inventory"),
    path("watch/<int:watch_id>/", watch_view, name="watch"),
    path("checkout/", checkout_view, name="checkout"),
    path("contact/<str:form_name>/", contact_view, name="contact"),
    path("add_to_cart/<int:watch_id>/", add_to_cart, name="add_to_cart"),
    path("remove_from_cart/<int:watch_id>/", remove_from_cart, name="remove_from_cart"),
    path("add_or_remove_from_cart/<int:watch_id>/<str:action>/", add_or_remove_from_cart, name="add_or_remove_from_cart"),
    path("delete_image/<int:image_id>/", delete_image, name="delete_image"),
    path("delete_watch/<int:watch_id>/", delete_watch, name="delete_watch"),
    path("privacy/", privacy, name="privacy"),
    path("logout/", logout_view, name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
