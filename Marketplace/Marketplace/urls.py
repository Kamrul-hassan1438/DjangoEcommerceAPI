from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('Core.urls', namespace='Core')),

    path('api/admin/', include('Admin.urls', namespace='Admin')),
    path('api/seller/', include('Seller.urls', namespace='Seller')),
    path('api/customer/', include('Customer.urls', namespace='Customer')),
]

