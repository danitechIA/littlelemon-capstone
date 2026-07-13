from rest_framework import serializers
from .models import Menu, Booking


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'name', 'price', 'menu_item_description', 'inventory']


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Booking
        fields = ['id', 'user', 'first_name', 'reservation_date', 'reservation_slot']
        read_only_fields = ['user']

    def validate(self, attrs):
        date = attrs.get('reservation_date', getattr(self.instance, 'reservation_date', None))
        slot = attrs.get('reservation_slot', getattr(self.instance, 'reservation_slot', None))
        qs = Booking.objects.filter(reservation_date=date, reservation_slot=slot)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('That time slot is already booked for the selected date.')
        return attrs
