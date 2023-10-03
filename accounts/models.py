# from django.contrib.auth.models import AbstractUser
# from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

from mysite import settings


# class User(AbstractUser):
class User(AbstractUser):
    email = models.EmailField()


class FriendShip(models.Model):
    followee = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="friendships_as_followee", on_delete=models.CASCADE
    )
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="friendships_as_follower", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "followee"], name="unique_follow_user"),
        ]
