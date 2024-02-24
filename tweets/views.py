from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from tweets.models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):
    template_name = "tweets/home.html"
    model = Tweet
    context_object_name = "tweets"
    queryset = Tweet.objects.select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["like_list"] = Like.objects.filter(likeuser=self.request.user).values_list("likedtweet__pk", flat=True)
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    template_name = "tweets/tweet_create.html"
    model = Tweet
    success_url = reverse_lazy("tweets:home")
    fields = ["content"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    template_name = "tweets/tweet_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["like_list"] = Like.objects.filter(likeuser=self.request.user).values_list("likedtweet__pk", flat=True)
        return context


class TweetDeleteView(UserPassesTestMixin, DeleteView):
    model = Tweet
    template_name = "tweets/tweet_delete.html"
    success_url = reverse_lazy("tweets:home")

    def test_func(self):
        tweet = self.get_object()
        return tweet.user == self.request.user


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet_id = kwargs["pk"]
        tweet = get_object_or_404(Tweet, pk=self.kwargs["pk"])
        Like.objects.get_or_create(likeuser=request.user, likedtweet=tweet)
        liked = True
        unlike_url = reverse("tweets:unlike", kwargs={"pk": tweet_id})
        context = {
            "liked": liked,
            "tweet_id": tweet_id,
            "likes_count": tweet.likedtweet.count(),
            "unlike_url": unlike_url,
        }
        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet_id = kwargs["pk"]
        tweet = get_object_or_404(Tweet, pk=self.kwargs["pk"])
        Like.objects.filter(likeuser=request.user, likedtweet=tweet).delete()
        liked = False
        like_url = reverse("tweets:like", kwargs={"pk": tweet_id})
        context = {
            "liked": liked,
            "tweet_id": tweet_id,
            "likes_count": tweet.likedtweet.count(),
            "like_url": like_url,
        }
        return JsonResponse(context)
