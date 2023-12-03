from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from tweets.models import Tweet


class HomeView(ListView, LoginRequiredMixin):
    template_name = "tweets/home.html"
    model = Tweet
    context_object_name = "tweets"
    queryset = Tweet.objects.select_related("user")


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


class TweetDeleteView(UserPassesTestMixin, DeleteView):
    model = Tweet
    template_name = "tweets/tweet_delete.html"
    success_url = reverse_lazy("tweets:home")
    context_object_name = "tweets"

    def test_func(self):
        tweet = self.get_object()
        return tweet.user == self.request.user
