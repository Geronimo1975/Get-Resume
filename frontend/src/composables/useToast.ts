import { ref } from 'vue'

export interface ToastMessage {
  id: string
  title: string
  description?: string
  variant?: 'default' | 'destructive' | 'success'
}

const toasts = ref<ToastMessage[]>([])

let counter = 0

export function useToast() {
  function toast(message: Omit<ToastMessage, 'id'>) {
    const id = `toast-${++counter}`
    toasts.value.push({ id, ...message })
    setTimeout(() => dismiss(id), 5000)
  }

  function dismiss(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return { toasts, toast, dismiss }
}
