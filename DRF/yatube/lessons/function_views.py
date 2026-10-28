from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from posts.models import Group, Post
from .drf1_serializers import GroupSerializer, PostSerializer


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def api_token_auth(request):
    serializer = AuthTokenSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    token, _ = Token.objects.get_or_create(user=serializer.validated_data['user'])
    return Response({'token': token.key})


@api_view(['GET', 'POST'])
def api_posts(request):
    if request.method == 'POST':
        serializer = PostSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    posts = Post.objects.select_related('author', 'group').all()
    return Response(PostSerializer(posts, many=True, context={'request': request}).data)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_posts_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author', 'group'), pk=pk)
    if request.method == 'GET':
        return Response(PostSerializer(post, context={'request': request}).data)
    if post.author_id != request.user.pk:
        raise PermissionDenied('Изменять и удалять пост может только его автор.')
    if request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = PostSerializer(
        post, data=request.data, partial=request.method == 'PATCH', context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['GET'])
def api_groups(request):
    return Response(GroupSerializer(Group.objects.order_by('pk'), many=True).data)
