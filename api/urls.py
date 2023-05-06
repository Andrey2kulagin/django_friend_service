from .views import UserViewSet

from django.urls import path, include

urlpatterns = [
    path('user/create/', UserViewSet.as_view({'post': 'create'}), name="user_create"),
    path('user/list/', UserViewSet.as_view({'get': 'list'}), name="user_list"),
    path('user/detail/<int:pk>', UserViewSet.as_view({'get': 'retrieve'}), name="user_detail"),

    path('user/update/', UserViewSet.as_view({'patch': 'update'}), name="user_update"),
]
