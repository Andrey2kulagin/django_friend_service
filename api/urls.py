from .views import UserViewSet

from django.urls import path, include

urlpatterns = [
    path('user/list', UserViewSet.as_view({'get': 'list'})),
    path('user/detail/<int:pk>', UserViewSet.as_view({'get': 'retrieve'})),
    path('user/create', UserViewSet.as_view({'post': 'create'})),
    path('user/update/<int:pk>', UserViewSet.as_view({'patch': 'update'})),
]
