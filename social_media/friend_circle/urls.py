from django.urls import path, include
from rest_framework import routers
from .views import UserViewset,UserSearchAPIView,FriendRequestAPIView,ListFriendsView,ListPendingFriendRequestsView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = routers.DefaultRouter()
router.register(r'users', UserViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('user/search/', UserSearchAPIView.as_view(), name='user-search'),
    path('friend/requests/', FriendRequestAPIView.as_view(), name='friend-request-list'),
    path('friend/list/', ListFriendsView.as_view(), name='friend-list'),
    path('friend/list/pending/',ListPendingFriendRequestsView.as_view(), name = 'pending-friend-list')

]

