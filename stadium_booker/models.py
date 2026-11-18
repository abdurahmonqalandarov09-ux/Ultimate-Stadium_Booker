from django.db import models
from django.contrib.auth.models import AbstractUser 



class CustomUsers(AbstractUser):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=325)
    photo = models.ImageField(upload_to='images/')
    phone = models.CharField(max_length=13)
    about = models.TextField(max_length=150)


    def __str__(self):
        return self.username



class Category(models.Model):
    name = models.CharField(max_length=120)
    player_count = models.PositiveBigIntegerField()


    def __str__(self):
        return self.name



class Field(models.Model):
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=120)
    description = models.TextField(max_length=120)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='fields')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    photo = models.ImageField(upload_to='images/')
    STATUS = [
        ('available', 'Свободно'),
        ('unavailable', 'Занято')
    ]
    is_free = models.BooleanField(default='available')


    def __str__(self):
        return self.name




class Booking(models.Model):
    STATUS = [
        ('active', 'Активный'),
        ('complited', 'Завершен')
    ]

    user = models.ForeignKey(CustomUsers, related_name='bookings')
    field = models.ForeignKey(Field, related_name='bookings')
    has_team = models.BooleanField()
    players_quantity = models.PositiveBigIntegerField()
    status = models.CharField(max_length=120, choices='available, complited', default='available')
    created_at = models.DateTimeField(auto_now_add=True)



class Participant(models.Model):
    booking = models.ForeignKey(Booking, related_name='participants')
    user = models.ForeignKey(CustomUsers, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.booking