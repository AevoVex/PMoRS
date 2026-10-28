"""Alternative views for pages 56 and 65, using the same persisted posts."""
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from posts.models import Post
from .permissions import IsAuthorOrReadOnly
from .drf1_serializers import PostSerializer


class APIPost(APIView):
    def get(self, request):
        queryset = Post.objects.select_related('author', 'group').all()
        return Response(PostSerializer(queryset, many=True, context={'request': request}).data)

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author', 'group').all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
