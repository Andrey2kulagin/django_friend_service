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
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        unique_together = ('user_from', 'user_to')  # чтобы не было дубликатов


class Friendship(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends2')
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        unique_together = ('user1', 'user2')  # чтобы не было дубликатов

    def __str__(self):
        return f'{self.user1} - {self.user2}'
