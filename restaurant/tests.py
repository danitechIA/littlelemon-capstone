from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Menu, Booking


class StaticPagesTests(APITestCase):
    """Django serving static HTML content."""

    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_menu_page_loads(self):
        response = self.client.get('/menu/')
        self.assertEqual(response.status_code, 200)

    def test_book_page_loads(self):
        response = self.client.get('/book/')
        self.assertEqual(response.status_code, 200)

    def test_reservations_page_loads(self):
        response = self.client.get('/reservations/')
        self.assertEqual(response.status_code, 200)


class RegistrationAndAuthTests(APITestCase):
    """User registration and authentication (Djoser)."""

    def test_user_can_register(self):
        response = self.client.post('/api/users/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registered_user_can_get_token(self):
        User.objects.create_user(username='loginuser', password='StrongPass123!')
        response = self.client.post('/api/token/login/', {
            'username': 'loginuser',
            'password': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('auth_token', response.data)


class MenuAPITests(APITestCase):
    """Menu API: public read, staff-only write."""

    def setUp(self):
        self.staff = User.objects.create_user(username='staff', password='pass12345', is_staff=True)
        self.customer = User.objects.create_user(username='customer', password='pass12345')
        self.menu_item = Menu.objects.create(
            name='Greek salad', price=12.00,
            menu_item_description='Fresh vegetables, feta, olives.', inventory=50,
        )

    def test_anyone_can_list_menu_items(self):
        response = self.client.get('/api/menu-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_create_menu_item(self):
        response = self.client.post('/api/menu-items/', {
            'name': 'Bruschetta', 'price': '7.00',
            'menu_item_description': 'x', 'inventory': 10,
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create_menu_item(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/menu-items/', {
            'name': 'Bruschetta', 'price': '7.00',
            'menu_item_description': 'x', 'inventory': 10,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_menu_item(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post('/api/menu-items/', {
            'name': 'Bruschetta', 'price': '7.00',
            'menu_item_description': 'x', 'inventory': 10,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BookingAPITests(APITestCase):
    """Table booking API: authenticated, no duplicate date+slot."""

    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='pass12345')
        self.user2 = User.objects.create_user(username='bob', password='pass12345')

    def test_anonymous_cannot_list_bookings(self):
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_booking(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/bookings/', {
            'first_name': 'Alice',
            'reservation_date': '2026-08-01',
            'reservation_slot': '19:00:00',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(Booking.objects.first().user, self.user1)

    def test_duplicate_slot_is_rejected(self):
        Booking.objects.create(
            user=self.user1, first_name='Alice',
            reservation_date='2026-08-01', reservation_slot='19:00:00',
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/api/bookings/', {
            'first_name': 'Bob',
            'reservation_date': '2026-08-01',
            'reservation_slot': '19:00:00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_only_sees_own_bookings(self):
        Booking.objects.create(
            user=self.user1, first_name='Alice',
            reservation_date='2026-08-01', reservation_slot='19:00:00',
        )
        Booking.objects.create(
            user=self.user2, first_name='Bob',
            reservation_date='2026-08-01', reservation_slot='20:00:00',
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['first_name'], 'Alice')
