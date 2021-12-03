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
import re
import emoji
from django.contrib.auth.decorators import login_required


def parser(text):
    # replace persian and arabic digits with equivalent englis digits
    num_dict = dict()
    num_dict[u"۰"] = u"0"
    num_dict[u"۱"] = u"1"
    num_dict[u"۲"] = u"2"
    num_dict[u"۳"] = u"3"
    num_dict[u"۴"] = u"4"
    num_dict[u"۵"] = u"5"
    num_dict[u"۶"] = u"6"
    num_dict[u"۷"] = u"7"
    num_dict[u"۸"] = u"8"
    num_dict[u"۹"] = u"9"

    num_dict[u"٠"] = u"0"
    num_dict[u"١"] = u"1"
    num_dict[u"٢"] = u"2"
    num_dict[u"٣"] = u"3"
    num_dict[u"٤"] = u"4"
    num_dict[u"٥"] = u"5"
    num_dict[u"٦"] = u"6"
    num_dict[u"٧"] = u"7"
    num_dict[u"٨"] = u"8"
    num_dict[u"٩"] = u"9"

    num_dict[u"٪"] = u"%"
    num_dict[u"؟"] = u"?"

    num_pattern = re.compile(r"(" + "|".join(num_dict.keys()) + r")")
    text = num_pattern.sub(lambda x: num_dict[x.group()], text)

    # Remove links
    text = re.sub(
        r"""(?i)\b((?:http|https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""",
        "&link",
        text,
    )
    text = re.sub(r"[a-zA-Z0-9_-]+\.(ir|com)", "&link", text)
    # Remove emojis
    text = emoji.get_emoji_regexp().sub(u"&emoji", text)

    # Remove dates
    text = re.sub(r"\\", "/", text)
    text = re.sub("(\d+/)*\d+/\d+", "&date", text)

    # Remove times
    text = re.sub("(\d+:)*\d+:\d+", "&time", text)

    # Remove phone
    text = re.sub("[^0-9](\(?(0|9)\d{6,}).*?", " &phone ", text)
    text = re.sub(r"(\d{3}-\d{3,}).*?", " &phone ", text)

    # remove numbers

    text = re.sub(r"،", ",", text)
    text = re.sub("\d+\.\d+", "&number", text)
    text = re.sub("[\d+\,]+\d+", "&number", text)
    text = re.sub("[0-9]+", "&number", text)

    text = re.sub(r"_", "", text)
    text = re.sub(r"@", "", text)
    text = re.sub(
        r"[a-zA-Z]+\b(?<!\&name)\b(?<!\&number)\b(?<!\&phone)\b(?<!\&time)\b(?<!\&date)\b(?<!\&emoji)\b(?<!\&link)",
        "&english",
        text,
    )

    return text


def fix_theme(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(gray, (5, 5))
    if cv2.mean(blur)[0] > 127:
        return image  # light
    else:
        return 1 - image  # dark


@login_required
def home_page(request):
    if request.user.username != "hue":
        messages.error(request, "Cannot access Home page")
        return redirect("add/")
    else:

        SMS_list = SMS.objects.all().order_by("id")
        paginator = Paginator(SMS_list, 24)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(
            request, "home.html", {"page_obj": page_obj, "total": len(SMS_list)}
        )


@login_required
def add_page(request):

    form = AddSMSForm()
    if request.method == "POST":
        form = AddSMSForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.text = parser(obj.text).strip()
            try:
                obj.save()

            except:
                messages.warning(request, "SMS with this Text already exists")
            else:
                messages.success(request, "SMS added successfully")
            return HttpResponseRedirect("")
    return render(request, "add.html", {"method": request.method, "form": form})


@login_required
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
            obj = form.save(commit=False)
            obj.text = parser(obj.text).strip()
            try:
                obj.save()

            except:
                messages.warning(request, "UNIQUE constraint failed")
            else:
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
            "total": len(OCR.objects.all().filter(is_added=False)),
        },
    )
