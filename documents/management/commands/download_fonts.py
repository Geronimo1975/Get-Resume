"""
Management command to download Google Fonts woff2 files for self-hosting.

DSGVO compliance: LG Muenchen ruling forbids loading fonts from Google CDN.
We download once and serve from our own static files.
"""

import os
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand


FONTS = {
    "inter/Inter-Regular.woff2": (
        "https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2"
    ),
    "inter/Inter-SemiBold.woff2": (
        "https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa25L7SUc.woff2"
    ),
    "inter/Inter-Bold.woff2": (
        "https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2"
    ),
    "merriweather/Merriweather-Regular.woff2": (
        "https://fonts.gstatic.com/s/merriweather/v30/u-440qyriQwlOrhSvowK_l5-fCZM.woff2"
    ),
    "merriweather/Merriweather-Bold.woff2": (
        "https://fonts.gstatic.com/s/merriweather/v30/u-4n0qyriQwlOrhSvowK_l52xwNZWMf6.woff2"
    ),
    "source-sans-pro/SourceSansPro-Regular.woff2": (
        "https://fonts.gstatic.com/s/sourcesanspro/v22/6xK3dSBYKcSV-LCoeQqfX1RYOo3qOK7l.woff2"
    ),
    "source-sans-pro/SourceSansPro-SemiBold.woff2": (
        "https://fonts.gstatic.com/s/sourcesanspro/v22/6xKydSBYKcSV-LCoeQqfX1RYOo3i54rwlxdu.woff2"
    ),
}


class Command(BaseCommand):
    help = "Download Google Fonts woff2 files to static/fonts/ for DSGVO-compliant self-hosting."

    def handle(self, *args, **options):
        fonts_dir = os.path.join(settings.BASE_DIR, "static", "fonts")
        os.makedirs(fonts_dir, exist_ok=True)

        for rel_path, url in FONTS.items():
            dest = os.path.join(fonts_dir, rel_path)
            dest_dir = os.path.dirname(dest)
            os.makedirs(dest_dir, exist_ok=True)

            if os.path.exists(dest):
                self.stdout.write(self.style.NOTICE(f"  SKIP  {rel_path} (already exists)"))
                continue

            self.stdout.write(f"  Downloading {rel_path} ...")
            try:
                urllib.request.urlretrieve(url, dest)
                self.stdout.write(self.style.SUCCESS(f"  OK    {rel_path}"))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  FAIL  {rel_path}: {exc}"))

        self.stdout.write(self.style.SUCCESS("\nFont download complete."))
