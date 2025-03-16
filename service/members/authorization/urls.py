from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.urls import path


# JWT 발급
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # 로그인 (액세스/리프레시 토큰 발급)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 액세스 토큰 갱신
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # 토큰 검증
]