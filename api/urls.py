from .views import UserViewSet, FriendshipStatus, IncomingApplicationsList, OutcomingApplicationsList, SendApplication,\
    DeleteApplication, ApplicationDecision, FriendsList, DeleteFriendship
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
    # APPLICATIONS
    path('applications/incoming_list/', IncomingApplicationsList.as_view(), name="incoming_list"),
    path('applications/outcoming_list/', OutcomingApplicationsList.as_view(), name="outcoming_list"),
    path('applications/send_application/', SendApplication.as_view(), name="send_application"),
    path('applications/decision/', ApplicationDecision.as_view(), name="decision"),
    path('applications/delete/<str:user_to_username>', DeleteApplication.as_view(), name="delete_application"),
    # FRIENDS
    path('friends/list', FriendsList.as_view(), name="friends_list"),
    path('friends/delete/<str:username>', DeleteFriendship.as_view(), name="friends_delete"),
    # AUTH
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

]
