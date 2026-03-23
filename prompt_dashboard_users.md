# User Dashboard Prompts — GetResume (Vue 3 Frontend)

> 50 prompturi pentru construirea dashboard-ului utilizatorilor (Mein Bereich)

---

## Layout & Navigation (1-10)

### 1. Dashboard Shell Layout
Construieste AppLayout.vue cu sidebar fix (240px) pe stanga, topbar cu user avatar + notifications + settings dropdown, si main content area cu router-view. Sidebar: logo GetResume, navigatie verticala cu iconite (Lucide), collapse pe mobile. Foloseste Tailwind CSS cu dark mode support.

### 2. Sidebar Navigation Items
Configureaza sidebar-ul cu 7 sectiuni: Ubersicht (dashboard home, icon: LayoutDashboard), Meine Lebensläufe (documents list, icon: FileText), Vorlagen (templates, icon: Layout), Bewerbungen (applications pipeline, icon: Send), Anschreiben (cover letters, icon: PenLine), Einstellungen (settings, icon: Settings), Hilfe & Support (help, icon: HelpCircle). Active state cu bg-primary/10 si text-primary.

### 3. Responsive Sidebar
Implementeaza sidebar responsive: pe desktop fix 240px, pe tablet overlay cu backdrop, pe mobile bottom navigation bar cu 5 iconite principale. Foloseste composable useSidebar() cu state in Pinia. Tranzitie slide cu Tailwind.

### 4. Topbar Component
Creeaza TopBar.vue cu: breadcrumbs (auto-generated din route meta), search bar (Cmd+K shortcut), notification bell cu badge count, user avatar dropdown (Profil, Einstellungen, Abo verwalten, Abmelden). Sticky top-0 cu backdrop-blur.

### 5. Breadcrumbs Auto-Generation
Creeaza composable useBreadcrumbs() care citeste route.matched si genereaza breadcrumbs din meta.breadcrumb. Format: Startseite > Meine Lebensläufe > Lebenslauf bearbeiten. Fiecare nivel e clickable cu router-link.

### 6. Command Palette (Cmd+K)
Implementeaza CommandPalette.vue modal cu search input care filtreaza: navigatie rapida (toate paginile), documente recente (ultimele 5), actiuni (Neuer Lebenslauf, Neue Bewerbung, Einstellungen). Keyboard navigation cu arrow keys + Enter.

### 7. Notification System
Creeaza NotificationStore (Pinia) cu: notifications array, unreadCount computed, markAsRead(), markAllAsRead(), fetchNotifications(). Notification types: document_exported, subscription_changed, support_reply, system_announcement. Toast notifications cu auto-dismiss.

### 8. Mobile Bottom Navigation
Creeaza MobileNav.vue vizibil doar sub md breakpoint. 5 tabs: Ubersicht, Dokumente, Neu+, Bewerbungen, Profil. Tab central "Neu+" cu FAB style (buton rotund primary). Badge pe Bewerbungen pentru unread.

### 9. Onboarding Tour
Implementeaza OnboardingTour.vue care apare la primul login. 5 pasi cu highlight pe UI: 1) Welcome message, 2) Sidebar navigation, 3) Create first CV button, 4) Template gallery, 5) Settings. Salveaza completion in UserProfile.onboarding_completed.

### 10. Error & Empty States
Creeaza componente reutilizabile: EmptyState.vue (icon, title, description, action button), ErrorState.vue (retry button), LoadingState.vue (skeleton). Foloseste-le consistent in toate view-urile dashboard.

---

## Dashboard Home / Ubersicht (11-20)

### 11. Dashboard Overview Page
Creeaza DashboardHome.vue cu grid layout: Welcome card (Willkommen zuruck, {name}!), Quick actions row, Stats cards row, Recent documents list, Activity timeline. Foloseste CSS Grid cu responsive columns.

### 12. Welcome Card cu Quick Actions
Card mare in top: "Willkommen zuruck, {first_name}!" cu subtitle "Du hast {doc_count} Lebensläufe erstellt". 3 quick action buttons: Neuen Lebenslauf erstellen (primary), Vorlage auswählen (secondary), Bewerbung starten (outline).

### 13. Stats Cards Row
4 stat cards cu iconite: Lebensläufe ({total_documents} count), Bewerbungen ({total_applications} count), Vorstellungsgespräche ({interviews_count}), Erfolgsquote ({success_rate}%). Fiecare card cu trend indicator (arrow up/down + percentage vs last month).

### 14. Recent Documents Grid
Afiseaza ultimele 4 documente ca cards: thumbnail preview (mini CV render), title, doc_type badge, last edited relative time (vor 2 Stunden), progress bar (completeness %). Click deschide editorul. "Alle anzeigen" link.

