from django.contrib import admin
from .models import Menu, Booking


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'inventory')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'reservation_date', 'reservation_slot')
    list_filter = ('reservation_date',)
