from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import CommentsViewSet, FollowViewSet, GroupViewSet, PostsViewSet

router_v1 = DefaultRouter()
router_v1.register(
    r'posts', PostsViewSet, basename='posts')
router_v1.register(
    r'posts/(?P<post_id>\d+)/comments', CommentsViewSet, basename='comments')
router_v1.register(
    r'follow', FollowViewSet, basename='follow')
router_v1.register(
    r'group', GroupViewSet, basename='group')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
