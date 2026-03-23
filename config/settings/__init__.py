import os

environment = os.environ.get("DJANGO_ENVIRONMENT", "local")

if environment == "production":
    from .production import *  # noqa: F401,F403
else:
    from .local import *  # noqa: F401,F403
