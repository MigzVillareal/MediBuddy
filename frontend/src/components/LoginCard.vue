<template>
  <!--
    LoginCard.vue
    ─────────────
    This is ONLY the white card with the form inside it.
    It knows nothing about the page layout around it.
    The parent page (LoginPage.vue) decides where to place it.
  -->
  <div class="card">
    <h2 class="card-title">Sign In</h2>

    <!-- USERNAME FIELD -->
    <div class="field">
      <label class="label">Username</label>
      <input
        class="input"
        type="text"
        placeholder="Enter your username"
        v-model="username"
      />
    </div>

    <!-- PASSWORD FIELD -->
    <div class="field">
      <label class="label">Password</label>
      <input
        class="input"
        :type="showPassword ? 'text' : 'password'"
        placeholder="Enter your password"
        v-model="password"
      />
      <button class="toggle-pw" type="button" @click="showPassword = !showPassword">
        {{ showPassword ? 'Hide' : 'Show' }}
      </button>
    </div>

    <!-- ERROR MESSAGE -->
    <p class="error" v-if="errorMessage">{{ errorMessage }}</p>

    <!-- LOGIN BUTTON -->
    <button class="btn-login" @click="handleLogin">
      Sign In
    </button>

    <!-- REGISTER LINK -->
    <p class="register-prompt">
      Don't have an account?
      <router-link to="/register" class="register-link">Register here</router-link>
    </p>
  </div>
</template>

<script>
export default {
  name: 'LoginCard',

  data() {
    return {
      username: '',
      password: '',
      showPassword: false,
      errorMessage: '',
    }
  },

  methods: {
    handleLogin() {
      this.errorMessage = ''

      if (!this.username || !this.password) {
        this.errorMessage = 'Please fill in both fields.'
        return
      }

      // Placeholder — you'll connect a real backend here later
      alert(`Welcome, ${this.username}! (Login logic coming soon)`)
    },
  },
}
</script>

<style scoped>
/*
  Only card-specific styles live here.
  Colors and fonts come from global.css via CSS variables.
*/

.card {
  background: var(--color-white);
  border-radius: var(--radius-card);
  padding: 32px 24px;
  width: 100%;
  box-shadow: var(--shadow-card);
}

.card-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--color-text-dark);
  margin-bottom: 24px;
}

/* ── FIELD ── */
.field {
  margin-bottom: 20px;
  position: relative;
}

.label {
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-body);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-input);
  font-size: 16px;
  font-family: var(--font-main);
  color: #1e293b;
  background: var(--color-input-bg);
  outline: none;
  transition: border-color 0.2s, background 0.2s;
}

.input:focus {
  border-color: var(--color-primary);
  background: var(--color-white);
}

/* ── SHOW / HIDE ── */
.toggle-pw {
  position: absolute;
  right: 14px;
  bottom: 14px;
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 700;
  font-family: var(--font-main);
  cursor: pointer;
  padding: 0;
}

/* ── ERROR ── */
.error {
  color: var(--color-text-error);
  font-size: 13px;
  font-weight: 600;
  margin: -10px 0 16px;
}

/* ── LOGIN BUTTON ── */
.btn-login {
  width: 100%;
  padding: 16px;
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-btn);
  color: var(--color-white);
  font-size: 16px;
  font-weight: 800;
  font-family: var(--font-main);
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  margin-top: 4px;
}

.btn-login:hover {
  background: var(--color-primary-dark);
}

.btn-login:active {
  transform: scale(0.98);
}

/* ── REGISTER LINK ── */
.register-prompt {
  text-align: center;
  font-size: 14px;
  color: var(--color-text-body);
  margin-top: 20px;
}

.register-link {
  color: var(--color-primary);
  font-weight: 700;
  text-decoration: none;
}

.register-link:hover {
  text-decoration: underline;
}
</style>
