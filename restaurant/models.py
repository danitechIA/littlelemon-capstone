from django.conf import settings
from django.db import models


class Menu(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    menu_item_description = models.TextField(max_length=1000, default='')
    inventory = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bookings', null=True, blank=True,
    )
    first_name = models.CharField(max_length=200)
    reservation_date = models.DateField()
    reservation_slot = models.TimeField(default='19:00:00')

    class Meta:
        # A given time slot on a given date can only be booked once (criteria 7, 9)
        unique_together = ('reservation_date', 'reservation_slot')
        ordering = ['reservation_date', 'reservation_slot']

    def __str__(self):
        return f"{self.first_name} - {self.reservation_date} {self.reservation_slot}"
