from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    following = models.ManyToManyField(User, related_name="user_followers", blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class FriendShip(models.Model):
    follower = models.ForeignKey(User, related_name="friendship_following", on_delete=models.CASCADE)
    followee = models.ForeignKey(User, related_name="friendship_followers", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower.username} follows {self.followee.username}"

    class Meta:
        ordering = ["-created_at"]
