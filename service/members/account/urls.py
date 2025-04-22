from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (SignupAPIView,
                    LoginAPIView,
                    LogoutAPIView,
                    UserProfileUpdateAPIView,
                    ChangePasswordAPIView,
                    DeleteAccountAPIView,
                    )

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='atoken_refresh'),

    path('profile/', UserProfileUpdateAPIView.as_view(), name='profile-update'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('delete-account/', DeleteAccountAPIView.as_view(), name='delete-account'),
]