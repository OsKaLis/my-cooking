# flake8: noqa
from django.contrib import admin
from users.models import Users, Subscriptions


class UsersPanel(admin.ModelAdmin):
    list_display = (
        'pk',
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
    )
    list_editable = ('password',)
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'


class SubscriptionsPanel(admin.ModelAdmin):
    list_display = (
        'pk',
        'id_subscriber',
        'id_writer',
    )
    list_editable = ('id_subscriber',)
    list_filter = ('id_subscriber', 'id_writer')
    empty_value_display = '-пусто-'


admin.site.register(Users, UsersPanel)
admin.site.register(Subscriptions, SubscriptionsPanel)
