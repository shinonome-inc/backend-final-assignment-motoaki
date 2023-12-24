from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, ListView

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

    def get_context_data(self, username, **kwargs):
        user = User.objects.get(username=username)
        context = super().get_context_data(**kwargs)
        context["user"] = user
        context["tweets"] = Tweet.objects.filter(user=user).order_by("-created_at")
        follow_query = FriendShip.objects.filter(followee=user, follower=self.request.user)
        context["is_following"] = follow_query.exists()
        context["followings_count"] = FriendShip.objects.filter(follower=user).count()
        context["followers_count"] = FriendShip.objects.filter(followee=user).count()
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


class FollowingListView(ListView):
    model = FriendShip
    template_name = 'accounts/followinglist.html'
    context_object_name = 'following_list'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        following_users = FriendShip.objects.filter(follower=user).select_related('followee')
        return following_users


class FollowerListView(ListView):
    model = FriendShip
    template_name = 'accounts/followerlist.html'
    context_object_name = 'follower_list'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        follower_users = FriendShip.objects.filter(followee=user).select_related('follower')
        return follower_users
