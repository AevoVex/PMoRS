from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .function_views import api_token_auth
from .views import PostViewSet

router = DefaultRouter()
router.register('posts', PostViewSet)
urlpatterns = [
    path('api/v1/api-token-auth/', api_token_auth),
    path('api/v1/', include(router.urls)),
]
