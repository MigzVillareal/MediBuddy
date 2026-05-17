<template>
  <div class="tab">

    <!-- ── PENDING INVITES ─────────────────────────────────────────── -->
    <section v-if="pendingInvites.length > 0" class="pending-section">
      <h3 class="section-label">🔔 Pending Invites</h3>
      <div class="invite-card" v-for="inv in pendingInvites" :key="inv.invite_id">
        <div class="invite-info">
          <p class="invite-circle">{{ inv.circle_name }}</p>
          <p class="invite-meta">from <strong>{{ inv.inviter_username }}</strong> · {{ permLabel(inv.permission) }}</p>
        </div>
        <div class="invite-actions">
          <button class="btn-accept" @click="respondInvite(inv.invite_id, 'accept')">Accept</button>
          <button class="btn-reject" @click="respondInvite(inv.invite_id, 'reject')">Reject</button>
        </div>
      </div>
    </section>

    <!-- ── MY CIRCLES ─────────────────────────────────────────────── -->
    <div class="header-row">
      <div>
        <h2 class="section-title">My Circles</h2>
        <p class="section-sub">Groups of people who can view or manage your medications.</p>
      </div>
      <button class="btn-new" @click="showCreate = true">+ New Circle</button>
    </div>

    <div class="empty-state" v-if="circles.length === 0">
      <span class="empty-icon">👨‍👩‍👧</span>
      <p class="empty-title">No circles yet</p>
      <p class="empty-sub">Create a circle and invite family or caregivers.</p>
    </div>

    <div class="circle-grid" v-else>
      <div class="circle-card" v-for="c in circles" :key="c.circle_id" @click="openCircle(c)">
        <div class="circle-card__icon">{{ c.circle_name.charAt(0).toUpperCase() }}</div>
        <div class="circle-card__body">
          <p class="circle-card__name">{{ c.circle_name }}</p>
          <p class="circle-card__meta">{{ c.member_count }} member{{ c.member_count !== 1 ? 's' : '' }}</p>
        </div>
        <span class="circle-card__arrow">›</span>
      </div>
    </div>

    <!-- ── CREATE CIRCLE MODAL ────────────────────────────────────── -->
    <div class="modal-overlay" v-if="showCreate" @click.self="showCreate = false">
      <div class="modal">
        <h3 class="modal-title">Create a Circle</h3>
        <p v-if="createError" class="error-msg">{{ createError }}</p>
        <input class="input" type="text" placeholder="Circle name…" v-model="newCircleName" @keyup.enter="createCircle" />
        <button class="btn-primary" @click="createCircle" :disabled="isCreating">
          {{ isCreating ? 'Creating…' : 'Create Circle' }}
        </button>
        <button class="btn-ghost" @click="showCreate = false">Cancel</button>
      </div>
    </div>

    <!-- ── CIRCLE DETAIL MODAL ────────────────────────────────────── -->
    <div class="modal-overlay" v-if="activeCircle" @click.self="closeCircle">
      <div class="modal modal--wide">

        <!-- Header -->
        <div class="modal-header">
          <div v-if="!renaming" class="modal-title-row">
            <h3 class="modal-title">{{ activeCircle.circle_name }}</h3>
            <button class="btn-icon-sm" @click="startRename" title="Rename">✏️</button>
          </div>
          <div v-else class="rename-row">
            <input class="input input--sm" v-model="renameValue" @keyup.enter="saveRename" />
            <button class="btn-accent-sm" @click="saveRename">Save</button>
            <button class="btn-ghost-sm" @click="renaming = false">Cancel</button>
          </div>
          <p v-if="detailError" class="error-msg">{{ detailError }}</p>
        </div>

        <!-- Members -->
        <p class="list-label">Members</p>
        <div class="empty-members" v-if="activeMembers.length === 0">
          <p>No members yet. Send an invite below.</p>
        </div>
        <div class="member-row" v-for="m in activeMembers" :key="m.user_id">
          <div class="member-avatar">{{ m.username.charAt(0).toUpperCase() }}</div>
          <div class="member-info">
            <p class="member-name">{{ m.username }}</p>
            <span class="badge" :class="'badge--' + m.permission">{{ permLabel(m.permission) }}</span>
          </div>
          <div class="member-controls">
            <select class="select-sm" v-model="m.permission" @change="updatePerm(m)">
              <option value="canview">View Only</option>
              <option value="canedit">Can Edit</option>
            </select>
            <button class="btn-remove" @click="removeMember(m)" title="Remove">✕</button>
          </div>
        </div>

        <!-- Pending sent invites for this circle -->
        <template v-if="sentForCircle.length > 0">
          <p class="list-label">Sent Invites</p>
          <div class="sent-row" v-for="s in sentForCircle" :key="s.invite_id">
            <span class="sent-name">{{ s.invitee_username }}</span>
            <span class="sent-badge" :class="'sent-badge--' + s.status">{{ s.status }}</span>
          </div>
        </template>

        <!-- Add Member -->
        <p class="list-label" style="margin-top:16px">Invite a Member</p>
        <p v-if="inviteError" class="error-msg">{{ inviteError }}</p>
        <input class="input input--sm" type="text" placeholder="Their username" v-model="inviteUsername" />
        <select class="input input--sm" v-model="invitePermission">
          <option value="canview">View Only</option>
          <option value="canedit">Can Edit</option>
        </select>
        <button class="btn-primary" @click="sendInvite" :disabled="isSending">
          {{ isSending ? 'Sending…' : 'Send Invite' }}
        </button>

        <!-- Danger -->
        <button class="btn-danger" @click="deleteCircle" style="margin-top:8px">Delete Circle</button>
        <button class="btn-ghost" @click="closeCircle" style="margin-top:6px">Close</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'

