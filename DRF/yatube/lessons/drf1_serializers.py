from rest_framework import serializers
from posts.models import Group, Post


class PostSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(
        slug_field='slug', queryset=Group.objects.all(), required=False, allow_null=True,
    )
    character_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'text', 'author', 'image', 'pub_date', 'group', 'character_quantity')
        read_only_fields = ('author', 'pub_date')
        # Count the saved text exactly, including leading/trailing whitespace.
        extra_kwargs = {'text': {'trim_whitespace': False}}

    def get_character_quantity(self, obj):
        return len(obj.text)

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError('Текст не должен быть пустым.')
        return value


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')
