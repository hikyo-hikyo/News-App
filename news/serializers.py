
from rest_framework import serializers
from .models import Article, Newsletter, Publisher, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField for create/update (accepts ID)
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    # Optional: nested representation for GET requests
    author_detail = UserSerializer(source='author', read_only=True)

    publisher = serializers.PrimaryKeyRelatedField(
        read_only=True)  # or full serializer

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'author', 'author_detail',
            'publisher', 'created_at', 'approved'
        ]


class NewsletterSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    articles = ArticleSerializer(many=True, read_only=True)

    class Meta:
        model = Newsletter
        fields = '__all__'
