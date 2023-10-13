# Generated by Django 3.2.3 on 2023-10-13 07:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_subscriptions_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptions',
            name='id_subscriber',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions_subscriber', to=settings.AUTH_USER_MODEL, verbose_name='Кто подписался'),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='id_writer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions_writer', to=settings.AUTH_USER_MODEL, verbose_name='На кого подписан'),
        ),
    ]