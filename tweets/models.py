from django.conf import settings
from django.db import models


class Tweet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Like(models.Model):
    likeuser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    likedtweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="likedtweet")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["likeuser", "likedtweet"], name="unique_like")]
