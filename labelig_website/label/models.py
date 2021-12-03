from django.db import models
from django.contrib.auth.models import User

LABEL_CHOICES = (("spam", "Spam"), ("ham", "Ham"))


class SMS(models.Model):
    text = models.TextField(max_length=1000, unique=True)
    label = models.CharField(max_length=25, choices=LABEL_CHOICES, default="spam")

    def __str__(self):
        return self.text[:50]


class OCR(models.Model):
    name = models.TextField(max_length=50)
    accuracy = models.FloatField()
    is_added = models.BooleanField()

    def __str__(self):
        return self.name