### 15. Activity Timeline
Componenta ActivityTimeline.vue cu ultimele 10 activitati: document_created, document_exported, application_sent, profile_updated, subscription_changed. Fiecare cu icon, text descriptiv in germana, relative timestamp. Vertical timeline cu dots si lines.

### 16. Subscription Status Card
Card care afiseaza: plan curent (Kostenlos/Pro/Enterprise), features disponibile, usage stats (documente create/limita), CTA "Jetzt upgraden" daca e pe free plan. Progress bar pentru usage limit.

### 17. Tips & Suggestions Widget
Card rotativ cu tips: "Vervollständige dein Profil für bessere Ergebnisse", "Nutze unsere ATS-optimierten Vorlagen", "Exportiere deinen Lebenslauf als PDF". Dismiss individual + "Nicht mehr anzeigen" option.

### 18. Document Completeness Widget
Daca userul are documente incomplete, afiseaza card: "Dein Lebenslauf ist zu {pct}% vollständig. Ergänze noch: {missing_sections}." Cu progress ring (SVG circle) si link direct la editarea sectiunii lipsa.

### 19. Upcoming Deadlines Widget
Daca userul are aplicatii cu deadline: card cu lista sortata: firma, pozitie, deadline date, days remaining (color coded: green >7d, yellow 3-7d, red <3d). Link la application details.

### 20. Dashboard Data Fetching
Creeaza composable useDashboardData() care face parallel fetch: documents summary, applications summary, activity feed, subscription status. Foloseste Promise.all cu loading states individuale. Cache 5 minute in Pinia.

---

## Document Management (21-30)

### 21. Documents List Page
Creeaza DocumentsListView.vue cu: header (title + "Neuer Lebenslauf" button), filter bar (doc_type, sort by, search), documents grid/list toggle. Grid: card view cu thumbnail. List: table view cu columns sortabile.

### 22. Document Card Component
DocumentCard.vue cu: mini preview (scaled down CV render in iframe/canvas), title editable inline, doc_type badge, last_edited relative time, completeness progress bar, 3-dot menu (Bearbeiten, Duplizieren, Exportieren, Löschen).

### 23. Document Filters & Sort
Filter bar cu: select doc_type (Alle, Lebenslauf, Anschreiben), sort dropdown (Zuletzt bearbeitet, Name A-Z, Erstellt am), search input cu debounce 300ms. Filters persist in URL query params. Clear all filters button.

### 24. Create New Document Flow
Modal/page: Step 1 - Alege doc_type (Lebenslauf/Anschreiben), Step 2 - Alege template din gallery cu preview, Step 3 - Enter title + optional import from existing. POST /api/v1/documents/ apoi redirect la editor.

### 25. Document Duplicate Action
Implementeaza duplicateDocument(id) in documents store. POST /api/v1/documents/{id}/duplicate/. Afiseaza toast "Lebenslauf wurde dupliziert" si redirect la noul document in editor.

### 26. Document Delete cu Confirmation
Dialog confirmare: "Möchtest du diesen Lebenslauf wirklich löschen?" cu document title bold, "Dieser Vorgang kann nicht rückgängig gemacht werden." (soft delete, dar userul nu stie). Buton "Löschen" rosu + "Abbrechen".

### 27. Document Export Options
Modal cu export options: PDF (standard), PDF (ATS-optimiert), DOCX, PNG (preview image). Fiecare cu icon si scurta descriere. Pro-only formats cu lock icon si upgrade CTA. Progress indicator pe download.

### 28. Bulk Document Actions
Checkbox pe fiecare document card. Cand cel putin 1 selectat, apare action bar fix in bottom: "{n} ausgewählt" + Exportieren, Duplizieren, Löschen buttons. Select all checkbox in header.

### 29. Document Import
Buton "Importieren" in documents list. Accepta: PDF (parse cu backend), JSON (GetResume format), LinkedIn PDF export. Upload cu drag-and-drop zone. Progress bar + preview inainte de save.

### 30. Empty Documents State
Cand userul nu are documente: ilustratie SVG, "Du hast noch keine Lebensläufe erstellt", "Erstelle deinen ersten professionellen Lebenslauf in wenigen Minuten.", CTA button "Jetzt starten" care deschide create flow.

---

## User Profile & Settings (31-40)

### 31. Settings Page Layout
SettingsView.vue cu tabs verticale pe stanga: Profil, Konto, Abonnement, Datenschutz, Benachrichtigungen. Content area pe dreapta. Mobile: tabs devin accordion sau horizontal scroll.

### 32. Profile Settings Form
Tab Profil: avatar upload (crop modal), Anrede (Herr/Frau/Divers select), Vorname, Nachname, Geburtsdatum (date picker), Telefon, Adresse (Strasse, PLZ, Stadt, Bundesland dropdown, Land). Auto-save cu 2s debounce.

