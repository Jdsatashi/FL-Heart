from .requests import authenticate


auth_route = authenticate

# Api routes
from .api import bookings

booking = bookings
from .api import confirm_booking

confirm_route = confirm_booking
