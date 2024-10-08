# Generated by Django 5.0.6 on 2024-06-12 15:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("selfchatgpt", "0005_qnareply_post_alter_qnapost_author_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="qnareply",
            name="post",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reply",
                to="selfchatgpt.qnapost",
            ),
        ),
    ]
