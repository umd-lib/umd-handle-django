from django.urls import path

from . import views

urlpatterns = [
    path(
        "v1/handles/<str:prefix>/<int:suffix>",
        views.handles_prefix_suffix,
        name="handles_prefix_suffix"
    ),
    path(
        "v1/handles",
        views.handles_mint_new_handle,
        name="handles_mint_new_handle"
    ),
    path(
        "v1/handles/exists",
        views.handles_exists,
        name="handles_exists"
    ),
    path(
        "v1/handles/info",
        views.handles_info,
        name="handles_info"
    ),
]
