from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True, verbose_name="Nombre")
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True, verbose_name='Biografia')

    avatar = models.ImageField(null=True, default="avatar.svg")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def followings(self):
        user_ids = Relationship.objects.filter(from_user=self.pk)\
            .values_list('to_user_id', flat=True)
        return User.objects.filter(id__in=user_ids)
    
    def followers(self):
        user_ids = Relationship.objects.filter(to_user=self.pk)\
            .values_list('from_user_id', flat=True)
        return User.objects.filter(id__in=user_ids)
    


class Topic(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    
    class Meta:
        verbose_name = 'Tema'
        verbose_name_plural = 'Temas'

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Usuario')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, verbose_name='Tema')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(null=True, blank=True, verbose_name='Descripcion')
    participants = models.ManyToManyField(User, related_name='participants', blank=True, verbose_name='Participantes')
    updated = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Creado')

    class Meta:
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='Sala')
    body = models.TextField(verbose_name='Cuerpo del mensaje')
    updated = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Creado')

    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]

class Relationship(models.Model):
    from_user = models.ForeignKey(User, related_name='relationships', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='related_to', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Relación'
        verbose_name_plural = 'Relaciónes'
    
    def __str__(self):
        return f'{self.from_user.username} --- sigue a --- {self.to_user.username}'