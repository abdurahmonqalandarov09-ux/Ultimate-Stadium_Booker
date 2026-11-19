from django.db import models
from django.contrib.auth.models import AbstractUser 



class CustomUser(AbstractUser):
    photo = models.ImageField(upload_to='images/', null=True)
    phone = models.CharField(max_length=13, blank=True)
    about = models.TextField(max_length=150, blank=True)


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
    photo = models.ImageField(upload_to='fields/')
    STATUS = [
        ('available', 'Свободно'),
        ('unavailable', 'Занято')
    ]
    is_free = models.BooleanField(default=True)


    def __str__(self):
        return self.name




class Booking(models.Model):
    STATUS = [
            ('active', 'Активный'),
            ('completed', 'Завершён'),
            ('cancelled', 'Отменён'),
        ]

    user = models.ForeignKey(CustomUser, related_name='bookings', on_delete=models.CASCADE)
    field = models.ForeignKey(Field, related_name='bookings', on_delete=models.CASCADE)
    has_team = models.BooleanField()
    players_needed = models.PositiveBigIntegerField(null=True)
    status = models.CharField(max_length=20, choices=STATUS, default='active')
    created_at = models.DateTimeField(auto_now_add=True)



class Participant(models.Model):
    booking = models.ForeignKey(Booking, related_name='participants', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.username