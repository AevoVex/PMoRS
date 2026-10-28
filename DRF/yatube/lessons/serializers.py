from rest_framework import serializers
from posts.models import Post


class InitialPostSerializer(serializers.ModelSerializer):
    """Page 29: only text, author, pub_date; no id."""
    class Meta:
        model = Post
        fields = ('text', 'author', 'pub_date')
