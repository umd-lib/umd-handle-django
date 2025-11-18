import json
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError

from .models import Handle, mint_new_handle

@csrf_exempt
def handles_exists(request):
    """
    Returns whether or not a handle exists with a specified repository and
    repository id
    """
    if request.method == 'GET':
        # Retrieve the "repo" and "repo_id" parameters
        repo = request.GET.get('repo', '')
        repo_id = request.GET.get('repo_id', '')

        if not repo or not repo_id:
            return JsonResponse({'errors': ["'repo' and 'repo_id' parameters are required"]}, status=400)

        try:
            handle = Handle.objects.get(repo=repo, repo_id=repo_id)
            exists = True
        except Handle.DoesNotExist:
            exists = False


        request_dict = {
            'repo': repo,
            'repo_id': repo_id
        }
        if exists:
            json_response = {
                'exists': True,
                'handle_url': handle.handle_url(),
                'prefix': handle.prefix,
                'suffix': str(handle.suffix),
                'url': handle.url,
                'request': request_dict
            }
        else:
            json_response = {
                'exists': False,
                'request': request_dict
            }

        return JsonResponse(json_response)


@csrf_exempt
def handles_info(request):
    """
    Returns additional information about a handle with a specified prefix and
    suffix
    """
    if request.method == 'GET':
        # Retrieve the "prefix" and "suffic" parameters
        prefix = request.GET.get('prefix', '')
        suffix = request.GET.get('suffix', '')

        if not prefix or not suffix:
            return JsonResponse({'errors': ["'prefix' and 'suffix' parameters are required"]}, status=400)

        try:
            handle = Handle.objects.get(prefix=prefix, suffix=suffix)
            exists = True
        except Handle.DoesNotExist:
            exists = False


        request_dict = {
            'prefix': prefix,
            'suffix': suffix
        }
        if exists:
            json_response = {
                'exists': True,
                'handle_url': handle.handle_url(),
                'prefix': handle.prefix,
                'suffix': str(handle.suffix),
                'url': handle.url,
                'request': request_dict
            }
        else:
            json_response = {
                'exists': False,
                'request': request_dict
            }

        return JsonResponse(json_response)


@csrf_exempt
def handles_prefix_suffix(request, prefix, suffix):
    """
    Returns the resolved URL for the given handle, or a 404 if the no
    handle is found.
    """
    try:
        handle = get_object_or_404(Handle, prefix=prefix, suffix=suffix)

        if request.method == 'GET':
            return handles_prefix_suffix_get(handle)
        elif request.method == 'PATCH':
            return handles_prefix_suffix_patch(request, handle)
        else:
            # Return 405 Method Not Allowed for any other method
            return HttpResponseNotAllowed(['GET', 'POST'])
    except Http404:
        # Return an empty JSON response, with a 404 status if the handle is
        # not found.
        return JsonResponse({}, status=404)


def handles_prefix_suffix_get(handle):
    """
    For GET requests to the "handles_prefix_suffix" endpoint, returns a
    JsonResponse containing the URL associated with the given handle.

    Returns a JsonResponse on success or error.
    """
    json_response = {
        "url": f"{handle.url}"
    }
    return JsonResponse(json_response)


def handles_prefix_suffix_patch(request, handle):
    """
    For PATCH requests to the "handles_prefix_suffix" endpoint, perform a
    partial update on the given handle.

    Returns a JsonResponse on success or error.
    """

    try:
        body = request.body.decode('utf-8')
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        return JsonResponse({'errors': ['Invalid JSON']}, status=400)

    allowed_fields = ['repo', 'repo_id', 'url', 'description', 'notes']

    for key in allowed_fields:
        if key in data:
            setattr(handle, key, data.get(key))

    try:
        handle.full_clean()
        handle.save()
    except ValidationError as e:
        messages = []
        if hasattr(e, 'message_dict'):
            for v in e.message_dict.values():
                if isinstance(v, (list, tuple)):
                    messages.extend([str(x) for x in v])
                else:
                    messages.append(str(v))
        else:
            messages = list(e.messages)
        return JsonResponse({'errors': messages}, status=400)
    except Exception as e:
        return JsonResponse({'errors': [str(e)]}, status=400)

    # Success response
    json_response = {
        'handle_url': handle.handle_url(),
        'request': {
            'prefix': handle.prefix,
            'repo': handle.repo,
            'repo_id': handle.repo_id,
            'url': handle.url
        }
    }
    return JsonResponse(json_response)


@csrf_exempt
@require_http_methods(["POST"])
def handles_mint_new_handle(request):
    """
    POST endpoint to mint a new handle. Expects a JSON body with keys:
    * prefix (str)
    * url (str)
    * repo (str)
    * repo_id (str)
    Optional: description, notes

    On success returns JSON with the created handle info, on failure returns
    status 400 with `{'errors': [...]}`.
    """
    try:
        body = request.body.decode('utf-8')
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        return JsonResponse({'errors': ['Invalid JSON']}, status=400)

    required = ['prefix', 'url', 'repo', 'repo_id']
    errors = []
    for key in required:
        if key not in data or data.get(key) in (None, ''):
            errors.append(f"'{key}' parameter is required")
    if errors:
        return JsonResponse({'errors': errors}, status=400)

    try:
        handle = mint_new_handle(
            prefix=data['prefix'],
            url=data['url'],
            repo=data['repo'],
            repo_id=data['repo_id'],
            description=data.get('description', ''),
            notes=data.get('notes', ''),
        )
    except ValidationError as e:
        messages = []
        if hasattr(e, 'message_dict'):
            for v in e.message_dict.values():
                if isinstance(v, (list, tuple)):
                    messages.extend([str(x) for x in v])
                else:
                    messages.append(str(v))
        else:
            messages = list(e.messages)
        return JsonResponse({'errors': messages}, status=400)
    except Exception as e:
        return JsonResponse({'errors': [str(e)]}, status=400)

    return JsonResponse(
        {
            'suffix': str(handle.suffix),
            'handle_url': handle.handle_url(),
            'request': {
                'prefix':data['prefix'],
                'repo':data['repo'],
                'repo_id':data['repo_id'],
                'url':data['url']
            }
        }
    )
