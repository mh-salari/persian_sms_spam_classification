from django import forms
from django.forms import widgets
from .models import SMS

LABEL_CHOICES = (("spam", "Spam"), ("ham", "Ham"))


class AddSMSForm(forms.ModelForm):
    class Meta:
        model = SMS
        fields = ("text", "label")
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-control sms-text"}),
            "label": forms.Select(
                attrs={"class": "form-control form-select select-label"}
            ),
        }
