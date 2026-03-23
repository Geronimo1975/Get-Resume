# Blog Models and Views Reference

## Overview

This reference documents the complete blog system for the Karriere-Blog, including SEO-optimized models, views, RSS feed, sitemap generation, and admin configuration. The blog serves as a content marketing engine for the Lebenslauf-Builder platform, targeting German-language career and resume-related keywords.

---

## 1. SEOMixin Abstract Model

```python
# blog/models.py

from django.db import models
from django.utils.text import slugify


class SEOMixin(models.Model):
    """
    Abstract model mixin providing SEO metadata fields.

    Used by Article, Category, and any page that needs
    individual SEO control. Fields follow Google's recommendations
    for meta tags, Open Graph (Facebook), and Twitter Cards.

    Character limits:
    - meta_title: 60 chars (Google truncates at ~60)
    - meta_description: 160 chars (Google truncates at ~155-160)
    """

    meta_title = models.CharField(
        max_length=70,
        blank=True,
        default="",
        verbose_name="SEO-Titel",
        help_text=(
            "Titel fuer Suchmaschinen (max. 60 Zeichen empfohlen). "
            "Leer = automatisch aus Seitentitel generiert."
        ),
    )
    meta_description = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Meta-Beschreibung",
        help_text=(
            "Beschreibung fuer Suchmaschinen (max. 160 Zeichen empfohlen). "
            "Wird in Google-Suchergebnissen angezeigt."
        ),
    )
    og_image = models.ImageField(
        upload_to="seo/og-images/%Y/%m/",
        blank=True,
        verbose_name="Open-Graph-Bild",
        help_text=(
            "Bild fuer Social-Media-Vorschau (empfohlen: 1200x630 px). "
            "Leer = Featured Image oder Standard-OG-Bild."
        ),
    )
    canonical_url = models.URLField(
        blank=True,
        default="",
        verbose_name="Kanonische URL",
        help_text=(
            "Kanonische URL, wenn der Inhalt auf einer anderen URL "
            "zuerst veroeffentlicht wurde (verhindert Duplicate Content)."
        ),
    )
    noindex = models.BooleanField(
        default=False,
        verbose_name="Nicht indexieren (noindex)",
        help_text="Aktivieren, um diese Seite von Suchmaschinen auszuschliessen.",
    )
    nofollow = models.BooleanField(
        default=False,
        verbose_name="Links nicht folgen (nofollow)",
        help_text="Aktivieren, um Suchmaschinen anzuweisen, Links nicht zu folgen.",
    )

    class Meta:
        abstract = True

    def get_meta_title(self):
        """Return meta_title or generate from title field."""
        if self.meta_title:
            return self.meta_title
        if hasattr(self, "title"):
            return f"{self.title} | Lebenslauf-Builder Karriere-Blog"
        return "Lebenslauf-Builder Karriere-Blog"

    def get_meta_description(self):
        """Return meta_description or generate from excerpt/content."""
        if self.meta_description:
            return self.meta_description
        if hasattr(self, "excerpt") and self.excerpt:
            return self.excerpt[:160]
        return ""

    def get_og_image_url(self):
        """Return OG image URL or fallback."""
        if self.og_image:
            return self.og_image.url
        if hasattr(self, "featured_image") and self.featured_image:
            return self.featured_image.url
        return None  # Template will use default OG image

    def get_robots_meta(self):
        """Generate robots meta content string."""
        directives = []
        if self.noindex:
            directives.append("noindex")
        else:
            directives.append("index")
        if self.nofollow:
            directives.append("nofollow")
        else:
            directives.append("follow")
        return ", ".join(directives)
```

---

## 2. Article Model

