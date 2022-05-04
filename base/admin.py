from django.contrib import admin
from .models import Room, Topic, Message, User, Relationship

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'username', 'email', 'bio']
    
    
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['host', 'topic', 'name', 'description']
    
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name']
    
    
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'room']


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    pass
