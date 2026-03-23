# Admin Dashboard Prompts — GetResume (Django Unfold)

> 50 prompturi pentru construirea admin panel-ului cu Django Unfold

---

## Setup & Configurare (1-10)

### 1. Instalare Django Unfold
Instaleaza django-unfold si configureaza-l in config/settings/base.py. Adauga unfold, unfold.contrib.filters, unfold.contrib.forms, unfold.contrib.inlines INAINTE de django.contrib.admin in INSTALLED_APPS. Seteaza UNFOLD dict cu SITE_TITLE="GetResume Admin", SITE_HEADER="GetResume", SITE_SYMBOL="description".

### 2. Sidebar Navigation cu Sectiuni
Configureaza UNFOLD["SIDEBAR"]["navigation"] cu 5 grupuri: Dashboard (icon: dashboard), Benutzer (icon: people), Dokumente (icon: description), Rechtliches (icon: gavel), Support (icon: support_agent). Fiecare grup sa aiba items cu title, icon, link folosind reverse_lazy.

### 3. Environment Badge
Creeaza environment_callback(request) in config/settings/base.py care returneaza ["Production", "danger"] sau ["Development", "info"] bazat pe DJANGO_ENVIRONMENT env var. Leaga-l in UNFOLD["ENVIRONMENT"].