```python
# blog/models.py (continued)

import uuid
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


class Article(SEOMixin):
    """
    Blog article model with full SEO support.

    Supports:
    - Draft/Published workflow with scheduled publishing
    - Pillar article designation for content strategy
    - Rich content with markdown or HTML
    - Category and tag taxonomies
    - Author profiles with expertise areas
    - Reading time estimation
    - Related articles
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Entwurf"
        REVIEW = "review", "In Pruefung"
        PUBLISHED = "published", "Veroeffentlicht"
        ARCHIVED = "archived", "Archiviert"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # === Core fields ===
    title = models.CharField(
        max_length=200,
        verbose_name="Titel",
        help_text="Artikeltitel (H1). Optimal: 50-60 Zeichen fuer SEO.",
    )
    slug = models.SlugField(
        max_length=250,
        unique=True,
        verbose_name="URL-Slug",
        help_text="URL-freundlicher Name. Wird automatisch aus dem Titel generiert.",
    )
    excerpt = models.TextField(
        max_length=500,
        verbose_name="Auszug / Teaser",
        help_text=(
            "Kurze Zusammenfassung fuer Listenansichten und "
            "Meta-Beschreibung (150-200 Zeichen empfohlen)."
        ),
    )
    content = models.TextField(
        verbose_name="Inhalt",
        help_text="Artikelinhalt in Markdown oder HTML.",
    )

    # === Taxonomy ===
    category = models.ForeignKey(
        "Category",
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="Kategorie",
    )
    tags = models.ManyToManyField(
        "Tag",
        blank=True,
        related_name="articles",
        verbose_name="Schlagwoerter",
    )

    # === Author ===
    author = models.ForeignKey(
        "Author",
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="Autor",
    )

    # === Media ===
    featured_image = models.ImageField(
        upload_to="blog/featured/%Y/%m/",
        blank=True,
        verbose_name="Beitragsbild",
        help_text="Hauptbild des Artikels (empfohlen: 1200x675 px, 16:9).",
    )
    featured_image_alt = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Beitragsbild Alt-Text",
        help_text="Beschreibender Alt-Text fuer Barrierefreiheit und SEO.",
    )
    featured_image_caption = models.CharField(
        max_length=300,
        blank=True,
        default="",
        verbose_name="Beitragsbild Bildunterschrift",
    )

    # === Publishing ===
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Status",
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Veroeffentlicht am",
        help_text="Datum/Uhrzeit der Veroeffentlichung. Zukunftsdatum = geplant.",
    )

    # === Content strategy ===
    is_pillar_article = models.BooleanField(
        default=False,
        verbose_name="Pillar-Artikel",
        help_text=(
            "Pillar-Artikel sind umfassende Leitfaeden zu einem Kernthema. "
            "Sie dienen als Ankerpunkt fuer interne Verlinkung."
        ),
    )
    related_articles = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        verbose_name="Verwandte Artikel",
    )

    # === Reading metrics ===
    reading_time_minutes = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Lesezeit (Minuten)",
        help_text="Wird automatisch berechnet bei Speicherung.",
    )
    word_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Wortanzahl",
    )

    # === Analytics ===
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Aufrufe",
    )

    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blog_articles"
        ordering = ["-published_at"]
        verbose_name = "Artikel"
        verbose_name_plural = "Artikel"
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=False)

        # Calculate reading time (average 200 words/minute for German text)
        if self.content:
            import re
            words = len(re.findall(r"\w+", self.content))
            self.word_count = words
            self.reading_time_minutes = max(1, round(words / 200))

        # Auto-set published_at when status changes to published
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:article_detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        """Check if article is published and publication date has passed."""
        if self.status != self.Status.PUBLISHED:
            return False
        if not self.published_at:
            return False
        return self.published_at <= timezone.now()

    @classmethod
    def published_articles(cls):
        """QuerySet of currently published articles."""
        return cls.objects.filter(
            status=cls.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        )
```

---

## 3. Category Model

```python
# blog/models.py (continued)

class Category(SEOMixin):
    """
    Blog category for organizing articles.

    Categories represent major topic areas of the Karriere-Blog:
    - Lebenslauf-Tipps
    - Bewerbung schreiben
    - Vorstellungsgespraech
    - Karriereplanung
    - Branchenspezifisch
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Name",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name="URL-Slug",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Beschreibung",
        help_text="Beschreibung fuer die Kategorie-Seite (SEO-relevant).",
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Icon-Klasse",
        help_text="CSS-Icon-Klasse (z.B. 'bi-file-earmark-text').",
    )
    ordering = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Sortierung",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktiv",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blog_categories"
        ordering = ["ordering", "name"]
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=False)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category_detail", kwargs={"slug": self.slug})

    @property
    def published_article_count(self):
        return self.articles.filter(
            status=Article.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        ).count()
```

