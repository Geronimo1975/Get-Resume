def cookie_consent(request):
    """Inject cookie consent status into all templates."""
    return {
        "cookie_consent": getattr(request, "cookie_consent", {
            "necessary": True,
            "statistics": False,
            "marketing": False,
            "external_media": False,
        }),
    }
