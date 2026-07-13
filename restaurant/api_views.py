from rest_framework import viewsets, permissions

from .models import Menu, Booking
from .serializers import MenuSerializer, BookingSerializer


class IsStaffOrReadOnly(permissions.BasePermission):
    """Anyone can read the menu; only staff/admin can create, update or delete items."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class MenuViewSet(viewsets.ModelViewSet):
    """
    /api/menu-items/        GET (public), POST (staff)
    /api/menu-items/{id}/   GET (public), PUT/PATCH/DELETE (staff)
    """
    queryset = Menu.objects.all().order_by('id')
    serializer_class = MenuSerializer
    permission_classes = [IsStaffOrReadOnly]


class BookingViewSet(viewsets.ModelViewSet):
    """
    /api/bookings/           GET (own bookings, or all for staff), POST (create for self)
    /api/bookings/{id}/      GET/PUT/PATCH/DELETE (owner or staff)
    Requires a valid auth token (see /api/token/login/).
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