---

## 4. Tag Model

```python
# blog/models.py (continued)

class Tag(models.Model):
    """
    Blog tag for fine-grained article classification.

    Tags are used for:
    - Topic clustering (e.g., "Initiativbewerbung", "Berufseinstieg")
    - Internal linking opportunities
    - Tag cloud generation
    - Content recommendation
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="Name",
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL-Slug",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "blog_tags"
        ordering = ["name"]
        verbose_name = "Schlagwort"
        verbose_name_plural = "Schlagwoerter"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=False)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:tag_detail", kwargs={"slug": self.slug})

    @property
    def published_article_count(self):
        return self.articles.filter(
            status=Article.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        ).count()
```

---

## 5. Author Model

```python
# blog/models.py (continued)

class Author(models.Model):
    """
    Blog author profile.

    Separate from User model to allow:
    - Guest authors without accounts
    - Multiple author bios
    - Author schema.org structured data
    - E-E-A-T signals for Google
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="author_profile",
        verbose_name="Benutzer",
    )
    name = models.CharField(
        max_length=150,
        verbose_name="Name",
    )
    slug = models.SlugField(
        max_length=170,
        unique=True,
        verbose_name="URL-Slug",
    )
    bio = models.TextField(
        verbose_name="Biografie",
        help_text="Kurzbiografie des Autors (fuer Autorenbox und schema.org).",
    )
    bio_short = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Kurz-Bio",
        help_text="Einzeiler fuer kompakte Autorendarstellungen.",
    )
    photo = models.ImageField(
        upload_to="blog/authors/",
        blank=True,
        verbose_name="Foto",
        help_text="Autorenfoto (empfohlen: 400x400 px, quadratisch).",
    )
    expertise = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Fachgebiete",
        help_text='Liste von Fachgebieten, z.B. ["Karriereberatung", "HR"].',
    )
    linkedin_url = models.URLField(
        blank=True,
        default="",
        verbose_name="LinkedIn-Profil",
    )
    xing_url = models.URLField(
        blank=True,
        default="",
        verbose_name="XING-Profil",
    )
    website_url = models.URLField(
        blank=True,
        default="",
        verbose_name="Website",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktiv",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blog_authors"
        ordering = ["name"]
        verbose_name = "Autor"
        verbose_name_plural = "Autoren"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=False)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:author_detail", kwargs={"slug": self.slug})

    @property
    def published_article_count(self):
        return self.articles.filter(
            status=Article.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        ).count()
```

---

## 6. Blog Views

