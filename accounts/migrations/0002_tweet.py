# Generated by Django 4.1.10 on 2023-12-14 16:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tweet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.CharField(max_length=280)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