### 4. Custom Color Scheme
Configureaza UNFOLD["COLORS"]["primary"] cu un albastru profesional (#2563EB shades) pentru brand GetResume. Genereaza toate 11 shade-urile (50-950) in format RGB space-separated.

### 5. Admin URL Customization
Muta admin-ul de la /admin-dashboard/ si asigura-te ca UNFOLD il preia corect. Verifica ca toate reverse_lazy references functioneaza cu noul admin site.

### 6. Admin Base Classes
Creeaza fisierul admin/base.py cu BaseModelAdmin(unfold.admin.ModelAdmin) care include: list_per_page=25, show_full_result_count=False, compressed_fields=True, warn_unsaved_form=True, si un get_queryset care exclude soft-deleted records (deleted_at__isnull=True).

### 7. ReadOnlyModelAdmin
In admin/base.py adauga ReadOnlyModelAdmin(BaseModelAdmin) cu has_add_permission, has_change_permission, has_delete_permission toate returnand False. Foloseste-l pentru audit logs si analytics.

### 8. Admin File Structure
Restructureaza fiecare app Django (accounts, documents, legal, payments) sa aiba admin/ folder cu __init__.py, base.py, si cate un fisier per model. Muta admin.py existent in noua structura.

### 9. Static Files pentru Unfold
Configureaza collectstatic sa includa Unfold assets. Verifica ca WhiteNoise serveste corect CSS/JS-ul Unfold in productie. Testeaza in docker-compose.prod.yml.

### 10. Admin Permissions Setup
Creeaza 3 grupuri de permisiuni: Admin (full access), Support (read users + manage tickets), Viewer (read-only pe tot). Configureaza-le in admin cu Group admin registration.

---

## User Management (11-20)

### 11. Custom UserAdmin cu Unfold
Inregistreaza accounts.User cu UnfoldUserAdmin extins din BaseModelAdmin. list_display: email, full_name, subscription_plan, display_status, date_joined, last_login. Adauga search_fields pe email si first_name.

### 12. User Status Display Decorator
Foloseste @display(description="Status", label={True: "success", False: "danger"}) pe display_status care returneaza obj.is_active. Adauga si display pentru subscription_plan cu label-uri colorate: free=warning, pro=success, enterprise=info.

### 13. User Profile Inline
Creeaza UserProfileInline(unfold.admin.StackedInline) pentru UserProfile. Afiseaza: phone, anrede, geburtsdatum, strasse, plz, stadt, bundesland, privacy_accepted_at, marketing_consent, newsletter_consent. readonly_fields pentru timestamps.

### 14. User Filters Avansate
Adauga list_filter cu Unfold filters: ("date_joined", RangeDateFilter), ("subscription_plan", ChoicesDropdownFilter), ("is_active", DropdownFilter), ("profile__marketing_consent", DropdownFilter). Import din unfold.contrib.filters.admin.

### 15. User Actions Bulk
Creeaza actions: activate_users, deactivate_users, export_users_csv, send_password_reset. Fiecare cu @admin.action(description="..."). export_users_csv sa genereze CSV cu email, name, plan, date_joined, last_login.

### 16. Online Users Tracking
Creeaza middleware OnlineUsersMiddleware care salveaza in Redis (db0) un set "online_users" cu user_id si TTL 5 minute. In admin dashboard widget, afiseaza numarul de useri online cu `redis_client.scard("online_users")`.

### 17. User Activity Log
Creeaza model UserActivityLog(user, action, ip_address, user_agent, created_at). Inregistreaza login, logout, document_create, document_export, password_change. Admin read-only cu filtre pe action si date range.

### 18. User Search Autocomplete
Configureaza autocomplete_fields pe toate FK-urile catre User. Adauga search_fields = ["email", "first_name", "last_name"] pe UserAdmin si seteaza get_search_results pentru cautare rapida.

### 19. User GDPR Actions
Adauga actiuni admin: export_user_data (Art. 20 DSGVO), anonymize_user (Art. 17), view_consent_history. export_user_data sa genereze JSON cu toate datele userului. anonymize_user sa stearga PII dar pastreze statisticile.

### 20. Last Login & Session Info
Afiseaza in UserAdmin: last_login, last_login_ip (din UserActivityLog), active_sessions_count (din django sessions), total_documents_count (annotate). Toate ca readonly_fields.

---

## Document Management (21-30)

### 21. DocumentAdmin cu Preview
Inregistreaza Document cu list_display: title, user_link, doc_type, display_status, sections_count, updated_at. user_link sa fie un link clickable catre UserAdmin change page.

### 22. Document Content Preview
Adauga readonly field display_content_preview care parseaza JSONField content si afiseaza un HTML summary: numar sectiuni completate, completeness percentage, limba detectata.

### 23. Document Filters
list_filter cu: ("doc_type", ChoicesDropdownFilter), ("created_at", RangeDateFilter), ("updated_at", RangeDateFilter), status filter custom (draft/complete bazat pe content completeness), ("user__subscription_plan", RelatedDropdownFilter).

### 24. Document Actions
Actions: duplicate_document, export_as_pdf, mark_as_template, soft_delete_selected, restore_deleted. soft_delete sa seteze deleted_at=now(), restore sa seteze deleted_at=None.

### 25. Soft Deleted Documents View
Creeaza un proxy model DeletedDocument cu custom manager filter(deleted_at__isnull=False). Inregistreaza-l separat in admin cu list_display care include deleted_at si restore action.

### 26. Template Admin
TemplateAdmin cu list_display: name, category, display_preview_thumbnail, is_premium, usage_count. category cu ChoicesDropdownFilter (klassisch, modern, kreativ, akademisch, it_tech, student).

### 27. Section Admin Inline
Creeaza SectionInline(unfold.admin.TabularInline) pentru Document. Afiseaza section_type, order, is_visible, content_length. Adauga drag-and-drop reordering cu Unfold sortable.

### 28. Document Statistics Annotations
In DocumentAdmin.get_queryset adauga annotate: sections_count=Count('sections'), content_size=Length('content'), days_since_update=Now()-F('updated_at'). Afiseaza in list_display.

### 29. Document Export Admin Action
Creeaza action export_documents_report care genereaza Excel (openpyxl) cu: document_id, user_email, doc_type, sections, created_at, updated_at, content_completeness_pct.

### 30. Document Version History
Creeaza model DocumentVersion(document, content_snapshot, version_number, created_at, created_by). Admin inline pe DocumentAdmin cu readonly, afisand diff-ul intre versiuni.

---

## Legal & Compliance (31-37)

### 31. Legal Documents Admin
Creeaza LegalDocumentAdmin pentru toate modelele din legal app: CookieConsent, GDPRRequest, PrivacyPolicy, TermsOfService, Impressum. Fiecare cu propriul fisier admin.

### 32. GDPR Request Dashboard
GDPRRequestAdmin cu list_display: user, request_type (export/delete), status (pending/processing/completed/rejected), created_at, completed_at. Actions: approve_request, reject_request, process_request.

### 33. Cookie Consent Tracking
CookieConsentAdmin read-only cu: user/session_id, consent_categories (necessary/statistics/marketing/external_media), ip_address, consented_at, revoked_at. Filters pe categorie si date.

### 34. Legal Document Versioning
Model LegalDocumentVersion(document_type, version, content_html, content_md, effective_date, is_active). Admin cu: version history, activate/deactivate actions, preview rendered HTML.

### 35. Compliance Dashboard Widget
Creeaza dashboard widget care afiseaza: total GDPR requests (pending/completed), cookie consent rate, users without consent, privacy policy acceptance rate. Afiseaza ca cards pe admin index.

### 36. Audit Trail Admin
Model AuditTrail(user, action, model_name, object_id, changes_json, ip_address, timestamp). ReadOnlyModelAdmin cu filtre pe action type, model, user, date range. Export CSV action.

### 37. Data Retention Policy Admin
Creeaza DataRetentionPolicy(model_name, retention_days, auto_delete, last_cleanup). Admin cu action run_cleanup care sterge records mai vechi decat retention_days. Celery task pentru auto-cleanup.

---

## Dashboards & Analytics (38-44)

### 38. Main Admin Dashboard
Override admin index cu Unfold dashboard. Randuri de widgets: [Useri totali, Useri online, Documente totale, Revenue luna curenta], [Grafic registrari ultimele 30 zile], [Grafic documente create/zi], [Top 5 template-uri folosite].

### 39. User Growth Chart
Dashboard widget cu Chart.js line chart: registrari noi pe zi ultimele 30 zile. Query: User.objects.filter(date_joined__gte=thirty_days_ago).extra(select={'day': 'date(date_joined)'}).values('day').annotate(count=Count('id')).

### 40. Document Analytics Widget
Widget cu: total documents, documents created today, documents created this week, average documents per user, most popular doc_type (pie chart), average sections per document.

### 41. Subscription Revenue Widget
Widget cu: active subscribers per plan (free/pro/enterprise), MRR (Monthly Recurring Revenue), conversion rate free→pro, churn rate last 30 days. Bar chart cu revenue per luna.

### 42. Real-time Stats Widget
HTMX widget care se auto-refresh la 30 secunde: useri online acum, documente in editare acum (Redis tracking), API requests/minut, average response time. Endpoint JSON dedicat.

### 43. Geographic Distribution Widget
Widget cu harta/tabel: useri per bundesland (din UserProfile), top 10 orase, distributie pe tara (daca exista). Horizontal bar chart cu Tailwind styling.

### 44. System Health Widget
Dashboard widget: database size, Redis memory usage, Celery queue length, failed tasks last 24h, disk usage, last backup timestamp. Status indicators: green/yellow/red.

---

## Support System (45-50)

### 45. Support Ticket Model
Creeaza app support/ cu model SupportTicket(user, subject, message, category, priority, status, assigned_to, created_at, updated_at, resolved_at). Categories: account, billing, technical, legal, feature_request. Priorities: low, medium, high, urgent.

### 46. Support Ticket Admin
SupportTicketAdmin cu list_display: ticket_number, user_link, subject_truncated, display_category, display_priority, display_status, assigned_to, created_at. Color-coded priority labels cu @display decorator.

### 47. Ticket Response Inline
Model TicketResponse(ticket, responder, message, is_internal_note, created_at). StackedInline pe SupportTicketAdmin. is_internal_note pentru note vizibile doar admin. Responder auto-set la request.user.

### 48. Ticket Assignment & Workflow
Actions: assign_to_me, assign_to_support_team, mark_in_progress, mark_resolved, mark_closed, reopen_ticket. Auto-email la user cand statusul se schimba. Celery task pentru email notification.

### 49. Support Dashboard Widget
Widget pe admin index: tickets deschise (per priority), average resolution time, tickets per category (pie chart), oldest unresolved ticket, support team workload (tickets per agent).

### 50. Canned Responses
Model CannedResponse(title, message_template, category, language, created_by). Admin cu: preview action, insert variables ({user_name}, {ticket_number}, {document_title}). Dropdown in ticket response form.
