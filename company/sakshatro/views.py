from django.shortcuts import render
from .models import User, Items, Order, Cart, Purchase
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json, hmac, hashlib


# Create your views here.
def index(request):

   

    if request.user.is_authenticated:
        Cart.objects.get_or_create(user=request.user)

    return render(request, "sakshatro/index.html")

def products(request):
    products = Items.objects.all()
    return render(request, "sakshatro/products.html",{
        "products" : products
    })

def log_in(request):

    if request.method == "POST":

        next_url = request.GET.get('next')  
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(request, username=email, password= password)
        print(email, password)
        print("AUTH RESULT:", user)

        

        if user is not None:
            login(request, user)
            if next_url:
                return HttpResponseRedirect(next_url)
            return HttpResponseRedirect(reverse("index"))
            
            
        else:
            messages.error(request, "Invalid Email or Password")
            return render(request, "sakshatro/login.html",{
                "message" : "Invalid Email or Password",
            })


    return render(request, "sakshatro/login.html")

def signup(request):

    if request.method == "POST":

        name = request.POST["name"]
        username = request.POST["username"]
        
        password = request.POST["password"]
        address = request.POST["address"]
        city = request.POST["city"]
        state = request.POST["state"]
        zip = request.POST["zip"]
        cont_number = request.POST.get("cont_number", "")


        f1 = User(
            username = username,
            name = name,
            contact_number = cont_number,
            Address = address,
            city = city,
            state = state,
            zip_code = zip
        )
        f1.set_password(password)

        
        try:
            f1.save()
            return render(request, "sakshatro/login.html",{
                "credential_msg" : "Please enter your credentials again!",
            })
        except IntegrityError:
            return render(request, 'sakshatro/signup.html', {
                "integrity": "username already taken",
            })
    


    return render(request, "sakshatro/signup.html")

def log_out(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
@login_required
def profile(request):
    user = request.user
    return render(request, "sakshatro/profile.html",{
        "user":user,
    })

@login_required(login_url='login')
def buy(request, product_id):

    

    user = request.user
    thing = Items.objects.get(pk=product_id)
    
    f1 = Order(
        user= user,
        date = timezone.now()
        
    )
    f1.save()
    

    f1.products.add(thing)
    messages.success(request, f"✅ {thing.name} has been successfully ordered!")

    
    return render(request, "sakshatro/index.html",{
        "products": Items.objects.all(),
        
    })
@login_required
def Order_History(request):
    orders = Order.objects.filter(user=request.user)

    
    
        

    return render(request, "sakshatro/history.html",{
        "orders":orders,
        "user": request.user,
        
    })
@login_required
def cart(request):
    
    user = request.user
    
    
    cart_products, _ = Cart.objects.get_or_create(user=user)

    if not cart_products.products.exists():
        return render(request, 'sakshatro/cart.html',{
            "nothing" : "No products in the cart."
        })
    
    amount=0
    for product in cart_products.products.all():
        amount = amount + product.price

    return render(request, "sakshatro/cart.html",{
        "user" : user,
        "carts" : cart_products,
        "amount":amount
    })

    

@login_required
def add_to_cart(request, product_id):
    if request.method == "POST":
        product = Items.objects.get(pk = product_id)
        quantity = request.POST["quantity"]
        user = request.user
        cart, _ = Cart.objects.get_or_create(user = user)
        cart.products.add(product, quantity)
        return HttpResponseRedirect(reverse("cart"))
    return HttpResponseRedirect(reverse("cart"))
    
@login_required
def rmv_from_cart(request, product_id):
    product = Items.objects.get(pk=product_id)
    user = request.user
    cart = Cart.objects.get(user=user)
    cart.products.remove(product)
    messages.success(request, f"✅ {product.name} has been removed from Cart!")
    return HttpResponseRedirect(reverse("cart"))




client = razorpay.Client(auth=(settings.RAZORPAY_TEST_API_KEY, settings.RAZORPAY_TEST_SECRET_KEY))

def payment_view(request):

    callback_url = request.build_absolute_uri(reverse('payment_verify'))
    amount = 50000  # Amount in paise (50000 paise = 500 INR)
    currency = "INR"
    
    # Create the order
    razorpay_order = client.order.create({
        "amount": amount,
        "currency": currency,
        "payment_capture": "1"  # Auto-capture payment
    })

    order = Purchase(
        user=request.user,
        razorpay_order_id=razorpay_order['id'],
        amount=amount / 100,
        status="created"
    )
    order.save()
    
    context = {
        "razorpay_order_id": razorpay_order['id'],
        "razorpay_merchant_key": settings.RAZORPAY_TEST_API_KEY,
        "razorpay_amount": amount,
        "currency": currency,
        "user" : request.user,
        "callback_url":callback_url,
    }
    return render(request, "sakshatro/payment.html", context)

@csrf_exempt
def payment_verify(request):
    if request.method == "POST":
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        

        # Generate signature
        generated_signature = hmac.new(
            bytes(settings.RAZORPAY_TEST_SECRET_KEY, 'utf-8'),
            bytes(f"{razorpay_order_id}|{razorpay_payment_id}", 'utf-8'),
            hashlib.sha256
        ).hexdigest()

        try:
            order = Purchase.objects.get(razorpay_order_id=razorpay_order_id)

            if generated_signature == razorpay_signature:
                # ✅ VALID PAYMENT
                order.status = "paid"
                order.payment_id = razorpay_payment_id
                order.save()
                return HttpResponseRedirect(reverse("success"))
            else:
                # ❌ INVALID SIGNATURE
                order.status = "failed"
                order.save()
                return HttpResponseRedirect(reverse("failure"))
        
        except Purchase.DoesNotExist:
            return HttpResponseRedirect(reverse("failure"))
@csrf_exempt
def success_view(request):
    return render(request, "sakshatro/success.html")

@csrf_exempt
def failure_view(request):
    return render(request, "sakshatro/failure.html")
