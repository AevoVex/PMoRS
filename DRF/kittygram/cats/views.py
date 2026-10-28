from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Achievement, Cat
from .permissions import AchievementPermission, IsOwnerOrReadOnly
from .serializers import AchievementWriteSerializer, CatListSerializer, CatSerializer, UserSerializer


class OwnerCreateMixin:
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CatViewSet(OwnerCreateMixin, viewsets.ModelViewSet):
    queryset = Cat.objects.select_related('owner').prefetch_related('achievements').all()
    serializer_class = CatSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        return CatListSerializer if self.action == 'list' else CatSerializer

    @action(detail=False, url_path='recent-white-cats')
    def recent_white_cats(self, request):
        cats = self.get_queryset().filter(color='White').order_by('-id')[:5]
        return Response(self.get_serializer(cats, many=True).data)


class CreateRetrieveViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class LightCatViewSet(OwnerCreateMixin, CreateRetrieveViewSet):
    queryset = Cat.objects.select_related('owner').prefetch_related('achievements').all()
    serializer_class = CatSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.prefetch_related('cats').order_by('pk')
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementWriteSerializer
    permission_classes = [AchievementPermission]
