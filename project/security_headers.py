import secrets

from django.conf import settings


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = secrets.token_urlsafe(16)
        response = self.get_response(request)

        csp = getattr(settings, "CONTENT_SECURITY_POLICY", "")
        if csp:
            header = "Content-Security-Policy-Report-Only" if settings.CONTENT_SECURITY_POLICY_REPORT_ONLY else "Content-Security-Policy"
            response.setdefault(header, csp.format(csp_nonce=request.csp_nonce))

        corp = getattr(settings, "CROSS_ORIGIN_RESOURCE_POLICY", "")
        if corp:
            response.setdefault("Cross-Origin-Resource-Policy", corp)
        return response
