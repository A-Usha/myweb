import qrcode
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Product, Category, Order, OrderItem


# ➕ Increase Quantity
def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        cart[product_id]['quantity'] += 1
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('view_cart')

# ➖ Decrease Quantity
def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        if cart[product_id]['quantity'] > 1:
            cart[product_id]['quantity'] -= 1
        else:
            del cart[product_id]  # Remove item if quantity becomes 0
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('view_cart')

# 🏠 Home Page
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {'products': products, 'categories': categories})


# 📂 Products by Category
def category_products(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'shop/category_products.html', {'category': category, 'products': products})


# 🔍 Search Products
def search(request):
    query = request.GET.get('q')
    results = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'shop/search_results.html', {'query': query, 'results': results})


# ➕ Add to Cart
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id]['quantity'] += 1
    else:
        cart[product_id] = {'quantity': 1}

    request.session['cart'] = cart
    messages.success(request, "Item added to cart.")
    return redirect('view_cart')


# ➖ Remove from Cart
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart.")
    else:
        messages.error(request, "Item not found in cart.")
    return redirect('view_cart')


# 🛒 View Cart
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        quantity = item['quantity']
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    context = {'cart_items': cart_items, 'total': total}
    return render(request, 'shop/cart.html', context)


# 🏦 UPI Payment Page
@login_required
def upi_payment(request):
    cart = request.session.get('cart', {})
    total = 0

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        total += product.price * item['quantity']

    if total == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    # UPI details
    upi_id = "yourupi@bank"  # Replace with your real UPI ID
    payee_name = "Your Shop Name"
    upi_uri = f"upi://pay?pa={upi_id}&pn={payee_name}&am={total}&cu=INR"

    # Generate QR code
    qr_img = qrcode.make(upi_uri)

    # Save QR code image to static folder
    qr_filename = "dynamic_qr.png"
    qr_path = os.path.join(settings.BASE_DIR, 'shop', 'static', 'shop', 'images', qr_filename)
    qr_img.save(qr_path)

    return render(request, 'shop/upi_qr.html', {
        'qr_image': f'shop/images/{qr_filename}',
        'amount': total
    })




# ✅ Place Order
@login_required
def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    total_price = 0
    order = Order.objects.create(user=request.user, total_price=0)  # Placeholder

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        quantity = item['quantity']
        subtotal = product.price * quantity
        total_price += subtotal

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

    order.total_price = total_price
    order.save()

    request.session['cart'] = {}
    messages.success(request, "Order placed successfully!")
    return redirect('order_history')


# 📖 Order History
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    for order in orders:
        order.items_list = order.items.all()  # Or order.orderitem_set.all() if no related_name
    return render(request, 'shop/order_history.html', {'orders': orders})




# 🔐 Auth Views
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})


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


def user_logout(request):
    logout(request)
    return redirect('home')


# 📦 Product Detail
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})
def order_success(request):
    return render(request, 'shop/order_success.html')
def thank_you(request):
    return render(request, 'shop/thank_you.html')
