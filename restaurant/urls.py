from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('menu/', views.menu, name='menu'),
    path('book/', views.book, name='book'),
    path('reservations/', views.reservations, name='reservations'),
    path('bookings', views.bookings, name='bookings'),
]
