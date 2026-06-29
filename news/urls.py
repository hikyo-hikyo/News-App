from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    # Frontend Views
    ArticleListView, ArticleDetailView, ArticleCreateView,
    NewsletterListView, NewsletterDetailView, NewsletterCreateView,
    ApproveArticleView,
    EditorArticleListView, EditorNewsletterListView,
    ArticleUpdateView, NewsletterUpdateView,
    ArticleDeleteView, NewsletterDeleteView,
    PublisherCreateView, subscribe_journalist,
    subscribe_publisher, unsubscribe_publisher, unsubscribe_journalist,

    # Subscription Views
    PublisherListView, JournalistListView,
    PublisherSubscriptionView, JournalistSubscriptionView,

    # Other
    register_view, approved_webhook,

    # API ViewSets
    ArticleViewSet, NewsletterViewSet,
)

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'newsletters', NewsletterViewSet, basename='newsletter')

urlpatterns = [
    # Home & Main Pages
    path('', ArticleListView.as_view(), name='home'),
    path('newsletters/', NewsletterListView.as_view(), name='newsletter_list'),
    path('newsletters/<int:pk>/', NewsletterDetailView.as_view(),
         name='newsletter_detail'),

    # Editor Management
    path('editor/articles/', EditorArticleListView.as_view(),
         name='editor-article-list'),
    path('editor/newsletters/', EditorNewsletterListView.as_view(),
         name='editor-newsletter-list'),

    # Article CRUD
    path('article/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('article/create/', ArticleCreateView.as_view(), name='article-create'),
    path('article/<int:pk>/update/',
         ArticleUpdateView.as_view(), name='article-update'),
    path('article/<int:pk>/delete/',
         ArticleDeleteView.as_view(), name='article-delete'),

    # Newsletter CRUD
    path('newsletter/create/', NewsletterCreateView.as_view(),
         name='newsletter-create'),
    path('newsletter/<int:pk>/update/',
         NewsletterUpdateView.as_view(), name='newsletter-update'),
    path('newsletter/<int:pk>/delete/',
         NewsletterDeleteView.as_view(), name='newsletter-delete'),

    # Approve Article
    path('approve/<int:pk>/', ApproveArticleView.as_view(), name='approve-article'),

    # Publisher Management
    path('publishers/', PublisherListView.as_view(), name='publisher-list'),
    path('publishers/create/', PublisherCreateView.as_view(),
         name='publisher-create'),

    # Subscription Pages
    path('journalists/', JournalistListView.as_view(), name='journalist-list'),

    # Subscription Actions
    path('subscribe/publisher/<int:pk>/',
         subscribe_publisher, name='subscribe-publisher'),
    path('unsubscribe/publisher/<int:pk>/',
         unsubscribe_publisher, name='unsubscribe-publisher'),
    path('subscribe/journalist/<int:pk>/',
         subscribe_journalist, name='subscribe-journalist'),
    path('unsubscribe/journalist/<int:pk>/',
         unsubscribe_journalist, name='unsubscribe-journalist'),

    # Auth
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', register_view, name='register'),

    # API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/approved/', approved_webhook, name='approved-webhook'),
]
