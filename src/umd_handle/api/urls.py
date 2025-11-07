from django.urls import path

from . import views

urlpatterns = [
    path(
        "v1/handles/<str:prefix>/<int:suffix>",
        views.handles_prefix_suffix,
        name="handles_prefix_suffix"
    ),
]
