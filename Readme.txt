Little Lemon - Capstone project
================================

API paths for peer review (use with Insomnia / any REST client)
------------------------------------------------------------------

Registration & authentication (Djoser):
  POST /api/users/                 -> register a new user
                                       body: username, email, password
  POST /api/token/login/           -> obtain an auth token
                                       body: username, password
                                       response: { "auth_token": "..." }
  POST /api/token/logout/          -> invalidate the current token
                                       header: Authorization: Token <token>

Menu API (public read, staff-only write):
  GET    /api/menu-items/          -> list all menu items (no auth needed)
  POST   /api/menu-items/          -> create a menu item (staff token required)
  GET    /api/menu-items/{id}/     -> retrieve one item
  PUT    /api/menu-items/{id}/     -> update an item (staff token required)
  PATCH  /api/menu-items/{id}/     -> partial update (staff token required)
  DELETE /api/menu-items/{id}/     -> delete an item (staff token required)

Table booking API (auth required for all operations):
  GET    /api/bookings/            -> list your own bookings (all bookings if staff)
  POST   /api/bookings/            -> create a booking
                                       body: first_name, reservation_date (YYYY-MM-DD),
                                             reservation_slot (HH:MM:SS)
                                       -> rejects a duplicate date+slot with 400
  GET    /api/bookings/{id}/       -> retrieve one booking (owner or staff only)
  PUT    /api/bookings/{id}/       -> update a booking
  PATCH  /api/bookings/{id}/       -> partial update
  DELETE /api/bookings/{id}/       -> delete a booking

All /api/menu-items/ and /api/bookings/ requests (except the public GET on
menu-items) need this header once you have a token:
  Authorization: Token <auth_token>

Sample credentials (created locally, see README.md for how to make your own):
  staff user:  admin / AdminPass123!
  regular user created via POST /api/users/ during testing.

Web pages (Django serving static HTML)
------------------------------------------------------------------
  /               home
  /about/         about
  /menu/          menu, rendered from the Menu model
  /book/          public booking form (session-based, no login needed)
  /reservations/  list of reservations, filterable by date

Setup
------------------------------------------------------------------
See README.md for full pipenv / MySQL setup instructions and how to run
the unit tests (python manage.py test restaurant).
