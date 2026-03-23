import { ref } from 'vue'

export interface CookiePreferences {
  necessary: boolean // always true, locked
  statistics: boolean
  marketing: boolean
  external_media: boolean
}

const COOKIE_NAME = 'cookie_consent'
const MAX_AGE = 365 * 24 * 60 * 60 // 1 year in seconds

const preferences = ref<CookiePreferences | null>(null)
const showBanner = ref(false)
let initialized = false

function readCookie(): CookiePreferences | null {
  try {
    const match = document.cookie.match(new RegExp(`(?:^|; )${COOKIE_NAME}=([^;]*)`))
    if (!match) return null
    return JSON.parse(decodeURIComponent(match[1] ?? ''))
  } catch {
    return null
  }
}

function writeCookie(prefs: CookiePreferences) {
  const value = encodeURIComponent(JSON.stringify(prefs))
  document.cookie = `${COOKIE_NAME}=${value}; path=/; max-age=${MAX_AGE}; SameSite=Lax`
}

function init() {
  if (initialized) return
  initialized = true
  const stored = readCookie()
  if (stored) {
    preferences.value = stored
    showBanner.value = false
  } else {
    showBanner.value = true
  }
}

export function useCookieConsent() {
  // Initialize eagerly on first call
  init()

  function acceptAll() {
    const prefs: CookiePreferences = {
      necessary: true,
      statistics: true,
      marketing: true,
      external_media: true,
    }
    preferences.value = prefs
    writeCookie(prefs)
    showBanner.value = false
  }

  function acceptNecessary() {
    const prefs: CookiePreferences = {
      necessary: true,
      statistics: false,
      marketing: false,
      external_media: false,
    }
    preferences.value = prefs
    writeCookie(prefs)
    showBanner.value = false
  }

  function savePreferences(prefs: CookiePreferences) {
    prefs.necessary = true // always locked
    preferences.value = prefs
    writeCookie(prefs)
    showBanner.value = false
  }

  function revokeConsent() {
    document.cookie = `${COOKIE_NAME}=; path=/; max-age=0`
    preferences.value = null
    showBanner.value = true
  }

  return {
    preferences,
    showBanner,
    acceptAll,
    acceptNecessary,
    savePreferences,
    revokeConsent,
  }
}
