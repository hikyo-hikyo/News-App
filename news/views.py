
from django.views.generic import (
    ListView, UpdateView, DetailView, CreateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from .models import Article, Newsletter, Publisher, User
from .forms import CustomUserCreationForm, ArticleForm, NewsletterForm
from .serializers import ArticleSerializer, NewsletterSerializer
from .permissions import IsJournalist, IsEditor, IsEditorOrJournalist
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView
from .models import Publisher

#  REGISTER


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
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
class NewsletterListView(ListView):
    model = Newsletter
    template_name = 'news/newsletter_list.html'
    context_object_name = 'newsletters'
    ordering = ['-created_at']


class NewsletterDetailView(DetailView):
    model = Newsletter
    template_name = 'news/newsletter_detail.html'
    context_object_name = 'newsletter'


class ApproveArticleView(LoginRequiredMixin, EditorRequiredMixin, UpdateView):
    model = Article
    fields = ['approved']
    template_name = 'news/approve_article.html'
    success_url = reverse_lazy('editor-article-list')

    def form_valid(self, form):
        form.instance.approved = True
        response = super().form_valid(form)
        return response


class EditorArticleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Article
    template_name = 'news/editor_article_list.html'
    context_object_name = 'articles'
    ordering = ['-created_at']

    def test_func(self):
        return self.request.user.groups.filter(name__in=['Editor', 'Journalist']).exists()

    def get_queryset(self):
        # Show ALL articles (including unapproved)
        return Article.objects.all()


class EditorNewsletterListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Newsletter
    template_name = 'news/editor_newsletter_list.html'
    context_object_name = 'newsletters'
    ordering = ['-created_at']

    def test_func(self):
        return self.request.user.groups.filter(name__in=['Editor', 'Journalist']).exists()


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


class ArticleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'news/article_form.html'
    success_url = reverse_lazy('editor-article-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Journalist').exists()

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.approved = False
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'news/article_update.html'
    success_url = reverse_lazy('editor-article-list')

    def test_func(self):
        article = self.get_object()
        return (
            self.request.user.groups.filter(name='Editor').exists() or
            article.author == self.request.user
        )

    def form_valid(self, form):
        return super().form_valid(form)


class NewsletterCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'news/newsletter_form.html'
    success_url = reverse_lazy('editor-newsletter-list')

    def test_func(self):
        return self.request.user.groups.filter(name='Journalist').exists()

    def form_valid(self, form):
        newsletter = form.save(commit=False)
        newsletter.author = self.request.user
        newsletter.save()
        form.save_m2m()
        return super().form_valid(form)


class NewsletterUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'news/newsletter_update.html'
    success_url = reverse_lazy('editor-newsletter-list')

    def test_func(self):
        newsletter = self.get_object()
        return (
            self.request.user.groups.filter(name='Editor').exists() or
            newsletter.author == self.request.user
        )

    def form_valid(self, form):
        newsletter = form.save(commit=False)
        newsletter.author = self.get_object().author
        newsletter.save()
        form.save_m2m()
        return super().form_valid(form)


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'news/article_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        article = self.get_object()
        return (
            self.request.user.groups.filter(name='Editor').exists() or
            article.author == self.request.user
        )


class NewsletterDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'news/article_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        article = self.get_object()
        return (
            self.request.user.groups.filter(name='Editor').exists() or
            article.author == self.request.user
        )


# REST API
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
        serializer.save(author=self.request.user)


class NewsletterViewSet(viewsets.ModelViewSet):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsEditorOrJournalist()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PublisherListView(ListView):
    model = Publisher
    template_name = 'news/publisher_list.html'
    context_object_name = 'publishers'
    ordering = ['name']


class PublisherCreateView(LoginRequiredMixin, EditorRequiredMixin, CreateView):
    model = Publisher
    fields = ['name', 'description']
    template_name = 'news/publisher_form.html'
    success_url = reverse_lazy('publisher-list')

    def form_valid(self, form):
        messages.success(self.request, "Publisher created successfully!")
        return super().form_valid(form)


@login_required
def subscribe_publisher(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    request.user.subscriptions_publishers.add(publisher)
    messages.success(request, f"Subscribed to {publisher.name}")
    return redirect('publisher-list')


@login_required
def unsubscribe_publisher(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    request.user.subscriptions_publishers.remove(publisher)
    messages.success(request, f"Unsubscribed from {publisher.name}")
    return redirect('publisher-list')


@login_required
def subscribe_journalist(request, pk):
    journalist = get_object_or_404(User, pk=pk, groups__name='Journalist')
    request.user.subscriptions_journalists.add(journalist)
    messages.success(
        request, f"Subscribed to journalist: {journalist.username}")
    return redirect('home')  # or a journalist profile page


@login_required
def unsubscribe_journalist(request, pk):
    journalist = get_object_or_404(User, pk=pk, groups__name='Journalist')
    request.user.subscriptions_journalists.remove(journalist)
    messages.success(request, f"Unsubscribed from {journalist.username}")
    return redirect('home')
