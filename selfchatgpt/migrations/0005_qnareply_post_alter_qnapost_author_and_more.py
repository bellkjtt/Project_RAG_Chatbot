# Generated by Django 5.0.6 on 2024-06-12 14:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("selfchatgpt", "0004_profile_qnapost_qnareply"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="qnareply",
            name="post",
            field=models.OneToOneField(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reply",
                to="selfchatgpt.qnapost",
            ),
        ),
        migrations.AlterField(
            model_name="qnapost",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="qnareply",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="replies",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
