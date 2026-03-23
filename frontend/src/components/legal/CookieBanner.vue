<script setup lang="ts">
import { ref } from 'vue'
import { useCookieConsent } from '@/composables/useCookieConsent'
import { Cookie, Settings2, Shield } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import CookieSettingsDialog from './CookieSettingsDialog.vue'

const { showBanner, acceptAll, acceptNecessary } = useCookieConsent()
const settingsOpen = ref(false)
</script>

<template>
  <!-- Banner -->
  <Teleport to="body">
    <Transition name="banner">
      <div
        v-if="showBanner && !settingsOpen"
        class="fixed inset-0 z-[100] flex items-end justify-center pointer-events-none"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-[2px] pointer-events-auto"></div>

        <!-- Banner card -->
        <div class="relative w-full pointer-events-auto">
          <div class="mx-auto max-w-4xl px-4 pb-4 sm:pb-6">
            <div class="rounded-2xl border border-white/[0.08] glass p-6 sm:p-8 shadow-2xl">
              <div class="flex flex-col sm:flex-row sm:items-start gap-5">
                <!-- Icon -->
                <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-500/10 border border-indigo-500/20 shrink-0">
                  <Cookie class="h-6 w-6 text-indigo-400" />
                </div>

                <!-- Content -->
                <div class="flex-1">
                  <h3 class="text-base font-mono font-semibold text-foreground">
                    Diese Website verwendet Cookies
                  </h3>
                  <p class="mt-1.5 text-sm text-zinc-400 leading-relaxed">
                    Wir nutzen Cookies und ahnliche Technologien, um Ihnen ein optimales Erlebnis zu bieten.
                    Gemafl <strong class="text-zinc-300 font-medium">TTDSG &sect;25</strong> benotigen wir Ihre Einwilligung fur nicht-essenzielle Cookies.
                    Weitere Informationen finden Sie in unserer
                    <RouterLink to="/datenschutz" class="text-indigo-400 hover:underline font-medium">Datenschutzerklarung</RouterLink>.
                  </p>

                  <!-- Buttons -->
                  <div class="mt-5 flex flex-wrap gap-3">
                    <Button @click="acceptAll" class="glow-sm hover:glow-md transition-shadow">
                      <Shield class="h-4 w-4" />
                      Alle akzeptieren
                    </Button>
                    <Button variant="outline" @click="settingsOpen = true">
                      <Settings2 class="h-4 w-4" />
                      Einstellungen
                    </Button>
                    <Button variant="ghost" @click="acceptNecessary" class="text-zinc-500">
                      Nur notwendige
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <CookieSettingsDialog v-model:open="settingsOpen" />
</template>

<style scoped>
.banner-enter-active {
  transition: opacity 0.3s ease, transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.banner-leave-active {
  transition: opacity 0.2s ease, transform 0.3s ease;
}
.banner-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.banner-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
