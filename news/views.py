# news/views.py
from django.views.generic import ListView, UpdateView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.db.models import Q

from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from .models import Article, Newsletter, Publisher, User
from .forms import CustomUserCreationForm, ArticleForm, NewsletterForm
from .serializers import ArticleSerializer, NewsletterSerializer
from .permissions import IsJournalist, IsEditor, IsEditorOrJournalist


# REGISTER VIEW
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # You can add group assignment logic here if needed
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
    success_url = reverse_lazy('home')


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

    def get_queryset(self):
        return Article.objects.filter(approved=True)


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


# REST API VIEWS
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'subscribed']:
            return [permissions.IsAuthenticated()]
        if self.action == 'create':
            return [IsJournalist()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsEditorOrJournalist()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Article.objects.filter(approved=True)
        user = self.request.user

        if self.action == 'subscribed' and user.is_authenticated:
            subscribed_publishers = user.subscriptions_publishers.all()
            subscribed_journalists = user.subscriptions_journalists.all()

            queryset = queryset.filter(
                Q(publisher__in=subscribed_publishers) |
                Q(author__in=subscribed_journalists)
            )
        return queryset

    @action(detail=False, methods=['get'], url_path='subscribed')
    def subscribed(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Automatically set the author to the logged-in journalist"""
        serializer.save(author=self.request.user)


class NewsletterViewSet(viewsets.ModelViewSet):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        # Create, Update, Delete only for Journalists & Editors
        return [IsEditorOrJournalist()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
