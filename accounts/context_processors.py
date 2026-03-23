def subscription_status(request):
    """Inject subscription status into all templates."""
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        return {
            "is_premium": request.user.profile.is_premium,
            "subscription_plan": request.user.profile.subscription_plan,
        }
    return {
        "is_premium": False,
        "subscription_plan": "free",
    }
