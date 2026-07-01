# news/mixins.py
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class ReaderRequiredMixin(UserPassesTestMixin):
    """Only allow users with 'Reader' role"""

    def test_func(self):
        return self.request.user.groups.filter(name='Reader').exists()

    def handle_no_permission(self):
        messages.warning(
            self.request, "This page is only available to Readers.")
        return redirect('home')
