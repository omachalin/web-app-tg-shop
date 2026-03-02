from django.http import HttpResponse

class TelegramCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if (
            not request.GET.get('tg') == '1' and
            not request.path.startswith('/secret-admin-panel/') and
            not request.path.startswith('/telegram_webhook/')
        ):
            return HttpResponse('')

        return self.get_response(request)
