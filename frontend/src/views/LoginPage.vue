<template>
  <!--
    LoginPage.vue
    ─────────────
    Desktop → full blue background, white card centered in the middle
    Mobile  → same background, card stretches to fill the screen width
  -->
  <div class="page">

    <!-- CARD WRAPPER — centers the card on desktop -->
    <div class="card-wrapper">

      <!-- App branding above the card -->
      <div class="brand">
        <span class="app-name">MediBuddy</span>
      </div>

      <!-- The reusable login card -->
      <LoginCard />

    </div>

  </div>
</template>

<script setup>
import LoginCard from '@/components/LoginCard.vue'

</script>

<style scoped>

/* ── FULL PAGE ── */
.page {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(160deg, #0ea5e9 0%, #0369a1 100%);
  display: flex;
  align-items: center;
  justify-content: center;

  /*
    On mobile we add side padding so the card doesn't
    touch the edges of the screen.
  */
  padding: 24px 16px;
}

/* ── CARD WRAPPER ── */
.card-wrapper {
  width: 100%;

  /*
    Mobile: card fills most of the screen width (up to 440px).
    Desktop: stays at 440px max so it doesn't get too wide.
  */
  max-width: 440px;
}

/* ── BRANDING (above the card) ── */
.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 24px;
}

.app-name {
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.5px;
  font-family: var(--font-main);
}

/*
  ══════════════════════════════════
  MOBILE TWEAKS  (max-width: 480px)
  ══════════════════════════════════
  On small phones, reduce font sizes
  and tighten spacing a little.
*/
@media (max-width: 480px) {
  .app-name {
    font-size: 24px;
  }

  .pill-icon {
    font-size: 30px;
  }

  /*
    :deep() lets scoped CSS reach inside
    a child component (LoginCard).
    We use it here to adjust the card
    padding on very small screens.
  */
  :deep(.card) {
    padding: 24px 18px;
  }
}

</style>
