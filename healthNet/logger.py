from django.contrib.auth.models import User
from django.db import models

from .models import Hospital


class SystemLog(models.Model):
    time = models.DateTimeField(auto_now_add=True, editable=False)
    operator = models.ForeignKey(User, editable=False)
    action = models.CharField(max_length=100, editable=False)
    hospital = models.ForeignKey(Hospital, null=True)

    def __str__(self):
        return "{} - {} - {}, {} - {}".format(self.time.date(), self.time.time(), self.operator.last_name,
                                              self.operator.first_name, self.action)