```python
# blog/views.py

from django.db.models import F, Q, Count, Prefetch
from django.http import Http404
from django.utils import timezone
from django.views.generic import ListView, DetailView

from .models import Article, Category, Tag, Author


class BlogListView(ListView):
    """
    Blog article listing page (main blog index).

    URL: /karriere-blog/
    Template: blog/article_list.html

    Features:
    - Paginated list of published articles
    - Sidebar with categories, popular articles, tag cloud
    - Featured/pillar articles highlighted at top
    - SEO: meta tags, structured data (CollectionPage)
    """

    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        return (
            Article.published_articles()
            .select_related("category", "author")
            .prefetch_related("tags")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Featured pillar articles (for hero section)
        context["pillar_articles"] = (
            Article.published_articles()
            .filter(is_pillar_article=True)
            .select_related("category", "author")
            .order_by("-published_at")[:3]
        )

        # Sidebar: Categories with article counts
        context["categories"] = (
            Category.objects
            .filter(is_active=True)
            .annotate(
                article_count=Count(
                    "articles",
                    filter=Q(
                        articles__status=Article.Status.PUBLISHED,
                        articles__published_at__lte=timezone.now(),
                    ),
                )
            )
            .filter(article_count__gt=0)
            .order_by("ordering", "name")
        )

        # Sidebar: Popular articles (by view count)
        context["popular_articles"] = (
            Article.published_articles()
            .order_by("-view_count")[:5]
            .values("title", "slug", "view_count")
        )

        # Sidebar: Tag cloud
        context["tags"] = (
            Tag.objects
            .annotate(
                article_count=Count(
                    "articles",
                    filter=Q(
                        articles__status=Article.Status.PUBLISHED,
                        articles__published_at__lte=timezone.now(),
                    ),
                )
            )
            .filter(article_count__gt=0)
            .order_by("-article_count")[:30]
        )

        # SEO
        context["page_meta_title"] = "Karriere-Blog | Lebenslauf-Builder"
        context["page_meta_description"] = (
            "Tipps und Ratgeber fuer Lebenslauf, Bewerbung und Karriere. "
            "Experten-Wissen fuer Ihren beruflichen Erfolg."
        )

        return context


class BlogDetailView(DetailView):
    """
    Single blog article page.

    URL: /karriere-blog/<slug>/
    Template: blog/article_detail.html

    Features:
    - Full article content with table of contents
    - Author box with bio and social links
    - Related articles
    - JSON-LD BlogPosting structured data
    - Breadcrumbs
    - Social sharing buttons
    - View count tracking
    """

    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        # Allow draft preview for staff
        if self.request.user.is_staff:
            return Article.objects.select_related("category", "author").prefetch_related("tags")

        return (
            Article.published_articles()
            .select_related("category", "author")
            .prefetch_related("tags", "related_articles")
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # Check publication status for non-staff
        if not self.request.user.is_staff and not obj.is_published:
            raise Http404

        return obj

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # Increment view count (fire-and-forget, no race condition concern)
        Article.objects.filter(pk=self.object.pk).update(
            view_count=F("view_count") + 1
        )

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object

        # Related articles
        context["related_articles"] = (
            article.related_articles
            .filter(
                status=Article.Status.PUBLISHED,
                published_at__lte=timezone.now(),
            )
            .select_related("category")[:4]
        )

        # If no manual related articles, use same-category articles
        if not context["related_articles"]:
            context["related_articles"] = (
                Article.published_articles()
                .filter(category=article.category)
                .exclude(pk=article.pk)
                .select_related("category")
                .order_by("-published_at")[:4]
            )

        # Breadcrumb data
        context["breadcrumbs"] = [
            {"name": "Karriere-Blog", "url": "/karriere-blog/"},
            {"name": article.category.name, "url": article.category.get_absolute_url()},
            {"name": article.title, "url": None},
        ]

        # Table of contents (extract H2/H3 from content)
        context["toc"] = self._generate_toc(article.content)

        # Previous/Next navigation
        published = Article.published_articles().order_by("published_at")
        context["previous_article"] = (
            published.filter(published_at__lt=article.published_at).last()
        )
        context["next_article"] = (
            published.filter(published_at__gt=article.published_at).first()
        )

        return context

    def _generate_toc(self, content):
        """Extract H2 and H3 headings from content for table of contents."""
        import re
        headings = []
        # Match markdown headings
        for match in re.finditer(r"^(#{2,3})\s+(.+)$", content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            anchor = slugify(text, allow_unicode=False)
            headings.append({
                "level": level,
                "text": text,
                "anchor": anchor,
            })
        return headings


class CategoryDetailView(ListView):
    """
    Category archive page showing articles in a specific category.

    URL: /karriere-blog/kategorie/<slug>/
    Template: blog/category_detail.html
    """

    template_name = "blog/category_detail.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        self.category = Category.objects.filter(
            slug=self.kwargs["slug"],
            is_active=True,
        ).first()

        if not self.category:
            raise Http404

        return (
            Article.published_articles()
            .filter(category=self.category)
            .select_related("author")
            .prefetch_related("tags")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category

        context["breadcrumbs"] = [
            {"name": "Karriere-Blog", "url": "/karriere-blog/"},
            {"name": self.category.name, "url": None},
        ]

        return context


class TagDetailView(ListView):
    """
    Tag archive page showing articles with a specific tag.

    URL: /karriere-blog/tag/<slug>/
    Template: blog/tag_detail.html
    """

    template_name = "blog/tag_detail.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        self.tag = Tag.objects.filter(slug=self.kwargs["slug"]).first()

        if not self.tag:
            raise Http404

        return (
            Article.published_articles()
            .filter(tags=self.tag)
            .select_related("category", "author")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag

        context["breadcrumbs"] = [
            {"name": "Karriere-Blog", "url": "/karriere-blog/"},
            {"name": f"#{self.tag.name}", "url": None},
        ]

        return context


class AuthorDetailView(DetailView):
    """
    Author page showing bio and authored articles.

    URL: /karriere-blog/autor/<slug>/
    Template: blog/author_detail.html
    """

    model = Author
    template_name = "blog/author_detail.html"
    context_object_name = "author"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Author.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["articles"] = (
            Article.published_articles()
            .filter(author=self.object)
            .select_related("category")
            .order_by("-published_at")[:20]
        )

        return context
```

