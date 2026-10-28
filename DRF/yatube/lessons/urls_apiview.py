from django.urls import path
from .function_views import api_token_auth
from .views import APIPost

urlpatterns = [
    path('api/v1/api-token-auth/', api_token_auth),
    path('api/v1/posts/', APIPost.as_view()),
]
