"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from core.openapi import openapi_schema, swagger_ui
from core.views import (
    admin_create_user,
    admin_create_nearby_place,
    admin_refund_review,
    admin_refunds,
    admin_me,
    admin_nearby_place_detail,
    admin_nearby_places,
    admin_moderation_event_review,
    admin_moderation_events,
    auth_me,
    health,
    login_view,
    organizer_company,
    organizer_event_detail,
    organizer_event_images,
    organizer_events,
    public_event_detail,
    public_event_seat_map,
    public_events,
    register_view,
    user_create_reservation,
    user_favorite_detail,
    user_favorites,
    user_bookings,
    user_payment_method_detail,
    user_payment_methods,
    user_pay_reservation,
    user_privacy,
    user_profile,
    user_request_refund,
    user_reservation_detail,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health', health),
    path('api/openapi.json', openapi_schema, name='openapi-schema'),
    path('api/docs', swagger_ui, name='swagger-ui'),
    path('api/events', public_events),
    path('api/events/<int:event_id>', public_event_detail),
    path('api/events/<int:event_id>/seat-map', public_event_seat_map),
    path('api/auth/login', login_view),
    path('api/auth/register', register_view),
    path('api/auth/me', auth_me),
    path('api/admin/me', admin_me),
    path('api/admin/users', admin_create_user),
    path('api/admin/refunds', admin_refunds),
    path('api/admin/refunds/<int:refund_id>/review', admin_refund_review),
    path('api/admin/events/moderation', admin_moderation_events),
    path('api/admin/events/<int:event_id>/review', admin_moderation_event_review),
    path('api/admin/nearby-places', admin_nearby_places),
    path('api/admin/nearby-places/create', admin_create_nearby_place),
    path('api/admin/nearby-places/<int:place_id>', admin_nearby_place_detail),
    path('api/user/profile', user_profile),
    path('api/user/bookings', user_bookings),
    path('api/user/reservations', user_create_reservation),
    path('api/user/reservations/<int:reservation_id>', user_reservation_detail),
    path('api/user/reservations/<int:reservation_id>/pay', user_pay_reservation),
    path('api/user/favorites', user_favorites),
    path('api/user/favorites/<int:event_id>', user_favorite_detail),
    path('api/user/payment-methods', user_payment_methods),
    path('api/user/payment-methods/<int:payment_method_id>', user_payment_method_detail),
    path('api/user/privacy', user_privacy),
    path('api/user/orders/<int:order_id>/refund-request', user_request_refund),
    path('api/organizer/company', organizer_company),
    path('api/organizer/events', organizer_events),
    path('api/organizer/events/<int:event_id>', organizer_event_detail),
    path('api/organizer/events/<int:event_id>/images', organizer_event_images),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
