from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Category, Review, CartItem, Profile
from .forms import RegisterForm, ProfileForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def home(request):
    return render(request, 'shop/home.html')

def shop(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    items = Item.objects.all()
    if query:
        items = items.filter(name__icontains=query)
    if category:
        items = items.filter(category__slug=category)
    if brand:
        items = items.filter(brand__icontains=brand)
    return render(request, 'shop/shop.html', {'items': items})

def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.viewed_items.add(item)
    reviews = item.reviews.all()
    return render(request, 'shop/item_detail.html', {'item': item, 'reviews': reviews})

@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    viewed = profile.viewed_items.all()
    return render(request, 'shop/dashboard.html', {'viewed': viewed})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Profile.objects.create(user=user)
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'shop/register.html', {'form': form})

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, 'shop/cart.html', {'cart_items': cart_items})

@login_required
def submit_review(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.item = item
            review.save()
    return redirect('item_detail', item_id=item.id)

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    cart = request.session.get('cart', {})

    # Increment quantity if already in cart, else add new
    if str(item.id) in cart:
        cart[str(item.id)] += 1
    else:
        cart[str(item.id)] = 1

    request.session['cart'] = cart
    return redirect('cart')

@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total_price = 0

    for item_id, quantity in cart.items():
        item = get_object_or_404(Item, id=item_id)
        item_total = item.price * quantity
        total_price += item_total
        items.append({
            'item': item,
            'quantity': quantity,
            'total': item_total,
        })

    context = {
        'cart_items': items,
        'total_price': total_price,
    }
    return render(request, 'shop/cart.html', context)

@login_required
def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})

        for item_id, quantity in request.POST.items():
            if item_id.startswith('quantity_'):
                id_str = item_id.split('_')[1]
                try:
                    qty = int(quantity)
                    if qty > 0:
                        cart[id_str] = qty
                    else:
                        cart.pop(id_str, None)
                except ValueError:
                    pass

        request.session['cart'] = cart
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    cart.pop(str(item_id), None)
    request.session['cart'] = cart
    return redirect('cart')
