import base64
import datetime as dt
import webcolors
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Achievement, Cat, CHOICES


class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name', max_length=64)

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class AchievementWriteSerializer(AchievementSerializer):
    """Direct dictionary CRUD must reject duplicate names; nested writes reuse them."""
    def validate_achievement_name(self, value):
        query = Achievement.objects.filter(name=value)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError('Такое достижение уже существует.')
        return value


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                header, encoded = data.split(';base64,', 1)
                extension = header.split('/', 1)[1]
                data = ContentFile(
                    base64.b64decode(encoded), name=f'temp.{extension}'
                )
            except (ValueError, IndexError, TypeError):
                raise serializers.ValidationError('Некорректное изображение в формате base64.')
        return super().to_internal_value(data)


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
    color = serializers.ChoiceField(choices=CHOICES)
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    age = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['color'] = webcolors.name_to_hex(instance.color.lower())
        except ValueError:
            pass
        return data

    def to_internal_value(self, data):
        data = data.copy()
        color = data.get('color')
        if isinstance(color, str) and color.startswith('#'):
            if color != color.upper():
                raise serializers.ValidationError({'color': 'Unsupported color.'})
            try:
                data['color'] = webcolors.hex_to_name(color).capitalize()
            except ValueError:
                raise serializers.ValidationError({'color': 'Unsupported color.'})
        return super().to_internal_value(data)

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'achievements', 'owner', 'age', 'image')
        validators = [UniqueTogetherValidator(
            queryset=Cat.objects.all(), fields=('name', 'owner'),
            message='У этого хозяина уже есть котик с таким именем.',
        )]

    def get_age(self, obj):
        return dt.date.today().year - obj.birth_year

    def validate_birth_year(self, value):
        year = dt.date.today().year
        if not year - 40 < value <= year:
            raise serializers.ValidationError('Год рождения должен быть в пределах последних 40 лет.')
        return value

    def validate(self, data):
        # PATCH may supply only one of these fields.
        name = data.get('name', getattr(self.instance, 'name', None))
        color = data.get('color', getattr(self.instance, 'color', None))
        if name == color:
            raise serializers.ValidationError('Имя не может совпадать с цветом!')
        return data

    @staticmethod
    def set_achievements(cat, items):
        # Unique names and through-table constraint prevent duplicated links.
        achievements = [Achievement.objects.get_or_create(**item)[0] for item in items]
        cat.achievements.set(achievements)

    def create(self, validated_data):
        items = validated_data.pop('achievements', [])
        try:
            with transaction.atomic():
                cat = Cat.objects.create(**validated_data)
                self.set_achievements(cat, items)
                return cat
        except IntegrityError:
            # A concurrent request can pass serializer validation before INSERT.
            raise serializers.ValidationError({'name': 'Котик с таким именем уже есть у владельца.'})

    def update(self, instance, validated_data):
        items = validated_data.pop('achievements', None)
        try:
            with transaction.atomic():
                instance = super().update(instance, validated_data)
                if items is not None:
                    self.set_achievements(instance, items)
                return instance
        except IntegrityError:
            raise serializers.ValidationError({'name': 'Котик с таким именем уже есть у владельца.'})


class CatListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color')


class UserSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'cats')
