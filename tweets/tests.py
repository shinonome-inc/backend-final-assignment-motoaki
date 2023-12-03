from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Tweet


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")
        self.user = User.objects.create_user(username="tester", password="password")
        self.client.force_login(self.user)
        self.tweet = Tweet.objects.create(content="tester", user=self.user)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/home.html")
        self.assertQuerysetEqual(response.context["tweets"], Tweet.objects.all())


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.client.login(username="tester", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/tweet_create.html")

    def test_success_post(self):
        self.client.force_login(self.user)
        response = self.client.post("/tweets/create/", {"content": "A test tweet"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tweet.objects.filter(user=self.user, content="A test tweet").exists())

    def test_failure_post_with_empty_content(self):
        invalid_data = {"content": ""}
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tweet.objects.filter(content=invalid_data["content"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["content"])

    def test_failure_post_with_too_long_content(self):
        self.client.force_login(self.user)
        response = self.client.post("/tweets/create/", {"content": "A" * 281})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tweet.objects.exists())


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.client.force_login(self.user)
        self.tweet = Tweet.objects.create(content="test", user=self.user)

    def test_success_get(self):
        response = self.client.get(f"/tweets/{self.tweet.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/tweet_detail.html")


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="Test tweet")

    def test_success_post(self):
        self.client.force_login(self.user)
        print(Tweet.objects.all().count())
        response = self.client.post(f"/tweets/{self.tweet.id}/delete/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tweet.objects.filter(pk=self.tweet.id).exists())

    def test_failure_post_with_not_exist_tweet(self):
        self.client.force_login(self.user)
        response = self.client.post("/tweets/9999/delete/")
        self.assertEqual(response.status_code, 404)

    def test_failure_post_with_incorrect_user(self):
        self.client.force_login(self.other_user)
        response = self.client.post(f"/tweets/{self.tweet.id}/delete/")
        self.assertEqual(response.status_code, 403)


# class TestLikeView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_liked_tweet(self):


# class TestUnLikeView(TestCase):

#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unliked_tweet(self):