---

## 7. RSS Feed

```python
# blog/feeds.py

from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed

from .models import Article


class BlogRSSFeed(Feed):
    """
    RSS 2.0 feed for the Karriere-Blog.

    URL: /karriere-blog/feed/rss/
    Content-Type: application/rss+xml

    Provides the 20 most recent published articles with:
    - Title, link, description
    - Author name
    - Category
    - Publication date
    - Featured image as enclosure
    """

    feed_type = Rss201rev2Feed
    title = "Lebenslauf-Builder Karriere-Blog"
    description = (
        "Aktuelle Tipps und Ratgeber zu Lebenslauf, Bewerbung und Karriere "
        "von den Experten des Lebenslauf-Builders."
    )
    language = "de"
    author_name = "Lebenslauf-Builder Redaktion"
    feed_copyright = "Copyright Lebenslauf-Builder GmbH"
    categories = [
        "Karriere",
        "Bewerbung",
        "Lebenslauf",
    ]

    def link(self):
        return reverse("blog:article_list")

    def items(self):
        return (
            Article.published_articles()
            .select_related("category", "author")
            .order_by("-published_at")[:20]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_name(self, item):
        return item.author.name

    def item_pubdate(self, item):
        return item.published_at

    def item_updateddate(self, item):
        return item.updated_at

    def item_categories(self, item):
        categories = [item.category.name]
        categories.extend(item.tags.values_list("name", flat=True))
        return categories

    def item_enclosures(self, item):
        """Include featured image as RSS enclosure."""
        if item.featured_image:
            from django.utils.feedgenerator import Enclosure
            return [Enclosure(
                url=item.featured_image.url,
                length=str(item.featured_image.size),
                mime_type="image/jpeg",
            )]
        return []


class CategoryRSSFeed(BlogRSSFeed):
    """
    RSS feed for a specific category.

    URL: /karriere-blog/kategorie/<slug>/feed/rss/
    """

    def get_object(self, request, slug):
        from .models import Category
        return Category.objects.get(slug=slug, is_active=True)

    def title(self, obj):
        return f"{obj.name} | Lebenslauf-Builder Karriere-Blog"

    def description(self, obj):
        return obj.description or f"Artikel zum Thema {obj.name}"

    def link(self, obj):
        return obj.get_absolute_url()

    def items(self, obj):
        return (
            Article.published_articles()
            .filter(category=obj)
            .select_related("author")
            .order_by("-published_at")[:20]
        )
```

---

## 8. Sitemap Generation Management Command

