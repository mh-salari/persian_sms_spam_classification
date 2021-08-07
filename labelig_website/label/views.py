from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.template import loader
from django.shortcuts import render, redirect
from .forms import AddSMSForm
from .models import SMS, OCR
from django.contrib import messages
import cv2
import pytesseract
import os


def fix_theme(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(gray, (5, 5))
    if cv2.mean(blur)[0] > 127:
        return image  # light
    else:
        return 1 - image  # dark


def home_page(request):
    SMS_list = SMS.objects.all()
    paginator = Paginator(SMS_list, 15)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "home.html", {"page_obj": page_obj})


def add_page(request):

    form = AddSMSForm()
    if request.method == "POST":
        form = AddSMSForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "SMS added successfully")
            return HttpResponseRedirect("")
    return render(request, "add.html", {"method": request.method, "form": form})


def ocr_page(request):
    disable = False
    image_name = ""
    images_path = (
        "/home/hue/Codes/persian_sms_spam_classification/search_twitter/database/media"
    )
    ocr = OCR.objects.all().filter(is_added=False).first()
    if ocr:
        image_name = ocr.name
        image = fix_theme(cv2.imread(os.path.join(images_path, image_name)))
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(img_rgb, lang="fas")
        # text = "asa"
        sms = SMS(text=text)
        form = AddSMSForm(instance=sms)
    else:
        messages.warning(request, "There are no more images")
        disable = True
        form = AddSMSForm()

    if request.method == "POST" and "skip" in request.POST:
        ocr.is_added = True
        ocr.save()
        return HttpResponseRedirect("")
    elif request.method == "POST" and "add" in request.POST:
        ocr.is_added = True
        ocr.save()
        form = AddSMSForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "SMS added successfully")
        return HttpResponseRedirect("")

    return render(
        request,
        "ocr.html",
        {
            "method": request.method,
            "form": form,
            "disable": disable,
            "image": image_name,
        },
    )
