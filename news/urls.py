from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ArticleViewSet, approved_webhook,
    ArticleListView, ApproveArticleView,
    ArticleDetailView, ArticleCreateView,
    NewsletterCreateView, register_view
)

router = DefaultRouter()
router.register(r'articles', ArticleViewSet,
                basename='api-article')   # Changed basename

urlpatterns = [
    # Frontend
    path('', ArticleListView.as_view(), name='home'),
    path('article/<int:pk>/', ArticleDetailView.as_view(),
         name='frontend-article-detail'),
    path('approve/<int:pk>/', ApproveArticleView.as_view(), name='approve-article'),
    path('article/create/', ArticleCreateView.as_view(), name='article-create'),
    path('newsletter/create/', NewsletterCreateView.as_view(),
         name='newsletter-create'),

    # Authentication
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', register_view, name='register'),

    # API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/articles/subscribed/',
         ArticleViewSet.as_view({'get': 'subscribed'}), name='subscribed-articles'),
    path('api/approved/', approved_webhook, name='approved-webhook'),
]
