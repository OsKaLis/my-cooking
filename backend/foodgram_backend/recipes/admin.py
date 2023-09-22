from django.contrib import admin
from recipes.models import (
    Tags,
    Ingredients,
    Recipes,
)


class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )


admin.site.register(Tags, TagsAdmin)
admin.site.register(Ingredients)
admin.site.register(Recipes)
