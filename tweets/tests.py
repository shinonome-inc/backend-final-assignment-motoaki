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
        Tweet.objects.create(content="Test Tweet 1", user=self.user)
        Tweet.objects.create(content="Test Tweet 2", user=self.user)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        tweets_in_context = response.context["tweets"]
        tweets_in_db = Tweet.objects.all()
        self.assertEqual(len(tweets_in_context), len(tweets_in_db))
        self.assertTemplateUsed(response, "tweets/home.html")
        self.assertQuerysetEqual(response.context["tweets"], tweets_in_db)


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
        initial_tweet_count = Tweet.objects.count()
        response = self.client.post("/tweets/create/", {"content": "A test tweet"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tweet.objects.count(), initial_tweet_count + 1)
        self.assertRedirects(response, reverse("tweets:home"))
        self.assertTrue(Tweet.objects.filter(user=self.user, content="A test tweet").exists())
        new_tweet = Tweet.objects.latest("created_at")
        self.assertEqual(new_tweet.content, "A test tweet")

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
        form = response.context["form"]
        self.assertIn("この値は 280 文字以下でなければなりません( 281 文字になっています)。", form.errors["content"])


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.client.force_login(self.user)
        self.tweet = Tweet.objects.create(content="test", user=self.user)

    def test_success_get(self):
        response = self.client.get(f"/tweets/{self.tweet.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/tweet_detail.html")
        tweets_in_context = response.context["tweet"]
        self.assertEqual(tweets_in_context, self.tweet)


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
        self.assertEqual(response.url, reverse("tweets:home"))

    def test_failure_post_with_not_exist_tweet(self):
        self.client.force_login(self.user)
        self.tweet.delete()
        response = self.client.post("/tweets/9999/delete/")
        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Tweet.objects.filter(pk=self.tweet.id).exists())

    def test_failure_post_with_incorrect_user(self):
        self.client.force_login(self.other_user)
        response = self.client.post(f"/tweets/{self.tweet.id}/delete/")
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(Tweet.objects.filter(pk=self.tweet.id).exists())
        self.assertEqual(Tweet.objects.get(pk=self.tweet.id).user, self.user)


# class TestLikeView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_liked_tweet(self):


# class TestUnLikeView(TestCase):

#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unliked_tweet(self):
