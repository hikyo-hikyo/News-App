from django import forms
from django.contrib.auth.forms import UserCreationForm
# ← All models imported here
from .models import Article, Newsletter, User, Publisher

# ====================== USER REGISTRATION ======================


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[
            ('Reader', 'Reader'),
            ('Journalist', 'Journalist'),
            ('Editor', 'Editor'),
        ],
        required=True,
        label="Register as"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            from django.contrib.auth.models import Group
            try:
                group = Group.objects.get(name=self.cleaned_data['role'])
                user.groups.add(group)
            except Group.DoesNotExist:
                pass  # Group will be created later in admin
        return user


# ====================== ARTICLE FORMS ======================
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'publisher': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.groups.filter(name='Journalist').exists():
            self.fields['publisher'].queryset = Publisher.objects.all()
        else:
            self.fields['publisher'].queryset = Publisher.objects.none()


class ArticleApprovalForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['approved']
        labels = {
            'approved': 'Approve this article for publishing'
        }


# ====================== NEWSLETTER FORMS ======================
class NewsletterForm(forms.ModelForm):
    articles = forms.ModelMultipleChoiceField(
        queryset=Article.objects.all().order_by('-created_at'),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-check-input'}),
        required=False,
        label="Select Articles"
    )

    class Meta:
        model = Newsletter
        fields = ['title', 'description', 'articles']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make checkboxes look better
        self.fields['articles'].help_text = "Hold Ctrl/Cmd to select multiple articles"


# ====================== SUBSCRIPTION FORMS ======================
class PublisherSubscriptionForm(forms.Form):
    publishers = forms.ModelMultipleChoiceField(
        queryset=Publisher.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-check-input'}),
        required=False,
        label="Subscribe to Publishers"
    )


class JournalistSubscriptionForm(forms.Form):
    journalists = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(groups__name='Journalist'),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-check-input'}),
        required=False,
        label="Subscribe to Independent Journalists"
    )
