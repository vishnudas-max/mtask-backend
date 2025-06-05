from django.contrib import admin
from .models import Order

class AuthorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Order)