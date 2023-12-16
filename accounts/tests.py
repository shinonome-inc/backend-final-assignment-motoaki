from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

User = get_user_model()


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, valid_data)
        login_redirect_url = settings.LOGIN_REDIRECT_URL
        # 1の確認 = **tweets/homeにリダイレクトすること**
        self.assertRedirects(
            response,
            reverse(login_redirect_url),
            status_code=302,
            target_status_code=200,
        )
        # 2の確認 = **ユーザーが作成されること**
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        # 3の確認 = **ログイン状態になること**
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_username(self):
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email=invalid_data["email"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["email"])

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(password=invalid_data["password1"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password1"])

    def test_failure_post_with_duplicated_user(self):
        User.objects.create_user(username="testuser", email="test@teest.com", password="testpassword")
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"], email=invalid_data["email"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])

    def test_failure_post_with_invalid_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "testtest",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email=invalid_data["email"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])

    def test_failure_post_with_too_short_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "test",
            "password2": "test",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは短すぎます。最低 8 文字以上必要です。", form.errors["password2"])

    def test_failure_post_with_password_similar_to_username(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testuser",
            "password2": "testuser",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])

    def test_failure_post_with_only_numbers_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "18273645",
            "password2": "18273645",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは数字しか使われていません。", form.errors["password2"])

    def test_failure_post_with_mismatch_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword1",
            "password2": "testpassword2",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertFalse(form.is_valid())
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])


class TestLoginView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:login")
        User.objects.create_user(username="testuser", password="testpass")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "password": "testpass",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        nouser_data = {
            "username": "testuser1",
            "password": "testpassword",
        }
        response = self.client.post(self.url, nouser_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertIn("正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。", form.errors["__all__"])

    def test_failure_post_with_empty_password(self):
        emptypass_data = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(self.url, emptypass_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertIn("このフィールドは必須です。", form.errors["password"])


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:logout")
        User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

    def test_success_post(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL), status_code=302, target_status_code=200)
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="Test tweet")

    def test_success_get(self):
        url = reverse("accounts:user_profile", kwargs={"username": self.user.username})
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        user_tweets_in_context = response.context["tweets"]
        user_tweets_in_database = Tweet.objects.filter(user=self.user)
        self.assertQuerysetEqual(user_tweets_in_context, user_tweets_in_database)


# class TestUserProfileEditView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestFollowView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_user(self):

#     def test_failure_post_with_self(self):


# class TestUnfollowView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestFollowingListView(TestCase):
#     def test_success_get(self):


# class TestFollowerListView(TestCase):
#     def test_success_get(self):
