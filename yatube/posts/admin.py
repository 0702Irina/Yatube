from django.contrib import admin
from posts.models import Post, Group


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'image',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    verbose_name = 'Посты'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'description',
    )
    search_fields = ('text',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
