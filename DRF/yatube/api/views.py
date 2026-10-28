from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from posts.models import Group, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer, FollowSerializer, GroupSerializer, PostSerializer,
)


class AuthorContentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    lookup_value_regex = r'\d+'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostViewSet(AuthorContentViewSet):
    queryset = Post.objects.select_related('author', 'group').all()
    serializer_class = PostSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('$text',)
    pagination_class = LimitOffsetPagination


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.order_by('pk')
    serializer_class = GroupSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    lookup_value_regex = r'\d+'


class CommentViewSet(AuthorContentViewSet):
    serializer_class = CommentSerializer
    pagination_class = None

    @cached_property
    def parent_post(self):
        return get_object_or_404(Post, pk=self.kwargs['post_id'])

    def get_post(self):
        return self.parent_post

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        # Check the parent for POST as well as GET, before body validation.
        self.get_post()

    def get_queryset(self):
        return self.get_post().comments.select_related('author').all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_post())


class FollowViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.follower.select_related('following').order_by('pk')

    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
