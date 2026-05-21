import { ref, computed } from 'vue'
import api from '@/api'

// Shared singleton — both ShelfTab and PrescriptionsTab see the same context
export const circles      = ref([])   // joined circles
export const activeCircle = ref(null) // null = own data

export const isOwn   = computed(() => !activeCircle.value)
export const canEdit = computed(() =>
  !activeCircle.value || activeCircle.value.permission === 'canedit'
)

export async function loadCircles() {
  try {
    circles.value = (await api.get('/circle/joined')).data
    if (activeCircle.value) {
      const still_exists = circles.value.find(
        c => c.circle_id === activeCircle.value.circle_id
      )
      if (!still_exists) activeCircle.value = null
    }
  }
  catch { circles.value = [] }
}

export function selectCircle(c) { activeCircle.value = c }
export function selectOwn()     { activeCircle.value = null }
