from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Article, Newsletter, User, Publisher
from django.contrib.auth.models import Group
# USER REGISTRATION


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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            # Assign the correct group
            role = self.cleaned_data.get('role')
            if role:
                group, _ = Group.objects.get_or_create(name=role)
                user.groups.add(group)

        return user


# ARTICLE FORMS
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        # Make sure publisher is included
        fields = ['title', 'content', 'publisher']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This ensures all publishers appear in the dropdown
        self.fields['publisher'].queryset = Publisher.objects.all()
        # Allow independent articles (no publisher)
        self.fields['publisher'].required = False

        # Optional: Make it look nicer
        self.fields['publisher'].empty_label = "No Publisher (Independent Article)"


class ArticleApprovalForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['approved']
        labels = {
            'approved': 'Approve this article for publishing'
        }


# NEWSLETTER FORMS
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


# SUBSCRIPTION FORMS
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
