from django.urls import path
from . import views

app_name = 'book'

urlpatterns = [
    path('order_generator', views.order_generator, name='order_generator'),
    path('ethusdc', views.ethusdc, name='ethusdc'),
    path('pools', views.pools, name='pools'),
    path('sender_balances', views.sender_balances, name='sender_balances'),
]