from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.all()[:6]
    return render(request, 'shop/home.html', {
        'categories': categories,
        'products': featured_products
    })

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'shop/category_products.html', {
        'category': category,
        'products': products
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'shop/signup.html', {'form': form})


@login_required
def add_to_cart(request, pk):
    cart = request.session.get('cart', [])
    if pk not in cart:
        cart.append(pk)
    request.session['cart'] = cart
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart = request.session.get('cart', [])
    products = Product.objects.filter(pk__in=cart)
    total = sum(p.price for p in products)
    return render(request, 'shop/cart.html', {'products': products, 'total': total})

@login_required
def place_order(request):
    cart = request.session.get('cart', [])
    if cart:
        order = Order.objects.create(user=request.user)
        order.products.set(cart)
        order.save()
        request.session['cart'] = []  # Clear cart after order
        return redirect('order_history')
    return redirect('home')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})
