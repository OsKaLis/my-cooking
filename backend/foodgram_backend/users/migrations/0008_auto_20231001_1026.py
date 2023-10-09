# Generated by Django 3.2.3 on 2023-10-01 07:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_users_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptions',
            name='id_subscriber',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriber', to=settings.AUTH_USER_MODEL, verbose_name='Кто подписался'),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='id_writer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer', to=settings.AUTH_USER_MODEL, verbose_name='На кого подписан'),
        ),
        migrations.AddConstraint(
            model_name='subscriptions',
            constraint=models.UniqueConstraint(fields=('id_subscriber', 'id_writer'), name='unique_id_subscriber_id_writer'),
        ),
    ]