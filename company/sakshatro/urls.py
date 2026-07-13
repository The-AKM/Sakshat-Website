from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.log_in, name="login"),
    path("signup", views.signup, name="signup"),
    path("logout", views.log_out, name="logout"),
    path("profile",views.profile, name="profile"),
    path("<int:product_id>", views.buy, name="buy"),
    path("order_history", views.Order_History, name="Order_History"),
    path("cart", views.cart, name="cart"),
    path("add_to_cart/<int:product_id>", views.add_to_cart, name="add_to_cart"),
    path("rmv_from_cart/<int:product_id>", views.rmv_from_cart, name="rmv_from_cart"),
    path("products/", views.products, name="products"),
    path("payment/", views.payment_view, name="payment"),
    path("payment-verify/", views.payment_verify, name="payment_verify"),
    path("success/", views.success_view, name="success"),
    path("failure/", views.failure_view, name="failure")
    
]