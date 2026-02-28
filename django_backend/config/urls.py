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
from core.views import (
    admin_create_user,
    admin_me,
    auth_me,
    health,
    login_view,
    organizer_company,
    organizer_event_detail,
    organizer_event_images,
    organizer_events,
    public_events,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health', health),
    path('api/events', public_events),
    path('api/auth/login', login_view),
    path('api/auth/me', auth_me),
    path('api/admin/me', admin_me),
    path('api/admin/users', admin_create_user),
    path('api/organizer/company', organizer_company),
    path('api/organizer/events', organizer_events),
    path('api/organizer/events/<int:event_id>', organizer_event_detail),
    path('api/organizer/events/<int:event_id>/images', organizer_event_images),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
