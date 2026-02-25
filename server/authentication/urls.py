from django.urls import path, include
from .views import *

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/reset/', include('django_rest_passwordreset.urls',  namespace='password_reset')),
    path('user/profile/', ProfileView.as_view(), name='profile'),
]