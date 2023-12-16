from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from tweets.models import Tweet

from .forms import SignupForm

User = get_user_model()


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get(self, request, username):
        user = User.objects.get(username=username)
        tweets = Tweet.objects.filter(user=user).order_by("-created_at")
        return render(
            request,
            self.template_name,
            {"user": user, "tweets": tweets},
        )
