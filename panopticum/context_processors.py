from django.conf import settings


def page_content(request):
    return {'PAGE_TITLE': settings.PAGE_TITLE,
            'PAGE_FOOTER': settings.PAGE_FOOTER}
