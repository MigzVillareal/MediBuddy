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
  try { circles.value = (await api.get('/circle/joined')).data }
  catch { circles.value = [] }
}

export function selectCircle(c) { activeCircle.value = c }
export function selectOwn()     { activeCircle.value = null }
