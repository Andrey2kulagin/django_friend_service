from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserApplication(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_from_applications")
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_to_applications")
    choices = (("Отправлена", "Отправлена"),
               ("Принята", "Принята"),
               ("Отклонена", "Отклонена"))
    status = models.CharField(max_length=50, choices=choices)
