from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import EditorRequiredMixin
from .models import Article, serializers
from .serializers import ArticleSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response


class ApproveArticleView(LoginRequiredMixin, EditorRequiredMixin, UpdateView):
    model = Article
    fields = ['approved']
    template_name = 'approve_article.html'

    def form_valid(self, form):
        article = form.save()
        # Signal will handle the rest
        return super().form_valid(form)


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.filter(approved=True)
    serializer_class = ArticleSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsJournalist()]
        # etc.
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def subscribed(self, request):
        user = request.user
        qs = Article.objects.filter(approved=True)
        if user.groups.filter(name='Reader').exists():
            qs = qs.filter(
                models.Q(publisher__in=user.subscriptions_publishers.all()) |
                models.Q(author__in=user.subscriptions_journalists.all())
            )
        return Response(ArticleSerializer(qs, many=True).data)
