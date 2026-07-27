from django.conf import settings


class AdminSessionCookieMiddleware:
    """
    Give Django admin its own session cookie while the regular app keeps the
    default session cookie.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session_cookie_name = settings.SESSION_COOKIE_NAME
        admin_cookie_name = getattr(settings, "ADMIN_SESSION_COOKIE_NAME", "admin_sessionid")
        admin_path = "/" + settings.ADMIN_URL.lstrip("/")

        request._uses_admin_session_cookie = request.path.startswith(admin_path)
        if request._uses_admin_session_cookie:
            admin_cookie = request.COOKIES.get(admin_cookie_name)
            if admin_cookie:
                request.COOKIES[session_cookie_name] = admin_cookie
            else:
                request.COOKIES.pop(session_cookie_name, None)

        response = self.get_response(request)

        if request._uses_admin_session_cookie and session_cookie_name in response.cookies:
            original_cookie = response.cookies[session_cookie_name]
            response.cookies[admin_cookie_name] = original_cookie.value

            for key, value in original_cookie.items():
                if value:
                    response.cookies[admin_cookie_name][key] = value

            response.cookies[admin_cookie_name]["path"] = admin_path
            del response.cookies[session_cookie_name]

        return response
