class CookieConsentMiddleware:
    """
    TTDSG §25 compliant cookie consent middleware.
    Stub implementation — blocks no scripts yet. Will be fully implemented
    in Increment 2 (legal app).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # TODO: Check cookie consent state and set request.cookie_consent
        request.cookie_consent = {
            "necessary": True,
            "statistics": False,
            "marketing": False,
            "external_media": False,
        }
        return self.get_response(request)