### 33. Account Settings
Tab Konto: Email andern (cu verification), Passwort andern (current + new + confirm, min 10 chars), Zwei-Faktor-Authentifizierung toggle, Active sessions list cu "Alle abmelden" button, Konto löschen (danger zone cu double confirmation).

### 34. Subscription Management
Tab Abonnement: current plan card cu features, usage stats, next billing date. Plan comparison table (Kostenlos/Pro/Enterprise). Upgrade/Downgrade buttons. Rechnungen (invoices) list cu download PDF. Zahlungsmethode management.

### 35. Privacy Settings (DSGVO)
Tab Datenschutz: toggle switches pentru marketing_consent, newsletter_consent, analytics_consent. "Meine Daten exportieren" button (Art. 20), "Mein Konto und Daten löschen" button (Art. 17) cu double confirmation. Cookie preferences link.

### 36. Notification Preferences
Tab Benachrichtigungen: toggle grid cu categorii (Email/Push/In-App) x types (Bewerbungsupdates, Neue Vorlagen, Produkt-News, Sicherheitsbenachrichtigungen, Tipps & Tricks). Master toggles per canal.

### 37. Avatar Upload cu Crop
Creeaza AvatarUpload.vue: click to upload sau drag-and-drop, crop modal cu circular mask (foloseste vue-advanced-cropper), preview before save, max 2MB, accept jpg/png/webp. Upload la /api/v1/users/me/avatar/.

### 38. Change Email Flow
Implementeaza: input new email → POST /api/v1/users/me/change-email/ → backend trimite verification la noul email → user confirma → email updated. UI: step indicator, pending state "Bestätigungs-E-Mail gesendet an {new_email}".

### 39. Delete Account Flow
3-step confirmation: 1) Info page (ce se sterge, ce se pastreaza), 2) Type "LÖSCHEN" input confirmation, 3) Enter password. POST /api/v1/users/me/gdpr/delete/. Redirect la landing page cu toast "Dein Konto wurde gelöscht."

### 40. Two-Factor Authentication Setup
2FA setup flow: 1) Generate QR code (TOTP), 2) Scan cu authenticator app, 3) Enter verification code, 4) Show backup codes (downloadable). Toggle on/off cu password confirmation.

---

## Templates & Gallery (41-45)

### 41. Template Gallery Page
TemplatesView.vue cu: category tabs (Alle, Klassisch, Modern, Kreativ, Akademisch, IT & Tech, Student), grid cu template cards (preview image, name, popularity badge, Pro badge), hover preview enlargement.

### 42. Template Preview Modal
Click pe template: full-screen modal cu large preview (scrollable), template details sidebar (name, description, sections included, category, rating), "Vorlage verwenden" primary button, "Vorschau schließen" secondary.

### 43. Template Card Component
TemplateCard.vue: aspect ratio 210:297 (A4), lazy loaded preview image, title overlay bottom, category badge top-left, Pro/Kostenlos badge top-right, hover: slight scale + shadow + "Vorschau" overlay button.

### 44. Template Filtering & Search
Filter bar: category chips (horizontal scroll), search by name, sort (Beliebteste, Neueste, Name A-Z), toggle "Nur kostenlose" switch. Results count "12 Vorlagen gefunden". Animated filter transitions.

### 45. Template Selection in Document Creation
Cand userul creeaza document nou: template gallery inline cu mini cards, selected template highlighted cu border-primary, "Ohne Vorlage starten" option, preview panel pe dreapta (desktop) sau modal (mobile).

---

## Applications Pipeline (46-50)

### 46. Applications Kanban Board
BewerbungenView.vue cu Kanban columns: Gespeichert, Beworben, Eingeladen, Vorstellungsgespräch, Angebot, Abgelehnt. Drag-and-drop cards intre coloane. Card: firma logo, position title, datum, priority dot.

### 47. Application Card Component
ApplicationCard.vue: firma name + logo (auto-fetch), position title, location, applied date, source (LinkedIn/StepStone/Indeed badge), attached document link, notes count badge, priority indicator (color dot).

### 48. Add Application Modal
Modal cu form: Firma (autocomplete), Position, Link zur Stellenanzeige (URL), Ansprechpartner, Bewerbungsdatum, Priorität (Niedrig/Mittel/Hoch), Notizen textarea, Dokument auswählen (dropdown din user docs). Quick add vs detailed form toggle.

### 49. Application Detail Page
Full page: header cu firma + position + status badge, timeline (toate status changes cu date), attached documents section, notes/comments section cu add note, next steps / reminders, related cover letter link.

### 50. Application Analytics
Stats section in Bewerbungen page: total bewerbungen this month, response rate %, average time to response (days), funnel visualization (Beworben → Eingeladen → Gespräch → Angebot), success rate per source (chart).
