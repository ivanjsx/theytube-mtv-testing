from http import HTTPStatus

from django.shortcuts import render


def not_modified_304(request, exception=None):
    return render(
        request=request,
        template_name=f"core/{HTTPStatus.NOT_MODIFIED.value}.html",
        status=HTTPStatus.NOT_MODIFIED,
        context={
            "title": (f"{HTTPStatus.NOT_MODIFIED.value}: "
                      f"{HTTPStatus.NOT_MODIFIED.phrase}"),
            "custom_message": HTTPStatus.NOT_MODIFIED.description,
        }
    )


def bad_request_400(request, exception=None):
    return render(
        request=request,
        template_name=f"core/{HTTPStatus.BAD_REQUEST.value}.html",
        status=HTTPStatus.BAD_REQUEST,
        context={
            "title": (f"{HTTPStatus.BAD_REQUEST.value}: "
                      f"{HTTPStatus.BAD_REQUEST.phrase}"),
            "custom_message": HTTPStatus.BAD_REQUEST.description,
        }
    )


def forbidden_403(request, exception=None):
    return render(
        request=request,
        template_name=f"core/{HTTPStatus.FORBIDDEN.value}.html",
        status=HTTPStatus.FORBIDDEN,
        context={
            "title": (f"{HTTPStatus.FORBIDDEN.value}: "
                      f"{HTTPStatus.FORBIDDEN.phrase}"),
            "custom_message": HTTPStatus.FORBIDDEN.description,
        }
    )


def csrf_failure_403(request, reason=None):
    return render(
        request=request,
        template_name="core/403_csrf_failure.html",
        status=HTTPStatus.FORBIDDEN,
    )


def not_found_404(request, exception=None):
    return render(
        request=request,
        template_name=f"core/{HTTPStatus.NOT_FOUND.value}.html",
        status=HTTPStatus.NOT_FOUND,
        context={
            "title": (f"{HTTPStatus.NOT_FOUND.value}: "
                      f"{HTTPStatus.NOT_FOUND.phrase}"),
            "custom_message": HTTPStatus.NOT_FOUND.description,
        }
    )


def internal_server_error_500(request, exception=None):
    return render(
        request=request,
        template_name=f"core/{HTTPStatus.INTERNAL_SERVER_ERROR.value}.html",
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        context={
            "title": (f"{HTTPStatus.INTERNAL_SERVER_ERROR.value}: "
                      f"{HTTPStatus.INTERNAL_SERVER_ERROR.phrase}"),
            "custom_message": HTTPStatus.INTERNAL_SERVER_ERROR.description,
        }
    )
