from django.urls import path,include
from tools.views import (ToolListView, submit_tool, signup_view, privacy_policy, 
                        terms_of_Service, cookie_policy, verify_email, 
                        resend_verification_email)
from django.contrib import admin
app_name = 'tools'
from tools import views
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from tools.forms import EnhancedLoginForm

urlpatterns = [
    path('', ToolListView.as_view(), name='list'),
    path('submit/', views.submit_tool, name='submit'),
    path('sitemap.xml', views.sitemap, name="sitemap"),
    path('robots.txt', views.robots, name="robots"),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        authentication_form=EnhancedLoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', signup_view, name='signup'),
    path('verify-email/<str:uidb64>/<str:token>/', verify_email, name='verify-email'),
    path('resend-verification/', resend_verification_email, name='resend-verification'),
    path('', include('tools.urls', namespace='tools')),
    path('aboutus/', views.aboutus, name="aboutus"),
    path('privacy_policy/', privacy_policy, name='privacy_policy'),
    path('terms_of_service/', terms_of_Service, name='terms_of_service'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
    path('9f4a2c1e8b7d6f3a2e1b4c9d0f6a7b8c.txt/', views.indexnow, name="indexnow"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


