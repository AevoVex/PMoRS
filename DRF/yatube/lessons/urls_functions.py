from django.urls import path
from . import function_views as views

urlpatterns = [
    path('api/v1/api-token-auth/', views.api_token_auth, name='api-token-auth'),
    path('api/v1/posts/', views.api_posts, name='post-list'),
    path('api/v1/posts/<int:pk>/', views.api_posts_detail, name='post-detail'),
    path('api/v1/groups/', views.api_groups, name='group-list'),
]
