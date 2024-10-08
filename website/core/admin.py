from django.contrib import admin

from .models import BlogModel, CommentModel, ProfileOfUser, Follow

admin.site.register(BlogModel)
admin.site.register(CommentModel)
admin.site.register(ProfileOfUser)
admin.site.register(Follow)