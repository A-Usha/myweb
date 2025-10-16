from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('view-cart/', views.view_cart, name='view_cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-history/', views.order_history, name='order_history'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
   path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    path('upi-payment/', views.upi_payment, name='upi_payment'),

   
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
   
    path('cart/increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
path('cart/decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),


    path('my-orders/', views.order_history, name='my_orders'),
    path('order-success/', views.order_success, name='order_success'),

    path('thank-you/', views.thank_you, name='thank_you'),
]
