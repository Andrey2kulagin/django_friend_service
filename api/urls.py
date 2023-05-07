from .views import UserViewSet, FriendshipStatus
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    # FRIEND
    path('user/create/', UserViewSet.as_view({'post': 'create'}), name="user_create"),
    path('user/list/', UserViewSet.as_view({'get': 'list'}), name="user_list"),
    path('user/detail/<str:username>', UserViewSet.as_view({'get': 'retrieve'}), name="user_detail"),
    path('user/delete/<str:username>', UserViewSet.as_view({'delete': 'destroy'}), name="user_delete"),
    path('user/update/<str:username>', UserViewSet.as_view({'patch': 'update'}), name="user_update"),
    path('user/is_friend/<str:username>', FriendshipStatus.as_view(), name="is_friend"),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
