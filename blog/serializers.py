from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'content', 'author']

class CommentSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'content', 'user', 'created_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['content', 'user', 'post']

