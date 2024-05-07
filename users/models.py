from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    position = models.SmallIntegerField(default=0, choices=((0,'bugalter'),(1,'omborchi')))

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.position}'

class ReportCode(models.Model):
    password = models.CharField(max_length=10)
    class Meta:
        verbose_name = "Parol"
