from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView

from tweets.models import Tweet

from .forms import SignupForm
from .models import FriendShip

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user
        follow_query = FriendShip.objects.filter(followee=self.user, follower=self.request.user)
        context["is_following"] = follow_query.exists()
        context["followings_count"] = FriendShip.objects.filter(follower=self.user).count()
        context["followers_count"] = FriendShip.objects.filter(followee=self.user).count()
        return context


class FollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        followee_name = self.kwargs["username"]
        followee = get_object_or_404(User, username=followee_name)

        if request.user == followee:
            return HttpResponseBadRequest("自分自身のユーザーをフォローすることはできません。")
        elif FriendShip.objects.filter(follower=self.request.user, followee=followee).exists():
            return HttpResponseBadRequest("既にフォローしています。")
        else:
            FriendShip.objects.get_or_create(follower=request.user, followee=followee)
            return redirect("accounts:user_profile", username=followee_name)


class UnFollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        followee_name = self.kwargs["username"]
        followee = get_object_or_404(User, username=followee_name)

        if followee == request.user:
            return HttpResponseBadRequest("自分自身をアンフォローすることはできません")

        else:
            FriendShip.objects.filter(follower=request.user, followee=followee).delete()

        return redirect("accounts:user_profile", username=followee_name)
