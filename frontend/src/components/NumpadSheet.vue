<template>
  <Teleport to="body">
    <Transition name="fade">
      <div class="overlay" v-if="target" @click.self="$emit('close')">
        <Transition name="slide-up">
          <div class="numpad-sheet" v-if="target">
            <div class="sheet-handle"></div>
            <p class="numpad-label">{{ target.brand_name ?? target.name }}</p>
            <p class="numpad-sub">{{ subtitle ?? 'Set stock quantity' }}</p>
            <div class="numpad-display" :class="{ 'numpad-display--low': display !== '0' && +display <= 5 }">
              <span class="numpad-value">{{ display }}</span>
              <span class="numpad-unit">pcs</span>
            </div>
            <div class="numpad-grid">
              <button class="numpad-key" v-for="key in ['1','2','3','4','5','6','7','8','9']" :key="key" @click="press(key)">{{ key }}</button>
              <button class="numpad-key numpad-key--action" @click="press('C')">C</button>
              <button class="numpad-key" @click="press('0')">0</button>
              <button class="numpad-key numpad-key--action" @click="press('⌫')">⌫</button>
            </div>
            <button class="numpad-confirm" @click="$emit('confirm', +display)">✓ &nbsp; Set to {{ display }} pcs</button>
            <button class="numpad-cancel" @click="$emit('close')">Cancel</button>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  target:   { type: Object,  default: null },
  subtitle: { type: String,  default: null },
})
defineEmits(['confirm', 'close'])

const raw = ref('')
const display = computed(() => raw.value === '' ? '0' : raw.value)

// Reset when a new target is opened
watch(() => props.target, (t) => {
  if (!t) { raw.value = ''; return }
  const stock = t.supply_stock ?? t.quantity
  raw.value = stock != null && stock > 0 ? String(stock) : ''
})

function press(key) {
  if (key === 'C')  { raw.value = ''; return }
  if (key === '⌫')  { raw.value = raw.value.slice(0, -1); return }
  if (raw.value.length >= 4) return
  if (raw.value === '' && key === '0') return
  raw.value += key
}
</script>

<style scoped>
.overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:flex-end; justify-content:center; z-index:500; }
.numpad-sheet { background:var(--color-white); border-radius:24px 24px 0 0; padding:12px 24px 44px; width:100%; max-width:420px; display:flex; flex-direction:column; align-items:center; }
.sheet-handle { width:40px; height:4px; background:#cbd5e1; border-radius:2px; margin:0 auto 12px; }
.numpad-label { font-size:16px; font-weight:800; color:var(--color-text-dark); text-align:center; }
.numpad-sub   { font-size:12px; color:var(--color-text-muted); margin-top:2px; margin-bottom:16px; }
.numpad-display { width:100%; background:var(--color-primary-light); border-radius:16px; padding:14px 20px; display:flex; align-items:baseline; justify-content:center; gap:8px; margin-bottom:20px; transition:background .2s; }
.numpad-display--low { background:#fee2e2; }
.numpad-value { font-size:42px; font-weight:900; color:var(--color-primary-dark); line-height:1; }
.numpad-display--low .numpad-value { color:#dc2626; }
.numpad-unit  { font-size:16px; font-weight:600; color:var(--color-text-muted); }
.numpad-grid  { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; width:100%; margin-bottom:16px; }
.numpad-key   { height:60px; border-radius:14px; border:none; background:#f1f5f9; color:var(--color-text-dark); font-size:22px; font-weight:700; font-family:var(--font-main); cursor:pointer; transition:background .1s,transform .08s; display:flex; align-items:center; justify-content:center; }
.numpad-key:active { background:var(--color-primary-light); transform:scale(.92); }
.numpad-key--action { background:#e2e8f0; color:var(--color-text-muted); font-size:18px; }
.numpad-confirm { width:100%; padding:15px; border:none; border-radius:var(--radius-btn); background:var(--color-primary); color:#fff; font-size:16px; font-weight:800; font-family:var(--font-main); cursor:pointer; transition:background .2s; margin-bottom:10px; }
.numpad-confirm:hover { background:var(--color-primary-dark); }
.numpad-cancel  { width:100%; padding:12px; border:2px solid var(--color-border); border-radius:var(--radius-btn); background:none; color:var(--color-text-muted); font-size:14px; font-weight:600; font-family:var(--font-main); cursor:pointer; }
.fade-enter-active,.fade-leave-active { transition:opacity .22s; }
.fade-enter-from,.fade-leave-to       { opacity:0; }
.slide-up-enter-active,.slide-up-leave-active { transition:transform .25s cubic-bezier(.32,1,.32,1); }
.slide-up-enter-from,.slide-up-leave-to       { transform:translateY(100%); }
</style>