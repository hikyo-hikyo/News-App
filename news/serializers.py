from rest_framework import serializers
from .models import Article, Newsletter, Publisher, User


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