```python
# blog/management/commands/generate_sitemap.py

import os
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Generate XML sitemap for blog and static pages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Output file path (default: STATIC_ROOT/sitemap.xml)",
        )

    def handle(self, *args, **options):
        from blog.models import Article, Category, Tag, Author

        output_path = options.get("output") or os.path.join(
            settings.STATIC_ROOT, "sitemap.xml"
        )

        base_url = settings.SITE_URL.rstrip("/")  # e.g., https://www.lebenslauf-builder.de

        urlset = Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        urlset.set("xmlns:xhtml", "http://www.w3.org/1999/xhtml")
        urlset.set("xmlns:image", "http://www.google.com/schemas/sitemap-image/1.1")

        # === Static pages ===
        static_pages = [
            ("/", "1.0", "daily"),
            ("/preise/", "0.9", "weekly"),
            ("/lebenslauf-vorlagen/", "0.9", "weekly"),
            ("/anschreiben-vorlagen/", "0.8", "weekly"),
            ("/karriere-blog/", "0.9", "daily"),
            ("/ueber-uns/", "0.5", "monthly"),
            ("/kontakt/", "0.4", "monthly"),
            ("/impressum/", "0.2", "yearly"),
            ("/datenschutz/", "0.2", "yearly"),
            ("/agb/", "0.2", "yearly"),
        ]

        for path, priority, changefreq in static_pages:
            url = SubElement(urlset, "url")
            SubElement(url, "loc").text = f"{base_url}{path}"
            SubElement(url, "priority").text = priority
            SubElement(url, "changefreq").text = changefreq

            # Add hreflang for DE/EN pages
            xhtml_de = SubElement(url, "xhtml:link")
            xhtml_de.set("rel", "alternate")
            xhtml_de.set("hreflang", "de")
            xhtml_de.set("href", f"{base_url}{path}")

            xhtml_en = SubElement(url, "xhtml:link")
            xhtml_en.set("rel", "alternate")
            xhtml_en.set("hreflang", "en")
            xhtml_en.set("href", f"{base_url}/en{path}")

        # === Blog articles ===
        articles = (
            Article.published_articles()
            .select_related("category")
            .order_by("-published_at")
        )

        for article in articles:
            url = SubElement(urlset, "url")
            SubElement(url, "loc").text = f"{base_url}{article.get_absolute_url()}"
            SubElement(url, "lastmod").text = article.updated_at.strftime("%Y-%m-%d")
            SubElement(url, "changefreq").text = "weekly"

            # Pillar articles get higher priority
            priority = "0.8" if article.is_pillar_article else "0.7"
            SubElement(url, "priority").text = priority

            # Add image sitemap data
            if article.featured_image:
                image = SubElement(url, "image:image")
                SubElement(image, "image:loc").text = f"{base_url}{article.featured_image.url}"
                if article.featured_image_alt:
                    SubElement(image, "image:caption").text = article.featured_image_alt
                SubElement(image, "image:title").text = article.title

        # === Categories ===
        categories = Category.objects.filter(is_active=True)

        for category in categories:
            url = SubElement(urlset, "url")
            SubElement(url, "loc").text = f"{base_url}{category.get_absolute_url()}"
            SubElement(url, "changefreq").text = "weekly"
            SubElement(url, "priority").text = "0.6"

        # === Tags (only those with articles) ===
        tags = Tag.objects.annotate(
            article_count=models.Count(
                "articles",
                filter=models.Q(
                    articles__status=Article.Status.PUBLISHED,
                    articles__published_at__lte=timezone.now(),
                ),
            )
        ).filter(article_count__gt=0)

        for tag in tags:
            url = SubElement(urlset, "url")
            SubElement(url, "loc").text = f"{base_url}{tag.get_absolute_url()}"
            SubElement(url, "changefreq").text = "weekly"
            SubElement(url, "priority").text = "0.5"

        # === Authors ===
        authors = Author.objects.filter(is_active=True)

        for author in authors:
            url = SubElement(urlset, "url")
            SubElement(url, "loc").text = f"{base_url}{author.get_absolute_url()}"
            SubElement(url, "changefreq").text = "monthly"
            SubElement(url, "priority").text = "0.5"

        # Write file
        tree = ElementTree(urlset)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as f:
            tree.write(f, encoding="UTF-8", xml_declaration=True)

        total_urls = len(urlset)
        self.stdout.write(self.style.SUCCESS(
            f"Sitemap generated: {output_path} ({total_urls} URLs)"
        ))
```

---

## 9. Admin Configuration

