from label import import_data
from django.urls import path, include
from . import views

urlpatterns = [
    path("add/", views.add_page, name="add_page"),
    path("ocr/", views.ocr_page, name="ocr_page"),
    path("", views.home_page, name="home_page"),
    path("accounts/", include("django.contrib.auth.urls")),
    # path("import_data/", import_data.import_labels, name="import_data"),
]
