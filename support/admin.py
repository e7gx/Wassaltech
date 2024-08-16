from django.contrib import admin

from support.models import Comment, Ticket

# Register your models here.

admin.site.register(Ticket)
admin.site.register(Comment)