// ── STATE ──────────────────────────────────────────────────────────
const circles       = ref([])
const pendingInvites = ref([])
const sentInvites   = ref([])

const showCreate    = ref(false)
const newCircleName = ref('')
const createError   = ref('')
const isCreating    = ref(false)

const activeCircle  = ref(null)   // the circle whose detail modal is open
const activeMembers = ref([])
const detailError   = ref('')

const renaming      = ref(false)
const renameValue   = ref('')

const inviteUsername   = ref('')
const invitePermission = ref('canview')
const inviteError      = ref('')
const isSending        = ref(false)

// Sent invites filtered to the currently open circle
const sentForCircle = computed(() =>
  activeCircle.value
    ? sentInvites.value.filter(s => s.circle_id === activeCircle.value.circle_id)
    : []
)

// ── HELPERS ────────────────────────────────────────────────────────
function permLabel(p) {
  return p === 'canedit' ? '✏️ Can Edit' : '👁 View Only'
}

// ── LOAD ───────────────────────────────────────────────────────────
async function init() {
  await Promise.all([loadCircles(), loadPendingInvites(), loadSentInvites()])
}

async function loadCircles() {
  try {
    const res = await api.get('/circle/mine')
    circles.value = res.data
  } catch (e) { console.error(e) }
}

async function loadPendingInvites() {
  try {
    const res = await api.get('/circle/invites/pending')
    pendingInvites.value = res.data
  } catch (e) { console.error(e) }
}

async function loadSentInvites() {
  try {
    const res = await api.get('/circle/invites/sent')
    sentInvites.value = res.data
  } catch (e) { console.error(e) }
}

onMounted(init)

// ── CREATE CIRCLE ──────────────────────────────────────────────────
async function createCircle() {
  createError.value = ''
  if (!newCircleName.value.trim()) { createError.value = 'Please enter a name.'; return }
  isCreating.value = true
  try {
    await api.post('/circle/create', { circle_name: newCircleName.value.trim() })
    newCircleName.value = ''
    showCreate.value = false
    await loadCircles()
  } catch (e) {
    createError.value = e.response?.data?.error || 'Failed to create circle.'
  } finally { isCreating.value = false }
}

