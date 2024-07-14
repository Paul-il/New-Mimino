from django.db import models

class UserData(models.Model):
    user_id = models.CharField(max_length=100)
    data = models.TextField()

    def __str__(self):
        return self.user_id
