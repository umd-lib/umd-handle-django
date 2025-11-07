from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse,  Http404

from .models import Handle

def handles_prefix_suffix(request, prefix, suffix):
    """
    Returns the resolved URL for the given handle, or a 404 if the no
    handle is found.
    """
    try:
        handle = get_object_or_404(Handle, prefix=prefix, suffix=suffix)

        json_response = {
            "url":f"{handle.url}"
        }
        return JsonResponse(json_response)
    except Http404:
        # Return an empty JSON response, with a 404 status if the handle is
        # not found.
        return JsonResponse({}, status=404)
