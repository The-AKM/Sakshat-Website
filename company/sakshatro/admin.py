from django.contrib import admin
from .models import User, Items, Feature, Cart, Order, Purchase
# Register your models here.

class Useradmin(admin.ModelAdmin):
    list_display = ('username',  'password', 'city', 'state', 'zip_code')
    list_filter = ('state', 'city')
    search_fields = ('username', 'email')


admin.site.register(User, Useradmin)
admin.site.register(Items)
admin.site.register(Feature)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Purchase)