// ── OPEN / CLOSE DETAIL ────────────────────────────────────────────
async function openCircle(c) {
  activeCircle.value = c
  detailError.value = ''
  inviteUsername.value = ''
  inviteError.value = ''
  renaming.value = false
  await loadMembers()
  await loadSentInvites()
}

function closeCircle() {
  activeCircle.value = null
  activeMembers.value = []
}

async function loadMembers() {
  if (!activeCircle.value) return
  try {
    const res = await api.get(`/circle/${activeCircle.value.circle_id}/members`)
    activeMembers.value = res.data
  } catch (e) { console.error(e) }
}

// ── RENAME ─────────────────────────────────────────────────────────
function startRename() {
  renameValue.value = activeCircle.value.circle_name
  renaming.value = true
}

async function saveRename() {
  if (!renameValue.value.trim()) return
  try {
    await api.put(`/circle/${activeCircle.value.circle_id}/rename`, { circle_name: renameValue.value.trim() })
    activeCircle.value.circle_name = renameValue.value.trim()
    renaming.value = false
    await loadCircles()
  } catch (e) { detailError.value = e.response?.data?.error || 'Rename failed.' }
}

// ── DELETE CIRCLE ──────────────────────────────────────────────────
async function deleteCircle() {
  if (!confirm(`Delete "${activeCircle.value.circle_name}"? This cannot be undone.`)) return
  try {
    await api.delete(`/circle/${activeCircle.value.circle_id}`)
    closeCircle()
    await loadCircles()
  } catch (e) { detailError.value = e.response?.data?.error || 'Delete failed.' }
}

// ── INVITE ─────────────────────────────────────────────────────────
async function sendInvite() {
  inviteError.value = ''
  if (!inviteUsername.value.trim()) { inviteError.value = 'Enter a username.'; return }
  isSending.value = true
  try {
    await api.post('/circle/invite', {
      circle_id: activeCircle.value.circle_id,
      username: inviteUsername.value.trim(),
      permission: invitePermission.value,
    })
    inviteUsername.value = ''
    invitePermission.value = 'canview'
    await loadSentInvites()
  } catch (e) {
    inviteError.value = e.response?.data?.error || 'Failed to send invite.'
  } finally { isSending.value = false }
}

// ── RESPOND TO INVITE ──────────────────────────────────────────────
async function respondInvite(inviteId, action) {
  try {
    await api.post(`/circle/invite/${inviteId}/respond`, { action })
    await loadPendingInvites()
    await loadCircles()
  } catch (e) { console.error(e) }
}

// ── PERMISSION UPDATE ──────────────────────────────────────────────
async function updatePerm(member) {
  try {
    await api.post('/circle/update_permission', {
      circle_id: activeCircle.value.circle_id,
      user_id: member.user_id,
      permission: member.permission,
    })
  } catch (e) { detailError.value = e.response?.data?.error || 'Update failed.' }
}

// ── REMOVE MEMBER ──────────────────────────────────────────────────
async function removeMember(member) {
  if (!confirm(`Remove ${member.username} from the circle?`)) return
  try {
    await api.post('/circle/remove_member', {
      circle_id: activeCircle.value.circle_id,
      user_id: member.user_id,
    })
    await loadMembers()
    await loadCircles()
  } catch (e) { detailError.value = e.response?.data?.error || 'Remove failed.' }
}
</script>

<style scoped>
/* ── BASE ─────────────────────────────────────────────────────── */
.tab { padding: 20px 20px 100px; }

