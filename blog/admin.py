from django.contrib import admin
# from .models import Post
from .models import *
from django_jalali.admin.filters import JDateFieldListFilter
from django.contrib.auth.admin import UserAdmin
from mptt.admin import MPTTModelAdmin

# Register your models here.

admin.sites.AdminSite.site_header = "پنل مدیریت جنگو"
admin.sites.AdminSite.site_title = "پنل"
admin.sites.AdminSite.index_title = "پنل مدیریت"


# Inlines

# class ImageInline(admin.StackedInline):
#     # model = Image
#     extra = 1


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0


# admin.site.register(Post)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'publish', 'created', 'updated', 'status', 'id']
    ordering = ['title',]
    list_filter = ['status', 'author', ('publish', JDateFieldListFilter)]
    search_fields = ['title']
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    prepopulated_fields = {'slug': ['title']}
    list_editable = ['status']
    inlines = [
        # ImageInline,
        CommentInline,
    ]
    # list_display_links = ['author']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'phone']


# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ["post", "name", "created", "active"]
#     list_filter = ["active", ('created'), ("updated")]
#     search_fields = ["name", "body"]
#     list_editable = ["active"]


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('date_of_birth', 'bio', 'photo', 'job')}),
    )

# @admin.register(Image)
# class ImageAdmin(admin.ModelAdmin):
#     list_display = ["post", "title", "created"]


admin.site.register(Contact)

admin.site.register(Comment, MPTTModelAdmin)