```python
# blog/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Category, Tag, Author


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "author",
        "status",
        "is_pillar_article",
        "published_at",
        "view_count",
        "reading_time_minutes",
    ]
    list_filter = [
        "status",
        "category",
        "is_pillar_article",
        "published_at",
        "author",
    ]
    search_fields = [
        "title",
        "excerpt",
        "content",
    ]
    prepopulated_fields = {
        "slug": ("title",),
    }
    date_hierarchy = "published_at"
    ordering = ["-updated_at"]
    readonly_fields = [
        "id",
        "view_count",
        "word_count",
        "reading_time_minutes",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["author"]
    filter_horizontal = ["tags", "related_articles"]

    fieldsets = (
        ("Artikel", {
            "fields": (
                "title",
                "slug",
                "excerpt",
                "content",
                "featured_image",
                "featured_image_alt",
                "featured_image_caption",
            ),
        }),
        ("Taxonomie", {
            "fields": (
                "category",
                "tags",
                "author",
            ),
        }),
        ("Veroeffentlichung", {
            "fields": (
                "status",
                "published_at",
                "is_pillar_article",
                "related_articles",
            ),
        }),
        ("SEO", {
            "classes": ("collapse",),
            "fields": (
                "meta_title",
                "meta_description",
                "og_image",
                "canonical_url",
                "noindex",
                "nofollow",
            ),
        }),
        ("Statistiken", {
            "classes": ("collapse",),
            "fields": (
                "view_count",
                "word_count",
                "reading_time_minutes",
            ),
        }),
        ("System", {
            "classes": ("collapse",),
            "fields": (
                "id",
                "created_at",
                "updated_at",
            ),
        }),
    )

    actions = ["publish_articles", "unpublish_articles"]

    @admin.action(description="Ausgewaehlte Artikel veroeffentlichen")
    def publish_articles(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status=Article.Status.DRAFT).update(
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.message_user(request, f"{updated} Artikel veroeffentlicht.")

    @admin.action(description="Ausgewaehlte Artikel zurueckziehen")
    def unpublish_articles(self, request, queryset):
        updated = queryset.update(status=Article.Status.DRAFT)
        self.message_user(request, f"{updated} Artikel zurueckgezogen.")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "ordering",
        "is_active",
        "published_article_count",
    ]
    list_editable = ["ordering", "is_active"]
    prepopulated_fields = {
        "slug": ("name",),
    }
    search_fields = ["name"]

    def published_article_count(self, obj):
        return obj.published_article_count
    published_article_count.short_description = "Artikel"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "published_article_count",
    ]
    prepopulated_fields = {
        "slug": ("name",),
    }
    search_fields = ["name"]

    def published_article_count(self, obj):
        return obj.published_article_count
    published_article_count.short_description = "Artikel"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "author_photo",
        "is_active",
        "published_article_count",
        "linkedin_url_link",
    ]
    list_filter = ["is_active"]
    prepopulated_fields = {
        "slug": ("name",),
    }
    search_fields = ["name", "bio"]
    raw_id_fields = ["user"]

    def author_photo(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="32" height="32" '
                'style="border-radius: 50%; object-fit: cover;">',
                obj.photo.url,
            )
        return "-"
    author_photo.short_description = "Foto"

    def linkedin_url_link(self, obj):
        if obj.linkedin_url:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">LinkedIn</a>',
                obj.linkedin_url,
            )
        return "-"
    linkedin_url_link.short_description = "LinkedIn"

    def published_article_count(self, obj):
        return obj.published_article_count
    published_article_count.short_description = "Artikel"
```

---

## URL Configuration

```python
# blog/urls.py

from django.urls import path
from . import views
from .feeds import BlogRSSFeed, CategoryRSSFeed

app_name = "blog"

urlpatterns = [
    # Main blog listing
    path(
        "",
        views.BlogListView.as_view(),
        name="article_list",
    ),

    # RSS feeds
    path(
        "feed/rss/",
        BlogRSSFeed(),
        name="rss_feed",
    ),

    # Category pages
    path(
        "kategorie/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path(
        "kategorie/<slug:slug>/feed/rss/",
        CategoryRSSFeed(),
        name="category_rss_feed",
    ),

    # Tag pages
    path(
        "tag/<slug:slug>/",
        views.TagDetailView.as_view(),
        name="tag_detail",
    ),

    # Author pages
    path(
        "autor/<slug:slug>/",
        views.AuthorDetailView.as_view(),
        name="author_detail",
    ),

    # Article detail (must be last - catches all slugs)
    path(
        "<slug:slug>/",
        views.BlogDetailView.as_view(),
        name="article_detail",
    ),
]

# In main urls.py:
# path("karriere-blog/", include("blog.urls")),
```