/* ── HEADER ROW ───────────────────────────────────────────────── */
.header-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 16px; }
.section-title { font-size: 20px; font-weight: 800; color: var(--color-text-dark); margin-bottom: 2px; }
.section-sub   { font-size: 13px; color: var(--color-text-muted); }
.btn-new {
  flex-shrink: 0;
  padding: 10px 16px;
  background: var(--color-primary);
  color: var(--color-white);
  border: none; border-radius: 12px;
  font-size: 14px; font-weight: 700;
  font-family: var(--font-main);
  cursor: pointer; white-space: nowrap;
  transition: background 0.2s;
}
.btn-new:hover { background: var(--color-primary-dark); }

/* ── PENDING INVITES ──────────────────────────────────────────── */
.pending-section { margin-bottom: 24px; }
.section-label { font-size: 13px; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: .05em; margin-bottom: 10px; }
.invite-card {
  background: var(--color-white);
  border-radius: 14px;
  padding: 14px 16px;
  display: flex; align-items: center; gap: 12px;
  box-shadow: var(--shadow-card);
  margin-bottom: 10px;
  border-left: 4px solid var(--color-primary);
}
.invite-info { flex: 1; }
.invite-circle { font-size: 15px; font-weight: 700; color: var(--color-text-dark); }
.invite-meta   { font-size: 12px; color: var(--color-text-muted); margin-top: 2px; }
.invite-actions { display: flex; gap: 8px; }
.btn-accept {
  padding: 7px 14px; border-radius: 10px; border: none;
  background: var(--color-primary); color: white;
  font-size: 13px; font-weight: 700; font-family: var(--font-main);
  cursor: pointer; transition: background 0.2s;
}
.btn-accept:hover { background: var(--color-primary-dark); }
.btn-reject {
  padding: 7px 14px; border-radius: 10px;
  border: 2px solid #ef4444; background: none;
  color: #ef4444; font-size: 13px; font-weight: 700;
  font-family: var(--font-main); cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.btn-reject:hover { background: #ef4444; color: white; }

/* ── CIRCLES GRID ─────────────────────────────────────────────── */
.circle-grid { display: flex; flex-direction: column; gap: 12px; }
.circle-card {
  background: var(--color-white);
  border-radius: 16px;
  padding: 16px;
  display: flex; align-items: center; gap: 14px;
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.circle-card:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.1); }
.circle-card__icon {
  width: 48px; height: 48px; border-radius: 14px;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 20px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.circle-card__body { flex: 1; }
.circle-card__name { font-size: 16px; font-weight: 700; color: var(--color-text-dark); }
.circle-card__meta { font-size: 13px; color: var(--color-text-muted); margin-top: 2px; }
.circle-card__arrow { font-size: 22px; color: var(--color-text-muted); }

/* ── EMPTY ────────────────────────────────────────────────────── */
.empty-state { text-align: center; padding: 40px 20px; color: var(--color-text-muted); }
.empty-icon  { font-size: 48px; display: block; margin-bottom: 12px; }
.empty-title { font-size: 17px; font-weight: 700; color: var(--color-text-dark); margin-bottom: 6px; }
.empty-sub   { font-size: 14px; }

/* ── MODALS ───────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: flex-end; justify-content: center;
  z-index: 200; padding: 0;
}
.modal {
  background: var(--color-white);
  border-radius: 24px 24px 0 0;
  padding: 28px 24px 36px;
  width: 100%; max-width: 480px;
  max-height: 90vh; overflow-y: auto;
  display: flex; flex-direction: column; gap: 10px;
  animation: slideUp 0.25s ease;
}
.modal--wide { max-width: 520px; }
@keyframes slideUp {
  from { transform: translateY(40px); opacity: 0; }
  to   { transform: translateY(0);    opacity: 1; }
}
.modal-header { margin-bottom: 4px; }
.modal-title-row { display: flex; align-items: center; gap: 8px; }
.modal-title { font-size: 19px; font-weight: 800; color: var(--color-text-dark); }
.btn-icon-sm { background: none; border: none; font-size: 16px; cursor: pointer; padding: 2px; }

.rename-row { display: flex; gap: 8px; align-items: center; }
.input--sm { padding: 10px 14px; font-size: 14px; margin-bottom: 0; flex: 1; }
.btn-accent-sm {
  padding: 9px 14px; border-radius: 10px; border: none;
  background: var(--color-primary); color: white;
  font-size: 13px; font-weight: 700; font-family: var(--font-main); cursor: pointer;
}
.btn-ghost-sm {
  padding: 9px 14px; border-radius: 10px;
  border: 2px solid var(--color-border); background: none;
  color: var(--color-text-muted); font-size: 13px; font-weight: 600;
  font-family: var(--font-main); cursor: pointer;
}

/* ── MEMBER ROWS ──────────────────────────────────────────────── */
.list-label { font-size: 12px; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: .05em; margin-bottom: 6px; margin-top: 4px; }
.empty-members { font-size: 13px; color: var(--color-text-muted); padding: 8px 0; }
.member-row {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 0; border-bottom: 1px solid var(--color-border);
}
.member-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--color-primary-light); color: var(--color-primary-dark);
  font-size: 14px; font-weight: 800;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.member-info { flex: 1; }
.member-name { font-size: 14px; font-weight: 700; color: var(--color-text-dark); }
.badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 20px; display: inline-block; margin-top: 2px; }
.badge--canview { background: #e0f2fe; color: #0369a1; }
.badge--canedit { background: #dcfce7; color: #15803d; }
.member-controls { display: flex; align-items: center; gap: 6px; }
.select-sm {
  padding: 6px 10px; border-radius: 8px;
  border: 2px solid var(--color-border); background: var(--color-input-bg);
  font-size: 12px; font-family: var(--font-main); color: var(--color-text-dark);
  cursor: pointer;
}
.btn-remove {
  width: 28px; height: 28px; border-radius: 50%; border: none;
  background: #fee2e2; color: #ef4444;
  font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
}
.btn-remove:hover { background: #ef4444; color: white; }

/* ── SENT INVITES ─────────────────────────────────────────────── */
.sent-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--color-border); }
.sent-name { font-size: 14px; font-weight: 600; color: var(--color-text-dark); }
.sent-badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: capitalize; }
.sent-badge--pending  { background: #fef9c3; color: #a16207; }
.sent-badge--accepted { background: #dcfce7; color: #15803d; }
.sent-badge--rejected { background: #fee2e2; color: #b91c1c; }

/* ── SHARED INPUTS / BTNS ─────────────────────────────────────── */
.input {
  width: 100%; padding: 13px 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-input);
  font-size: 16px; font-family: var(--font-main);
  color: #1e293b; background: var(--color-input-bg);
  outline: none; margin-bottom: 0;
  transition: border-color 0.2s; box-sizing: border-box;
}
.input:focus { border-color: var(--color-primary); }
.btn-primary {
  width: 100%; padding: 14px;
  background: var(--color-primary); border: none;
  border-radius: var(--radius-btn);
  color: var(--color-white); font-size: 15px; font-weight: 800;
  font-family: var(--font-main); cursor: pointer; transition: background 0.2s;
}
.btn-primary:hover:not(:disabled) { background: var(--color-primary-dark); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-ghost {
  width: 100%; padding: 12px;
  background: none; border: 2px solid var(--color-border);
  border-radius: var(--radius-btn);
  color: var(--color-text-muted); font-size: 14px; font-weight: 600;
  font-family: var(--font-main); cursor: pointer;
}
.btn-danger {
  width: 100%; padding: 12px;
  background: none; border: 2px solid #ef4444;
  border-radius: var(--radius-btn);
  color: #ef4444; font-size: 15px; font-weight: 700;
  font-family: var(--font-main); cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.btn-danger:hover { background: #ef4444; color: white; }
.error-msg { font-size: 13px; color: #ef4444; font-weight: 600; }
</style>