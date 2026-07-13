
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):

    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=64, null=True)
    Address= models.CharField(max_length=500, default="")
    city = models.CharField(max_length=32, default="")
    state = models.CharField(max_length=64, default="")
    zip_code = models.CharField(max_length=10,default="")
    contact_number = models.CharField( max_length=11, null=True)

    def __str__(self):
        return f"{self.name}"
    #remember that email is treated as the username in the backend
    #even if the user doesnt know at all
    #Their name is just used as User.name
    #"GOD"damn yeaeeah!



class Feature(models.Model):
    name = models.CharField(max_length=128)
    
    def __str__(self):
        return f"{self.name}"



class Items(models.Model):  
    user = models.ManyToManyField(User, related_name="person", blank=True)
    name = models.CharField(max_length=64)
    price = models.IntegerField()
    image = models.ImageField(upload_to='products/', null=True)
    features = models.ManyToManyField(Feature, related_name="points")
    

    def __str__(self):
        return f"{self.name} : {self.price}"
    

class Cart(models.Model):
    user = models.ForeignKey(User, related_name="user_cart" ,blank=True, on_delete=models.CASCADE)
    products = models.ManyToManyField(Items, related_name="cart_products", blank=True)
    quantity = models.IntegerField(null=True)

class Order(models.Model):

    STATUS_CHOICES = [
        ('P', 'Processing'),
        ('OD', 'Out for Delivery'),
        ('D', 'Delivered')
    ]

    status = models.CharField(max_length=2, default='P', choices=STATUS_CHOICES)

    user = models.ForeignKey(User, related_name="user_order", blank=True, on_delete=models.CASCADE)
    products = models.ManyToManyField(Items, related_name="order_products", blank=True)
    date = models.DateField(null=True)
    amount = models.FloatField(blank=True, null=True)




class Purchase(models.Model):
    user = models.ForeignKey(User, related_name="user_purchase", null=True, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=50)
    amount = models.IntegerField()
    status = models.CharField(max_length=20)