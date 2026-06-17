from django.views.generic import ListView, UpdateView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Q
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

# Import all models
from .models import Article, Newsletter   # ← Newsletter added here

from .serializers import ArticleSerializer
from .permissions import IsJournalist, IsEditor
from .forms import ArticleForm, NewsletterForm

# REGISTER


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
# WEBHOOK


@api_view(['POST'])
def approved_webhook(request):
    print("EXTERNAL WEBHOOK RECEIVED:")
    print(request.data)
    return Response({"status": "success"}, status=200)


# MIXINS
class EditorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Editor').exists()


# FRONTEND VIEWS
class ApproveArticleView(LoginRequiredMixin, EditorRequiredMixin, UpdateView):
    model = Article
    fields = ['approved']
    template_name = 'news/approve_article.html'
    success_url = '/'


class ArticleListView(ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    ordering = ['-created_at']

    def get_queryset(self):
        return Article.objects.filter(approved=True)


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'news/article_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.approved = False
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class NewsletterCreateView(LoginRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'news/newsletter_form.html'
    success_url = reverse_lazy('home')


# REST API
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsJournalist()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsEditor() | IsJournalist()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def subscribed(self, request):
        user = request.user
        qs = Article.objects.filter(approved=True)

        if user.groups.filter(name='Reader').exists():
            qs = qs.filter(
                Q(publisher__in=user.subscriptions_publishers.all()) |
                Q(author__in=user.subscriptions_journalists.all())
            )

        serializer = ArticleSerializer(qs, many=True)
        return Response(serializer.data)
