from .models import OCR
from django.http import HttpResponse

import json


def import_labels(request):
    labels_path = "/home/hue/Codes/persian_sms_spam_classification/computer_vision_twitter_media/fastai_labels.json"
    with open(labels_path, "r") as fp:
        labels = json.load(fp)

    data = []
    for file_name, (label, accuracy) in labels.items():
        if label == "message" and accuracy > 0.90:
            data.append(
                OCR(
                    name=file_name,
                    accuracy=accuracy,
                    is_added=False,
                )
            )

    OCR.objects.bulk_create(data)
    return HttpResponse(f"{len(data)} data added")
