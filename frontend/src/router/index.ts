import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    // --- Public ---
    {
      path: '/',
      component: () => import('@/views/LandingPage.vue'),
    },
    {
      path: '/login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { guest: true },
    },
    {
      path: '/passwort-vergessen',
      component: () => import('@/views/auth/PasswordResetView.vue'),
      meta: { guest: true },
    },
    {
      path: '/email-bestaetigen/:key',
      component: () => import('@/views/auth/EmailConfirmView.vue'),
    },
    {
      path: '/passwort-zuruecksetzen/:uid/:token',
      component: () => import('@/views/auth/PasswordResetConfirmView.vue'),
      meta: { guest: true },
    },
    {
      path: '/preise',
      component: () => import('@/views/PricingView.vue'),
    },

    // --- Authenticated (Dashboard) ---
    {
      path: '/app',
      component: () => import('@/components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
        },
        {
          path: 'documents',
          name: 'documents',
          component: () => import('@/views/dashboard/DocumentsView.vue'),
        },
        {
          path: 'templates',
          name: 'templates',
          component: () => import('@/views/dashboard/TemplatesView.vue'),
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/dashboard/SettingsView.vue'),
        },
        {
          path: 'billing',
          name: 'billing',
          component: () => import('@/views/dashboard/BillingView.vue'),
        },
        {
          path: 'jobs',
          name: 'jobs',
          component: () => import('@/views/dashboard/JobsView.vue'),
        },
        {
          path: 'applications',
          name: 'applications',
          component: () => import('@/views/dashboard/ApplicationsView.vue'),
        },
        {
          path: 'admin',
          name: 'admin',
          component: () => import('@/views/dashboard/AdminView.vue'),
          meta: { requiresAuth: true, requiresStaff: true },
        },
      ],
    },

    // --- CV Editor (full-screen) ---
    {
      path: '/editor/:id',
      name: 'editor',
      component: () => import('@/views/editor/EditorView.vue'),
      meta: { requiresAuth: true },
    },

    // --- Legal ---
    {
      path: '/impressum',
      component: () => import('@/views/legal/ImpressumView.vue'),
    },
    {
      path: '/datenschutz',
      component: () => import('@/views/legal/DatenschutzView.vue'),
    },
    {
      path: '/agb',
      component: () => import('@/views/legal/AGBView.vue'),
    },

    // --- Catch-all ---
    {
      path: '/:pathMatch(.*)*',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

// Navigation guard
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return { path: '/app' }
  }

  if (to.meta.requiresStaff && !auth.isStaff) {
    return { path: '/app' }
  }
})

export default router
