# Dashboard HTMX Templates Reference

## Overview

All dashboard templates use Django template language with HTMX for dynamic interactions and Alpine.js for client-side state management. The design follows a sidebar layout pattern consistent with German SaaS conventions.

---

## 1. dashboard_base.html (Sidebar Layout)

```html
{# dashboard/templates/dashboard/dashboard_base.html #}

{% load static i18n %}
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block page_title %}Dashboard{% endblock %} | Lebenslauf-Builder</title>

    {# Preconnect for performance #}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://cdn.jsdelivr.net">

    {# CSS #}
    <link rel="stylesheet" href="{% static 'css/dashboard.css' %}">

    {# HTMX #}
    <script src="https://unpkg.com/htmx.org@1.9.12" defer></script>

    {# Alpine.js #}
    <script src="https://cdn.jsdelivr.net/npm/alpinejs@3.14/dist/cdn.min.js" defer></script>

    {# HTMX configuration #}
    <meta name="htmx-config" content='{"defaultSwapStyle":"innerHTML","globalViewTransitions":true}'>

    {% block extra_head %}{% endblock %}
</head>
<body
    x-data="{ sidebarOpen: false }"
    class="dashboard-body"
    hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
>
    {# === Toast notification container === #}
    <div id="toast-container"
         class="toast-container position-fixed top-0 end-0 p-3"
         style="z-index: 1090;">
    </div>

    {# === Mobile Top Bar === #}
    <header class="dashboard-topbar d-lg-none">
        <div class="d-flex align-items-center justify-content-between px-3 py-2">
            <button
                @click="sidebarOpen = !sidebarOpen"
                class="btn btn-link text-dark p-0"
                aria-label="Menue oeffnen"
            >
                {# Hamburger icon #}
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                     fill="currentColor" viewBox="0 0 16 16">
                    <path fill-rule="evenodd"
                          d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"/>
                </svg>
            </button>

            <a href="{% url 'dashboard:home' %}" class="dashboard-topbar-brand">
                <img src="{% static 'images/logo-small.svg' %}" alt="Lebenslauf-Builder" height="28">
            </a>

            <div class="dropdown">
                <button class="btn btn-link p-0" data-bs-toggle="dropdown" aria-label="Benutzermenue">
                    <div class="avatar avatar-sm">
                        {% if user.profile.photo %}
                            <img src="{{ user.profile.photo.url }}" alt="{{ user.get_full_name }}">
                        {% else %}
                            <span class="avatar-initials">{{ user.first_name|first }}{{ user.last_name|first }}</span>
                        {% endif %}
                    </div>
                </button>
                {% include "dashboard/partials/user_dropdown.html" %}
            </div>
        </div>
    </header>

    <div class="dashboard-layout">
        {# === Sidebar === #}
        <aside
            class="dashboard-sidebar"
            :class="{ 'sidebar-open': sidebarOpen }"
            @click.outside="sidebarOpen = false"
        >
            {# Logo #}
            <div class="sidebar-brand d-none d-lg-flex">
                <a href="{% url 'dashboard:home' %}">
                    <img src="{% static 'images/logo.svg' %}" alt="Lebenslauf-Builder" height="32">
                </a>
            </div>

            {# Navigation #}
            <nav class="sidebar-nav">
                <ul class="sidebar-menu">
                    {# Dashboard Home #}
                    <li class="sidebar-item {% if active_nav == 'home' %}active{% endif %}">
                        <a href="{% url 'dashboard:home' %}" class="sidebar-link">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M8.354 1.146a.5.5 0 0 0-.708 0l-6 6A.5.5 0 0 0 1.5 7.5v7a.5.5 0 0 0 .5.5h4.5a.5.5 0 0 0 .5-.5v-4h2v4a.5.5 0 0 0 .5.5H14a.5.5 0 0 0 .5-.5v-7a.5.5 0 0 0-.146-.354L13 5.793V2.5a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1.293L8.354 1.146z"/>
                            </svg>
                            <span>Dashboard</span>
                        </a>
                    </li>

                    {# Meine Dokumente #}
                    <li class="sidebar-item {% if active_nav == 'dokumente' %}active{% endif %}">
                        <a href="{% url 'dashboard:document_list' %}" class="sidebar-link">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M5.5 7a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1h-5zM5 9.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5z"/>
                                <path d="M9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.5L9.5 0z"/>
                            </svg>
                            <span>Meine Dokumente</span>
                            {% if document_counts.total %}
                                <span class="sidebar-badge">{{ document_counts.total }}</span>
                            {% endif %}
                        </a>
                    </li>

                    {# Bewerbungsmappe #}
                    <li class="sidebar-item {% if active_nav == 'bewerbungsmappe' %}active{% endif %}">
                        <a href="{% url 'dashboard:bewerbungsmappe' %}" class="sidebar-link">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M9.828 3h3.982a2 2 0 0 1 1.992 2.181l-.637 7A2 2 0 0 1 13.174 14H2.825a2 2 0 0 1-1.991-1.819l-.637-7a1.99 1.99 0 0 1 .342-1.31L.5 3a2 2 0 0 1 2-2h3.672a2 2 0 0 1 1.414.586l.828.828A2 2 0 0 0 9.828 3z"/>
                            </svg>
                            <span>Bewerbungsmappe</span>
                        </a>
                    </li>

                    {# Neues Dokument #}
                    <li class="sidebar-item sidebar-item-cta">
                        <a href="{% url 'editor:new' %}" class="sidebar-link sidebar-link-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
                            </svg>
                            <span>Neues Dokument</span>
                        </a>
                    </li>

                    <li class="sidebar-divider"></li>

                    {# Konto #}
                    <li class="sidebar-item {% if active_nav == 'konto' %}active{% endif %}">
                        <a href="{% url 'dashboard:konto' %}" class="sidebar-link">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4z"/>
                            </svg>
                            <span>Konto</span>
                        </a>
                    </li>

                    {# Abo & Zahlung #}
                    <li class="sidebar-item {% if active_nav == 'abo' %}active{% endif %}">
                        <a href="{% url 'dashboard:abo_zahlung' %}" class="sidebar-link">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4z"/>
                            </svg>
                            <span>Abo & Zahlung</span>
                        </a>
                    </li>

                    {# Datenschutz #}
                    <li class="sidebar-item {% if active_nav == 'datenschutz' %}active{% endif %}">
                        <a href="{% url 'dashboard:datenschutz' %}" class="sidebar-link">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M5.338 1.59a61.44 61.44 0 0 0-2.837.856.481.481 0 0 0-.328.39c-.554 4.157.726 7.19 2.253 9.188a10.725 10.725 0 0 0 2.287 2.233c.346.244.652.42.893.533.12.057.218.095.293.118a.55.55 0 0 0 .101.025.615.615 0 0 0 .1-.025c.076-.023.174-.061.294-.118.24-.113.547-.29.893-.533a10.726 10.726 0 0 0 2.287-2.233c1.527-1.997 2.807-5.031 2.253-9.188a.48.48 0 0 0-.328-.39c-.651-.213-1.75-.56-2.837-.855C9.552 1.29 8.531 1.067 8 1.067c-.53 0-1.552.223-2.662.524zM5.072.56C6.157.265 7.31 0 8 0s1.843.265 2.928.56c1.11.3 2.229.655 2.887.87a1.54 1.54 0 0 1 1.044 1.262c.596 4.477-.787 7.795-2.465 9.99a11.775 11.775 0 0 1-2.517 2.453 7.159 7.159 0 0 1-1.048.625c-.28.132-.581.24-.829.24s-.548-.108-.829-.24a7.158 7.158 0 0 1-1.048-.625 11.777 11.777 0 0 1-2.517-2.453C1.928 10.487.545 7.169 1.141 2.692A1.54 1.54 0 0 1 2.185 1.43 62.456 62.456 0 0 1 5.072.56z"/>
                            </svg>
                            <span>Datenschutz</span>
                        </a>
                    </li>

                    {% if user.is_staff %}
                    <li class="sidebar-divider"></li>

                    <li class="sidebar-section-title">Administration</li>

                    {# Admin Dashboard #}
                    <li class="sidebar-item {% if active_nav == 'admin_dashboard' %}active{% endif %}">
                        <a href="{% url 'dashboard:admin_dashboard' %}" class="sidebar-link">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M4 11H2v3h2v-3zm5-4H7v7h2V7zm5-5h-2v12h2V2zm-2-1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1h-2zM6 7a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7z"/>
                            </svg>
                            <span>Admin Dashboard</span>
                        </a>
                    </li>

                    {# Benutzerverwaltung #}
                    <li class="sidebar-item {% if active_nav == 'admin_users' %}active{% endif %}">
                        <a href="{% url 'dashboard:admin_users' %}" class="sidebar-link">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022zM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"/>
                                <path fill-rule="evenodd" d="M5.216 14A2.238 2.238 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.325 6.325 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1h4.216z"/>
                                <path d="M4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/>
                            </svg>
                            <span>Benutzer</span>
                        </a>
                    </li>

                    {# DSGVO Panel #}
                    <li class="sidebar-item {% if active_nav == 'admin_gdpr' %}active{% endif %}">
                        <a href="{% url 'dashboard:admin_gdpr' %}" class="sidebar-link">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z"/>
                            </svg>
                            <span>DSGVO</span>
                            {% if pending_gdpr_requests %}
                                <span class="sidebar-badge badge-warning">{{ pending_gdpr_requests }}</span>
                            {% endif %}
                        </a>
                    </li>
                    {% endif %}
                </ul>
            </nav>

            {# Sidebar Footer #}
            <div class="sidebar-footer d-none d-lg-block">
                <div class="sidebar-user-info">
                    <div class="avatar avatar-sm">
                        {% if user.profile.photo %}
                            <img src="{{ user.profile.photo.url }}" alt="">
                        {% else %}
                            <span class="avatar-initials">{{ user.first_name|first }}{{ user.last_name|first }}</span>
                        {% endif %}
                    </div>
                    <div class="sidebar-user-details">
                        <span class="sidebar-user-name">{{ user.get_full_name|default:user.email }}</span>
                        <span class="sidebar-user-plan">
                            {% if subscription %}{{ subscription.plan.display_name }}{% else %}Kostenlos{% endif %}
                        </span>
                    </div>
                </div>
            </div>
        </aside>

        {# === Mobile Overlay === #}
        <div
            class="sidebar-overlay d-lg-none"
            x-show="sidebarOpen"
            x-transition:enter="transition-opacity ease-out duration-200"
            x-transition:enter-start="opacity-0"
            x-transition:enter-end="opacity-100"
            x-transition:leave="transition-opacity ease-in duration-150"
            x-transition:leave-start="opacity-100"
            x-transition:leave-end="opacity-0"
            @click="sidebarOpen = false"
        ></div>

        {# === Main Content === #}
        <main class="dashboard-content">
            {# Breadcrumb #}
            <div class="dashboard-breadcrumb">
                {% block breadcrumb %}
                <nav aria-label="Breadcrumb">
                    <ol class="breadcrumb mb-0">
                        <li class="breadcrumb-item">
                            <a href="{% url 'dashboard:home' %}">Dashboard</a>
                        </li>
                        {% block breadcrumb_items %}{% endblock %}
                    </ol>
                </nav>
                {% endblock %}
            </div>

            {# Page Header #}
            <div class="dashboard-page-header">
                <h1 class="h4">{% block content_title %}{{ page_title }}{% endblock %}</h1>
                {% block page_actions %}{% endblock %}
            </div>

            {# Messages / Alerts #}
            {% if messages %}
            <div class="dashboard-messages">
                {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Schliessen"></button>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {# Page Content #}
            <div class="dashboard-page-content">
                {% block dashboard_content %}{% endblock %}
            </div>
        </main>
    </div>

    {# === HTMX global event listeners === #}
    <script>
        // Show toast on HTMX events
        document.body.addEventListener("documentDeleted", function(evt) {
            const detail = evt.detail;
            showToast("Dokument geloescht", `"${detail.title}" wurde geloescht.`, "success");

            // Remove card with animation
            const card = document.querySelector(`[data-document-id="${detail.id}"]`);
            if (card) {
                card.style.transition = "opacity 0.3s, transform 0.3s";
                card.style.opacity = "0";
                card.style.transform = "scale(0.95)";
                setTimeout(() => card.remove(), 300);
            }
        });

        document.body.addEventListener("documentDuplicated", function(evt) {
            const detail = evt.detail;
            showToast("Dokument dupliziert", `"${detail.title}" wurde erstellt.`, "success");
        });

        document.body.addEventListener("profileUpdated", function() {
            showToast("Gespeichert", "Profil wurde aktualisiert.", "success");
        });

        // Toast helper
        function showToast(title, message, type) {
            const container = document.getElementById("toast-container");
            const id = "toast-" + Date.now();
            const bgClass = type === "success" ? "bg-success" : type === "error" ? "bg-danger" : "bg-info";

            container.insertAdjacentHTML("beforeend", `
                <div id="${id}" class="toast ${bgClass} text-white" role="alert" aria-live="assertive">
                    <div class="toast-header">
                        <strong class="me-auto">${title}</strong>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">${message}</div>
                </div>
            `);

            const toastEl = document.getElementById(id);
            const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
            toast.show();
            toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
        }

        // HTMX loading indicator
        document.body.addEventListener("htmx:beforeRequest", function(evt) {
            evt.target.classList.add("htmx-loading");
        });
        document.body.addEventListener("htmx:afterRequest", function(evt) {
            evt.target.classList.remove("htmx-loading");
        });
    </script>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 2. meine_dokumente.html (Grid View with Alpine.js Toggle)

```html
{# dashboard/templates/dashboard/meine_dokumente.html #}

{% extends "dashboard/dashboard_base.html" %}
{% load static %}

{% block breadcrumb_items %}
<li class="breadcrumb-item active">Meine Dokumente</li>
{% endblock %}

{% block content_title %}Meine Dokumente{% endblock %}

{% block page_actions %}
<a href="{% url 'editor:new' %}" class="btn btn-primary">
    + Neues Dokument
</a>
{% endblock %}

{% block dashboard_content %}
<div x-data="{
    viewMode: '{{ view_mode }}',
    toggleView(mode) {
        this.viewMode = mode;
        // Persist via HTMX
        htmx.ajax('GET', '{% url 'dashboard:document_list' %}?view=' + mode, {
            target: '#document-container',
            swap: 'none'
        });
    }
}">
    {# === Filter Bar === #}
    <div class="card mb-4">
        <div class="card-body py-2">
            <div class="d-flex flex-wrap align-items-center gap-3">
                {# Search #}
                <div class="flex-grow-1" style="min-width: 200px; max-width: 400px;">
                    <input
                        type="search"
                        name="q"
                        value="{{ search_query }}"
                        placeholder="Dokumente suchen..."
                        class="form-control form-control-sm"
                        hx-get="{% url 'dashboard:document_list' %}"
                        hx-target="#document-container"
                        hx-trigger="input changed delay:300ms, search"
                        hx-include="[name='type'], [name='sort']"
                        hx-push-url="true"
                    >
                </div>

                {# Type Filter #}
                <select
                    name="type"
                    class="form-select form-select-sm"
                    style="width: auto;"
                    hx-get="{% url 'dashboard:document_list' %}"
                    hx-target="#document-container"
                    hx-trigger="change"
                    hx-include="[name='q'], [name='sort']"
                    hx-push-url="true"
                >
                    <option value="">Alle Typen</option>
                    <option value="lebenslauf" {% if active_type == "lebenslauf" %}selected{% endif %}>Lebenslauf</option>
                    <option value="anschreiben" {% if active_type == "anschreiben" %}selected{% endif %}>Anschreiben</option>
                    <option value="deckblatt" {% if active_type == "deckblatt" %}selected{% endif %}>Deckblatt</option>
                </select>

                {# Sort #}
                <select
                    name="sort"
                    class="form-select form-select-sm"
                    style="width: auto;"
                    hx-get="{% url 'dashboard:document_list' %}"
                    hx-target="#document-container"
                    hx-trigger="change"
                    hx-include="[name='q'], [name='type']"
                    hx-push-url="true"
                >
                    <option value="-updated" {% if active_sort == "-updated" %}selected{% endif %}>Zuletzt bearbeitet</option>
                    <option value="-created" {% if active_sort == "-created" %}selected{% endif %}>Neueste zuerst</option>
                    <option value="title" {% if active_sort == "title" %}selected{% endif %}>Name A-Z</option>
                    <option value="-title" {% if active_sort == "-title" %}selected{% endif %}>Name Z-A</option>
                </select>

                {# View Toggle #}
                <div class="btn-group btn-group-sm" role="group" aria-label="Ansicht">
                    <button
                        type="button"
                        class="btn"
                        :class="viewMode === 'grid' ? 'btn-primary' : 'btn-outline-secondary'"
                        @click="toggleView('grid')"
                        title="Kachelansicht"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                             fill="currentColor" viewBox="0 0 16 16">
                            <path d="M1 2.5A1.5 1.5 0 0 1 2.5 1h3A1.5 1.5 0 0 1 7 2.5v3A1.5 1.5 0 0 1 5.5 7h-3A1.5 1.5 0 0 1 1 5.5v-3zm8 0A1.5 1.5 0 0 1 10.5 1h3A1.5 1.5 0 0 1 15 2.5v3A1.5 1.5 0 0 1 13.5 7h-3A1.5 1.5 0 0 1 9 5.5v-3zm-8 8A1.5 1.5 0 0 1 2.5 9h3A1.5 1.5 0 0 1 7 10.5v3A1.5 1.5 0 0 1 5.5 15h-3A1.5 1.5 0 0 1 1 13.5v-3zm8 0A1.5 1.5 0 0 1 10.5 9h3a1.5 1.5 0 0 1 1.5 1.5v3a1.5 1.5 0 0 1-1.5 1.5h-3A1.5 1.5 0 0 1 9 13.5v-3z"/>
                        </svg>
                    </button>
                    <button
                        type="button"
                        class="btn"
                        :class="viewMode === 'list' ? 'btn-primary' : 'btn-outline-secondary'"
                        @click="toggleView('list')"
                        title="Listenansicht"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                             fill="currentColor" viewBox="0 0 16 16">
                            <path fill-rule="evenodd" d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>

    {# === Document Container === #}
    <div id="document-container">
        {% include "dashboard/partials/document_grid.html" %}
    </div>
</div>
{% endblock %}
```

### Document Grid Partial

```html
{# dashboard/templates/dashboard/partials/document_grid.html #}

{% load static %}

{% if documents %}
<div class="document-grid"
     :class="{ 'document-grid-list': viewMode === 'list' }">
    {% for document in documents %}
        {% include "dashboard/partials/document_card.html" %}
    {% endfor %}
</div>

{# Infinite scroll trigger #}
{% if page_obj.has_next %}
<div
    hx-get="{% url 'dashboard:document_list' %}?page={{ page_obj.next_page_number }}{% if active_type %}&type={{ active_type }}{% endif %}{% if active_sort %}&sort={{ active_sort }}{% endif %}{% if search_query %}&q={{ search_query }}{% endif %}"
    hx-trigger="intersect once threshold:0.1"
    hx-target="#document-container .document-grid"
    hx-swap="beforeend"
    class="text-center py-4"
>
    <div class="spinner-border spinner-border-sm text-primary" role="status">
        <span class="visually-hidden">Wird geladen...</span>
    </div>
</div>
{% endif %}

{% else %}
<div class="text-center py-5">
    <div class="mb-3">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"
             fill="currentColor" class="text-muted" viewBox="0 0 16 16">
            <path d="M9.293 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.707A1 1 0 0 0 13.707 4L10 .293A1 1 0 0 0 9.293 0z"/>
        </svg>
    </div>
    <h3 class="h5 text-muted">Noch keine Dokumente</h3>
    <p class="text-muted mb-4">Erstellen Sie Ihren ersten Lebenslauf in wenigen Minuten.</p>
    <a href="{% url 'editor:new' %}" class="btn btn-primary">
        + Neues Dokument erstellen
    </a>
</div>
{% endif %}
```

---

## 3. document_card.html (HTMX Partial)

```html
{# dashboard/templates/dashboard/partials/document_card.html #}

{% load static humanize %}

<div
    class="document-card"
    data-document-id="{{ document.id }}"
    id="doc-card-{{ document.id }}"
    x-data="{ showDropdown: false, renaming: false, newTitle: '{{ document.title|escapejs }}' }"
>
    {# Thumbnail #}
    <div class="document-card-thumbnail">
        <a href="{% url 'editor:edit' document.id %}">
            {% if document.thumbnail %}
                <img src="{{ document.thumbnail.url }}"
                     alt="{{ document.title }}"
                     loading="lazy">
            {% else %}
                <div class="document-card-placeholder">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48"
                         fill="currentColor" viewBox="0 0 16 16">
                        <path d="M9.293 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.707A1 1 0 0 0 13.707 4L10 .293A1 1 0 0 0 9.293 0z"/>
                    </svg>
                </div>
            {% endif %}
        </a>

        {# Type Badge #}
        <span class="document-card-badge badge-{{ document.document_type }}">
            {% if document.document_type == "lebenslauf" %}
                Lebenslauf
            {% elif document.document_type == "anschreiben" %}
                Anschreiben
            {% elif document.document_type == "deckblatt" %}
                Deckblatt
            {% endif %}
        </span>

        {# Favorite indicator #}
        {% if document.is_favorite %}
        <span class="document-card-favorite" title="Favorit">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                 fill="#f59e0b" viewBox="0 0 16 16">
                <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>
            </svg>
        </span>
        {% endif %}
    </div>

    {# Card Body #}
    <div class="document-card-body">
        {# Title (with inline rename) #}
        <div class="document-card-title">
            <template x-if="!renaming">
                <a href="{% url 'editor:edit' document.id %}"
                   class="text-decoration-none text-dark"
                   @dblclick.prevent="renaming = true">
                    {{ document.title|truncatechars:40 }}
                </a>
            </template>
            <template x-if="renaming">
                <form
                    hx-post="{% url 'dashboard:document_action' document.id %}"
                    hx-target="#doc-card-{{ document.id }}"
                    hx-swap="outerHTML"
                    @htmx:after-request="renaming = false"
                >
                    <input type="hidden" name="action" value="rename">
                    <input
                        type="text"
                        name="title"
                        x-model="newTitle"
                        class="form-control form-control-sm"
                        @keydown.escape="renaming = false"
                        x-init="$nextTick(() => $el.focus())"
                    >
                </form>
            </template>
        </div>

        {# Meta info #}
        <div class="document-card-meta">
            <span class="text-muted small">
                {{ document.updated_at|naturaltime }}
            </span>
            {% if document.template %}
            <span class="text-muted small">
                &middot; {{ document.template.name }}
            </span>
            {% endif %}
        </div>
    </div>

    {# Dropdown Actions #}
    <div class="document-card-actions" x-data="{ open: false }">
        <button
            class="btn btn-sm btn-ghost"
            @click="open = !open"
            @click.outside="open = false"
            aria-label="Aktionen"
        >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                 fill="currentColor" viewBox="0 0 16 16">
                <path d="M9.5 13a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
            </svg>
        </button>

        <div class="dropdown-menu dropdown-menu-end" x-show="open" x-transition>
            {# Edit #}
            <a class="dropdown-item" href="{% url 'editor:edit' document.id %}">
                Bearbeiten
            </a>

            {# Rename #}
            <button class="dropdown-item" @click="renaming = true; open = false">
                Umbenennen
            </button>

            {# Favorite toggle #}
            <button
                class="dropdown-item"
                hx-post="{% url 'dashboard:document_action' document.id %}"
                hx-vals='{"action": "favorite"}'
                hx-target="#doc-card-{{ document.id }}"
                hx-swap="outerHTML"
            >
                {% if document.is_favorite %}Favorit entfernen{% else %}Als Favorit markieren{% endif %}
            </button>

            {# Duplicate #}
            <button
                class="dropdown-item"
                hx-post="{% url 'dashboard:document_action' document.id %}"
                hx-vals='{"action": "duplicate"}'
                hx-target="#document-container .document-grid"
                hx-swap="afterbegin"
            >
                Duplizieren
            </button>

            <div class="dropdown-divider"></div>

            {# Delete (with confirmation) #}
            <button
                class="dropdown-item text-danger"
                hx-post="{% url 'dashboard:document_action' document.id %}"
                hx-vals='{"action": "delete"}'
                hx-confirm="Moechten Sie &quot;{{ document.title }}&quot; wirklich loeschen?"
                hx-target="#doc-card-{{ document.id }}"
                hx-swap="outerHTML"
            >
                Loeschen
            </button>
        </div>
    </div>
</div>
```

---

## 4. konto.html (Profile Form with HTMX Inline Saves)

```html
{# dashboard/templates/dashboard/konto.html #}

{% extends "dashboard/dashboard_base.html" %}
{% load static %}

{% block breadcrumb_items %}
<li class="breadcrumb-item active">Konto</li>
{% endblock %}

{% block content_title %}Kontoeinstellungen{% endblock %}

{% block dashboard_content %}
<div class="row g-4">
    {# === Persoenliche Daten === #}
    <div class="col-lg-8">
        <div class="card" id="profile-section">
            <div class="card-header">
                <h2 class="h6 mb-0">Persoenliche Daten</h2>
            </div>
            <div class="card-body">
                <form
                    hx-post="{% url 'dashboard:konto_profile' %}"
                    hx-target="#profile-section .card-body"
                    hx-swap="innerHTML"
                >
                    {% csrf_token %}
                    {% include "dashboard/partials/konto_profile_form.html" %}
                </form>
            </div>
        </div>
    </div>

    {# === Profilfoto === #}
    <div class="col-lg-4">
        <div class="card">
            <div class="card-header">
                <h2 class="h6 mb-0">Profilfoto</h2>
            </div>
            <div class="card-body text-center">
                <div class="avatar avatar-xl mx-auto mb-3">
                    {% if user.profile.photo %}
                        <img src="{{ user.profile.photo.url }}" alt="{{ user.get_full_name }}" id="avatar-preview">
                    {% else %}
                        <span class="avatar-initials" id="avatar-preview">
                            {{ user.first_name|first }}{{ user.last_name|first }}
                        </span>
                    {% endif %}
                </div>
                <form
                    hx-post="{% url 'dashboard:konto_profile' %}"
                    hx-target="#profile-section .card-body"
                    hx-encoding="multipart/form-data"
                >
                    {% csrf_token %}
                    <input type="file" name="photo" id="photo-input"
                           accept="image/*" class="d-none"
                           onchange="this.form.requestSubmit()">
                    <button type="button" class="btn btn-outline-primary btn-sm"
                            onclick="document.getElementById('photo-input').click()">
                        Foto aendern
                    </button>
                </form>
            </div>
        </div>
    </div>

    {# === Passwort aendern === #}
    <div class="col-lg-8">
        <div class="card" id="password-section">
            <div class="card-header">
                <h2 class="h6 mb-0">Passwort aendern</h2>
            </div>
            <div class="card-body">
                <form
                    hx-post="{% url 'dashboard:konto_password' %}"
                    hx-target="#password-section .card-body"
                    hx-swap="innerHTML"
                >
                    {% csrf_token %}
                    {% include "dashboard/partials/konto_password_form.html" %}
                </form>
            </div>
        </div>
    </div>

    {# === Rechnungsadresse === #}
    <div class="col-lg-8">
        <div class="card" id="address-section">
            <div class="card-header">
                <h2 class="h6 mb-0">Rechnungsadresse</h2>
            </div>
            <div class="card-body">
                <form
                    hx-post="{% url 'dashboard:konto_address' %}"
                    hx-target="#address-section .card-body"
                    hx-swap="innerHTML"
                >
                    {% csrf_token %}
                    {% include "dashboard/partials/konto_address_form.html" %}
                </form>
            </div>
        </div>
    </div>

    {# === Benachrichtigungen === #}
    <div class="col-lg-8">
        <div class="card" id="notification-section">
            <div class="card-header">
                <h2 class="h6 mb-0">Benachrichtigungen</h2>
            </div>
            <div class="card-body">
                <form
                    hx-post="{% url 'dashboard:konto_notifications' %}"
                    hx-target="#notification-section .card-body"
                    hx-swap="innerHTML"
                >
                    {% csrf_token %}
                    {% include "dashboard/partials/konto_notification_form.html" %}
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 5. abo_zahlung.html (Current Plan Card, Payment History)

```html
{# dashboard/templates/dashboard/abo_zahlung.html #}

{% extends "dashboard/dashboard_base.html" %}
{% load static humanize %}

{% block breadcrumb_items %}
<li class="breadcrumb-item active">Abo & Zahlung</li>
{% endblock %}

{% block content_title %}Abo & Zahlung{% endblock %}

{% block dashboard_content %}
<div class="row g-4">

    {# === Current Plan Card === #}
    <div class="col-lg-8" id="abo-status-section">
        {% include "dashboard/partials/abo_status_card.html" %}
    </div>

    {# === Payment Method === #}
    <div class="col-lg-4">
        <div class="card">
            <div class="card-header">
                <h2 class="h6 mb-0">Zahlungsmethode</h2>
            </div>
            <div class="card-body">
                {% if payment_method %}
                <div class="d-flex align-items-center gap-3">
                    <div class="payment-icon">
                        {% if payment_method.brand == "Visa" %}
                            <img src="{% static 'images/cards/visa.svg' %}" alt="Visa" height="24">
                        {% elif payment_method.brand == "Mastercard" %}
                            <img src="{% static 'images/cards/mastercard.svg' %}" alt="Mastercard" height="24">
                        {% else %}
                            <span class="badge bg-secondary">{{ payment_method.brand }}</span>
                        {% endif %}
                    </div>
                    <div>
                        <div class="fw-medium">{{ payment_method.brand }} **** {{ payment_method.last4 }}</div>
                        {% if payment_method.type == "card" %}
                        <div class="text-muted small">Gueltig bis {{ payment_method.exp_month }}/{{ payment_method.exp_year }}</div>
                        {% endif %}
                    </div>
                </div>
                <hr>
                <a href="#" class="btn btn-outline-secondary btn-sm w-100"
                   hx-post="{% url 'payments:update_payment_method' %}"
                   hx-target="this">
                    Zahlungsmethode aendern
                </a>
                {% else %}
                <p class="text-muted mb-0">Keine Zahlungsmethode hinterlegt.</p>
                {% endif %}
            </div>
        </div>
    </div>

    {# === Available Plans === #}
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h2 class="h6 mb-0">Verfuegbare Plaene</h2>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    {% for plan in available_plans %}
                    <div class="col-md-4">
                        <div class="plan-card {% if subscription and subscription.plan_id == plan.id %}plan-card-active{% endif %}">
                            <h3 class="h6">{{ plan.display_name }}</h3>
                            <div class="plan-price">
                                <span class="plan-price-amount">{{ plan.price_monthly|floatformat:2 }} &euro;</span>
                                <span class="plan-price-period">/ Monat</span>
                            </div>
                            <div class="plan-price-note text-muted small">
                                inkl. 19% MwSt.
                                (netto: {{ plan.price_monthly_net|floatformat:2 }} &euro;)
                            </div>
                            <ul class="plan-features mt-3">
                                {% for feature in plan.features %}
                                <li>{{ feature }}</li>
                                {% endfor %}
                            </ul>
                            {% if subscription and subscription.plan_id == plan.id %}
                                <button class="btn btn-outline-primary btn-sm w-100" disabled>
                                    Aktueller Plan
                                </button>
                            {% else %}
                                <button
                                    class="btn btn-primary btn-sm w-100"
                                    hx-post="{% url 'dashboard:abo_upgrade' %}"
                                    hx-vals='{"plan_id": "{{ plan.id }}"}'
                                >
                                    {% if subscription and plan.price_monthly > subscription.plan.price_monthly %}
                                        Upgrade
                                    {% else %}
                                        Auswaeahlen
                                    {% endif %}
                                </button>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    {# === Payment History (Rechnungen) === #}
    <div class="col-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h2 class="h6 mb-0">Rechnungen</h2>
            </div>
            <div class="card-body p-0">
                {% if invoices %}
                <div class="table-responsive">
                    <table class="table table-hover mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Rechnungsnr.</th>
                                <th>Datum</th>
                                <th>Betrag</th>
                                <th>Status</th>
                                <th>PDF</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for invoice in invoices %}
                            <tr>
                                <td><code>{{ invoice.rechnungsnummer }}</code></td>
                                <td>{{ invoice.rechnungsdatum|date:"d.m.Y" }}</td>
                                <td>{{ invoice.bruttobetrag|floatformat:2 }} &euro;</td>
                                <td>
                                    <span class="badge bg-{% if invoice.status == 'paid' %}success{% elif invoice.status == 'sent' %}info{% else %}secondary{% endif %}">
                                        {{ invoice.get_status_display }}
                                    </span>
                                </td>
                                <td>
                                    {% if invoice.pdf_file %}
                                    <a href="{% url 'invoices:invoice_download' invoice.rechnungsnummer %}"
                                       class="btn btn-sm btn-outline-primary">
                                        PDF
                                    </a>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="text-center py-4 text-muted">
                    Noch keine Rechnungen vorhanden.
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    {# === Widerruf & Kuendigung === #}
    <div class="col-12">
        <div class="card border-danger">
            <div class="card-header bg-danger bg-opacity-10">
                <h2 class="h6 mb-0 text-danger">Kuendigung</h2>
            </div>
            <div class="card-body">
                {% if subscription and subscription.status == "active" %}
                    {% if widerruf_eligible %}
                    <div class="alert alert-info">
                        <strong>Widerrufsrecht:</strong>
                        Sie koennen Ihr Abo noch {{ widerruf_days_remaining }} Tag(e) lang
                        gemaess SS 355 BGB widerrufen. Dabei erhalten Sie eine vollstaendige Erstattung.
                    </div>
                    {% endif %}

                    {% if subscription.cancel_at_period_end %}
                    <div class="alert alert-warning">
                        Ihr Abo endet am {{ subscription.current_period_end|date:"d.m.Y" }}.
                        Sie koennen Ihr Abo bis dahin jederzeit reaktivieren.
                    </div>
                    {% else %}
                    <p class="text-muted">
                        Bei Kuendigung bleibt Ihr Abo bis zum Ende des aktuellen
                        Abrechnungszeitraums ({{ subscription.current_period_end|date:"d.m.Y" }}) aktiv.
                    </p>
                    <button
                        class="btn btn-outline-danger"
                        hx-post="{% url 'dashboard:abo_cancel' %}"
                        hx-target="#abo-status-section"
                        hx-confirm="Moechten Sie Ihr Abo wirklich kuendigen? Es bleibt bis zum {{ subscription.current_period_end|date:'d.m.Y' }} aktiv."
                    >
                        Abo kuendigen
                    </button>
                    {% endif %}
                {% else %}
                    <p class="text-muted mb-0">Kein aktives Abo vorhanden.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 6. datenschutz_settings.html (Consent Toggles, Export/Deletion)

```html
{# dashboard/templates/dashboard/datenschutz_settings.html #}

{% extends "dashboard/dashboard_base.html" %}
{% load static %}

{% block breadcrumb_items %}
<li class="breadcrumb-item active">Datenschutz</li>
{% endblock %}

{% block content_title %}Datenschutz-Einstellungen{% endblock %}

{% block dashboard_content %}
<div class="row g-4">
    {# === Consent Toggles === #}
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header">
                <h2 class="h6 mb-0">Einwilligungen verwalten</h2>
            </div>
            <div class="card-body">
                <p class="text-muted small mb-4">
                    Gemaess Art. 7 Abs. 3 DSGVO koennen Sie Ihre Einwilligungen
                    jederzeit mit Wirkung fuer die Zukunft widerrufen.
                </p>

                {# Analytics Consent #}
                <div class="consent-toggle mb-3" id="consent-analytics">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>Nutzungsanalyse</strong>
                            <p class="text-muted small mb-0">
                                Anonymisierte Analyse der Nutzung zur Verbesserung unseres Dienstes.
                            </p>
                        </div>
                        <div class="form-check form-switch">
                            <input
                                type="checkbox"
                                class="form-check-input"
                                id="toggle-analytics"
                                {% if consent_settings.analytics %}checked{% endif %}
                                hx-post="{% url 'dashboard:datenschutz_consent' %}"
                                hx-vals='{"consent_type": "analytics"}'
                                hx-target="#consent-analytics"
                                hx-swap="outerHTML"
                                hx-include="this"
                                name="value"
                                value="true"
                            >
                        </div>
                    </div>
                </div>

                {# Marketing Email Consent #}
                <div class="consent-toggle mb-3" id="consent-marketing">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>Marketing-E-Mails</strong>
                            <p class="text-muted small mb-0">
                                Tipps, Neuigkeiten und Angebote per E-Mail erhalten.
                            </p>
                        </div>
                        <div class="form-check form-switch">
                            <input
                                type="checkbox"
                                class="form-check-input"
                                id="toggle-marketing"
                                {% if consent_settings.marketing_email %}checked{% endif %}
                                hx-post="{% url 'dashboard:datenschutz_consent' %}"
                                hx-vals='{"consent_type": "marketing_email"}'
                                hx-target="#consent-marketing"
                                hx-swap="outerHTML"
                                name="value"
                                value="true"
                            >
                        </div>
                    </div>
                </div>

                {# Third-party Tracking Consent #}
                <div class="consent-toggle" id="consent-thirdparty">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>Drittanbieter-Tracking</strong>
                            <p class="text-muted small mb-0">
                                Verwendung von Drittanbieter-Cookies fuer personalisierte Werbung.
                            </p>
                        </div>
                        <div class="form-check form-switch">
                            <input
                                type="checkbox"
                                class="form-check-input"
                                id="toggle-thirdparty"
                                {% if consent_settings.third_party_tracking %}checked{% endif %}
                                hx-post="{% url 'dashboard:datenschutz_consent' %}"
                                hx-vals='{"consent_type": "third_party"}'
                                hx-target="#consent-thirdparty"
                                hx-swap="outerHTML"
                                name="value"
                                value="true"
                            >
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    {# === Data Export (Art. 20 DSGVO) === #}
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header">
                <h2 class="h6 mb-0">Datenexport (Art. 20 DSGVO)</h2>
            </div>
            <div class="card-body">
                <p class="text-muted small">
                    Sie haben das Recht auf Datenportabilitaet. Wir stellen Ihnen alle
                    personenbezogenen Daten in einem maschinenlesbaren Format (JSON + PDF) bereit.
                </p>

                {% if available_exports %}
                <div class="alert alert-success">
                    {% for export in available_exports %}
                    <div class="d-flex justify-content-between align-items-center">
                        <span>Export vom {{ export.completed_at|date:"d.m.Y H:i" }}</span>
                        <a href="{% url 'gdpr:download_export' export.id %}" class="btn btn-sm btn-success">
                            Herunterladen
                        </a>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}

                {% if pending_requests %}
                <div class="alert alert-info">
                    Ein Datenexport wird gerade verarbeitet. Sie erhalten eine E-Mail,
                    sobald der Download bereit ist.
                </div>
                {% else %}
                <div id="export-result">
                    <button
                        class="btn btn-outline-primary"
                        hx-post="{% url 'dashboard:datenschutz_export' %}"
                        hx-target="#export-result"
                        hx-swap="innerHTML"
                    >
                        Daten exportieren
                    </button>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    {# === Account Deletion (Art. 17 DSGVO) === #}
    <div class="col-lg-8">
        <div class="card border-danger">
            <div class="card-header bg-danger bg-opacity-10">
                <h2 class="h6 mb-0 text-danger">Konto und Daten loeschen (Art. 17 DSGVO)</h2>
            </div>
            <div class="card-body">
                <p class="text-muted small">
                    Sie haben das Recht auf Loeschung Ihrer personenbezogenen Daten.
                    Nach Bestaetigung wird Ihr Konto innerhalb von 14 Tagen unwiderruflich geloescht.
                    Rechnungsdaten unterliegen der gesetzlichen Aufbewahrungspflicht (10 Jahre, GoBD).
                </p>

                <div class="alert alert-warning">
                    <strong>Achtung:</strong> Diese Aktion kann nicht rueckgaengig gemacht werden.
                    Alle Ihre Dokumente, Lebenslauefe und Kontoeinstellungen werden geloescht.
                </div>

                <div id="deletion-result" x-data="{ confirmText: '' }">
                    <div class="mb-3">
                        <label for="delete-confirm" class="form-label">
                            Geben Sie <strong>LOESCHEN</strong> ein, um zu bestaetigen:
                        </label>
                        <input
                            type="text"
                            id="delete-confirm"
                            class="form-control"
                            x-model="confirmText"
                            placeholder="LOESCHEN"
                        >
                    </div>
                    <button
                        class="btn btn-danger"
                        :disabled="confirmText !== 'LOESCHEN'"
                        hx-post="{% url 'dashboard:datenschutz_deletion' %}"
                        hx-target="#deletion-result"
                        hx-swap="innerHTML"
                        hx-vals='{"confirmation": "LOESCHEN"}'
                    >
                        Konto unwiderruflich loeschen
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 7. bewerbungsmappe.html (Sortable.js Drag & Drop)

```html
{# dashboard/templates/dashboard/bewerbungsmappe.html #}

{% extends "dashboard/dashboard_base.html" %}
{% load static %}

{% block breadcrumb_items %}
<li class="breadcrumb-item active">Bewerbungsmappe</li>
{% endblock %}

{% block content_title %}Bewerbungsmappe{% endblock %}

{% block extra_head %}
{# Sortable.js for drag & drop #}
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15/Sortable.min.js" defer></script>
{% endblock %}

{% block page_actions %}
<button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#newMappeModal">
    + Neue Mappe
</button>
{% endblock %}

{% block dashboard_content %}
<div class="row g-4">
    {# === Mappen List (Sidebar) === #}
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h2 class="h6 mb-0">Meine Mappen</h2>
            </div>
            <div class="list-group list-group-flush">
                {% for mappe in mappen %}
                <a
                    href="{% url 'dashboard:bewerbungsmappe_detail' mappe.id %}"
                    class="list-group-item list-group-item-action {% if active_mappe and active_mappe.id == mappe.id %}active{% endif %}"
                >
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>{{ mappe.title }}</strong>
                            <div class="small text-muted">{{ mappe.items.count }} Dokument(e)</div>
                        </div>
                        <span class="badge bg-primary rounded-pill">{{ mappe.items.count }}</span>
                    </div>
                </a>
                {% empty %}
                <div class="list-group-item text-center text-muted py-4">
                    Noch keine Mappen erstellt.
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    {# === Active Mappe Content === #}
    <div class="col-md-8">
        {% if active_mappe %}
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h2 class="h6 mb-0">{{ active_mappe.title }}</h2>
                <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#addDocModal">
                        + Dokument hinzufuegen
                    </button>
                    <button class="btn btn-sm btn-outline-success"
                            hx-post="{% url 'dashboard:bewerbungsmappe_pdf' active_mappe.id %}"
                            hx-target="#pdf-download-area">
                        PDF erstellen
                    </button>
                </div>
            </div>
            <div class="card-body p-0">
                <div id="pdf-download-area"></div>

                <p class="text-muted small px-3 pt-3">
                    Ziehen Sie die Dokumente in die gewuenschte Reihenfolge:
                </p>

                {# Sortable List #}
                <ul
                    class="list-group list-group-flush sortable-list"
                    id="mappe-items"
                    data-reorder-url="{% url 'dashboard:bewerbungsmappe_reorder' active_mappe.id %}"
                >
                    {% for item in active_mappe.items.all %}
                    <li
                        class="list-group-item d-flex align-items-center gap-3"
                        data-item-id="{{ item.id }}"
                    >
                        {# Drag handle #}
                        <span class="sortable-handle text-muted" style="cursor: grab;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M7 2a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
                            </svg>
                        </span>

                        {# Position number #}
                        <span class="badge bg-light text-dark fw-normal position-badge">
                            {{ item.position }}
                        </span>

                        {# Document type badge #}
                        <span class="badge badge-{{ item.document.document_type }}">
                            {{ item.document.get_document_type_display }}
                        </span>

                        {# Title #}
                        <span class="flex-grow-1 fw-medium">
                            {{ item.document.title }}
                        </span>

                        {# Template name #}
                        {% if item.document.template %}
                        <span class="text-muted small">
                            {{ item.document.template.name }}
                        </span>
                        {% endif %}

                        {# Remove button #}
                        <button
                            class="btn btn-sm btn-link text-danger p-0"
                            hx-delete="{% url 'dashboard:bewerbungsmappe_remove' active_mappe.id item.id %}"
                            hx-target="closest li"
                            hx-swap="outerHTML"
                            hx-confirm="Dokument aus Mappe entfernen?"
                            title="Entfernen"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                                 fill="currentColor" viewBox="0 0 16 16">
                                <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                            </svg>
                        </button>
                    </li>
                    {% empty %}
                    <li class="list-group-item text-center text-muted py-4">
                        Keine Dokumente in dieser Mappe.
                        Fuegen Sie Dokumente ueber den Button oben hinzu.
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        {% else %}
        <div class="card">
            <div class="card-body text-center py-5">
                <p class="text-muted">Waehlen Sie eine Mappe aus oder erstellen Sie eine neue.</p>
            </div>
        </div>
        {% endif %}
    </div>
</div>

{# === Sortable.js Initialization === #}
{% if active_mappe %}
<script>
document.addEventListener("DOMContentLoaded", function() {
    const list = document.getElementById("mappe-items");
    if (!list) return;

    const sortable = new Sortable(list, {
        handle: ".sortable-handle",
        animation: 150,
        ghostClass: "sortable-ghost",
        chosenClass: "sortable-chosen",
        dragClass: "sortable-drag",
        onEnd: function(evt) {
            // Collect new order
            const items = list.querySelectorAll("[data-item-id]");
            const order = Array.from(items).map(el => el.dataset.itemId);

            // Update position badges
            items.forEach((el, idx) => {
                const badge = el.querySelector(".position-badge");
                if (badge) badge.textContent = idx + 1;
            });

            // Send to server via HTMX
            const url = list.dataset.reorderUrl;
            const formData = new FormData();
            order.forEach(id => formData.append("order[]", id));

            fetch(url, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")?.value
                        || document.cookie.match(/csrftoken=([^;]+)/)?.[1] || "",
                    "HX-Request": "true",
                },
            });
        },
    });
});
</script>
{% endif %}

{% endblock %}
```

---

## 8. Admin Templates (Chart.js Dashboard, User Management)

### admin_dashboard.html

```html
{# dashboard/templates/dashboard/admin_dashboard.html #}

{% extends "dashboard/dashboard_base.html" %}
{% load static humanize %}

{% block extra_head %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4/dist/chart.umd.min.js" defer></script>
{% endblock %}

{% block breadcrumb_items %}
<li class="breadcrumb-item active">Admin Dashboard</li>
{% endblock %}

{% block content_title %}Admin Dashboard{% endblock %}

{% block dashboard_content %}
{# === KPI Cards === #}
<div class="row g-3 mb-4">
    <div class="col-sm-6 col-xl-3">
        <div class="card bg-primary text-white">
            <div class="card-body">
                <div class="text-white-50 small">Monatl. Umsatz (MRR)</div>
                <div class="h4 mb-0">{{ mrr|floatformat:2 }} &euro;</div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card bg-success text-white">
            <div class="card-body">
                <div class="text-white-50 small">Jaehrl. Umsatz (ARR)</div>
                <div class="h4 mb-0">{{ arr|floatformat:2 }} &euro;</div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card bg-info text-white">
            <div class="card-body">
                <div class="text-white-50 small">Aktive Abos</div>
                <div class="h4 mb-0">{{ active_subscriptions|intcomma }}</div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card bg-warning text-dark">
            <div class="card-body">
                <div class="text-dark-50 small">Churn Rate</div>
                <div class="h4 mb-0">{{ churn_rate }}%</div>
            </div>
        </div>
    </div>
</div>

{# === Charts Row 1 === #}
<div class="row g-4 mb-4">
    {# Daily Revenue Chart #}
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header">
                <h2 class="h6 mb-0">Tagesumsatz (letzte 30 Tage)</h2>
            </div>
            <div class="card-body">
                <canvas id="dailyRevenueChart" height="300"></canvas>
            </div>
        </div>
    </div>

    {# Subscriptions by Plan (Doughnut) #}
    <div class="col-lg-4">
        <div class="card">
            <div class="card-header">
                <h2 class="h6 mb-0">Abos nach Plan</h2>
            </div>
            <div class="card-body">
                <canvas id="subsByPlanChart" height="300"></canvas>
            </div>
        </div>
    </div>
</div>

{# === Charts Row 2 === #}
<div class="row g-4 mb-4">
    {# Monthly Revenue Chart #}
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header">
                <h2 class="h6 mb-0">Monatsumsatz (12 Monate)</h2>
            </div>
            <div class="card-body">
                <canvas id="monthlyRevenueChart" height="250"></canvas>
            </div>
        </div>
    </div>

    {# User Registrations #}
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header">
                <h2 class="h6 mb-0">Neue Registrierungen (30 Tage)</h2>
            </div>
            <div class="card-body">
                <canvas id="registrationsChart" height="250"></canvas>
            </div>
        </div>
    </div>
</div>

{# === Stats Cards Row === #}
<div class="row g-3">
    <div class="col-sm-6 col-xl-3">
        <div class="card">
            <div class="card-body">
                <div class="text-muted small">Benutzer gesamt</div>
                <div class="h5">{{ total_users|intcomma }}</div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card">
            <div class="card-body">
                <div class="text-muted small">Neue Benutzer (30 T.)</div>
                <div class="h5">{{ new_users_30d|intcomma }}</div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card">
            <div class="card-body">
                <div class="text-muted small">Dokumente gesamt</div>
                <div class="h5">{{ total_documents|intcomma }}</div>
            </div>
        </div>
    </div>
    <div class="col-sm-6 col-xl-3">
        <div class="card">
            <div class="card-body">
                <div class="text-muted small">DSGVO-Antraege offen</div>
                <div class="h5 {% if pending_gdpr_requests > 0 %}text-warning{% endif %}">
                    {{ pending_gdpr_requests }}
                </div>
            </div>
        </div>
    </div>
</div>

{# === Chart.js Initialization === #}
<script>
document.addEventListener("DOMContentLoaded", function() {
    const chartColors = {
        primary: "#2563eb",
        primaryLight: "rgba(37, 99, 235, 0.1)",
        success: "#16a34a",
        successLight: "rgba(22, 163, 74, 0.1)",
    };

    // Daily Revenue Line Chart
    new Chart(document.getElementById("dailyRevenueChart"), {
        type: "line",
        data: {
            labels: {{ revenue_chart_labels|safe }},
            datasets: [{
                label: "Umsatz (EUR)",
                data: {{ revenue_chart_data|safe }},
                borderColor: chartColors.primary,
                backgroundColor: chartColors.primaryLight,
                fill: true,
                tension: 0.3,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ctx.parsed.y.toFixed(2) + " EUR",
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: (v) => v + " EUR" }
                }
            }
        }
    });

    // Subscriptions by Plan Doughnut
    new Chart(document.getElementById("subsByPlanChart"), {
        type: "doughnut",
        data: {
            labels: {{ subs_by_plan_labels|safe }},
            datasets: [{
                data: {{ subs_by_plan_data|safe }},
                backgroundColor: ["#2563eb", "#16a34a", "#f59e0b", "#ef4444", "#8b5cf6"],
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });

    // Monthly Revenue Bar Chart
    new Chart(document.getElementById("monthlyRevenueChart"), {
        type: "bar",
        data: {
            labels: {{ monthly_revenue_labels|safe }},
            datasets: [{
                label: "Monatsumsatz (EUR)",
                data: {{ monthly_revenue_data|safe }},
                backgroundColor: chartColors.primary,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: (v) => v + " EUR" }
                }
            }
        }
    });

    // Registrations Line Chart
    new Chart(document.getElementById("registrationsChart"), {
        type: "line",
        data: {
            labels: {{ registrations_chart_labels|safe }},
            datasets: [{
                label: "Registrierungen",
                data: {{ registrations_chart_data|safe }},
                borderColor: chartColors.success,
                backgroundColor: chartColors.successLight,
                fill: true,
                tension: 0.3,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });
});
</script>
{% endblock %}
```

### admin_user_management.html

```html
{# dashboard/templates/dashboard/admin_user_management.html #}

{% extends "dashboard/dashboard_base.html" %}
{% load static humanize %}

{% block breadcrumb_items %}
<li class="breadcrumb-item active">Benutzerverwaltung</li>
{% endblock %}

{% block content_title %}Benutzerverwaltung{% endblock %}

{% block dashboard_content %}
<div class="card">
    {# Filter Bar #}
    <div class="card-header">
        <div class="d-flex flex-wrap gap-3 align-items-center">
            <input
                type="search"
                name="q"
                value="{{ search_query }}"
                placeholder="Name oder E-Mail suchen..."
                class="form-control form-control-sm"
                style="max-width: 300px;"
                hx-get="{% url 'dashboard:admin_users' %}"
                hx-target="#user-table-container"
                hx-trigger="input changed delay:300ms"
                hx-include="[name='sub_status'], [name='plan'], [name='is_active']"
            >

            <select name="sub_status" class="form-select form-select-sm" style="width: auto;"
                    hx-get="{% url 'dashboard:admin_users' %}"
                    hx-target="#user-table-container"
                    hx-trigger="change"
                    hx-include="[name='q'], [name='plan'], [name='is_active']">
                <option value="">Abo-Status</option>
                <option value="active" {% if active_sub_status == "active" %}selected{% endif %}>Aktives Abo</option>
                <option value="none" {% if active_sub_status == "none" %}selected{% endif %}>Kein Abo</option>
                <option value="cancelled" {% if active_sub_status == "cancelled" %}selected{% endif %}>Gekuendigt</option>
            </select>

            <select name="plan" class="form-select form-select-sm" style="width: auto;"
                    hx-get="{% url 'dashboard:admin_users' %}"
                    hx-target="#user-table-container"
                    hx-trigger="change"
                    hx-include="[name='q'], [name='sub_status'], [name='is_active']">
                <option value="">Alle Plaene</option>
                {% for plan in plans %}
                <option value="{{ plan.id }}" {% if active_plan == plan.id|stringformat:"s" %}selected{% endif %}>
                    {{ plan.display_name }}
                </option>
                {% endfor %}
            </select>

            <select name="is_active" class="form-select form-select-sm" style="width: auto;"
                    hx-get="{% url 'dashboard:admin_users' %}"
                    hx-target="#user-table-container"
                    hx-trigger="change"
                    hx-include="[name='q'], [name='sub_status'], [name='plan']">
                <option value="">Alle Status</option>
                <option value="true">Aktiv</option>
                <option value="false">Inaktiv</option>
            </select>
        </div>
    </div>

    {# User Table #}
    <div id="user-table-container">
        {% include "dashboard/partials/admin_user_table.html" %}
    </div>
</div>
{% endblock %}
```
