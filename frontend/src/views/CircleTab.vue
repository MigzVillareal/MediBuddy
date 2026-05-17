<template>
  <div class="tab">

    <!-- ── PENDING INVITES (received) ──────────────────────────────────── -->
    <section v-if="pendingInvites.length > 0" class="pending-section">
      <h3 class="section-label">🔔 Pending Invites</h3>
      <div class="invite-card" v-for="inv in pendingInvites" :key="inv.circle_member_id">
        <div class="invite-info">
          <p class="invite-circle">{{ inv.circle_name }}</p>
          <p class="invite-meta">
            from <strong>{{ inv.inviter_username }}</strong>
            · <span class="perm-chip" :class="'perm--' + inv.permission">{{ permLabel(inv.permission) }}</span>
          </p>
        </div>
        <div class="invite-actions">
          <button class="btn-accept" @click="respondInvite(inv.circle_member_id, 'accept')">Accept</button>
          <button class="btn-reject" @click="respondInvite(inv.circle_member_id, 'reject')">Reject</button>
        </div>
      </div>
    </section>

    <!-- ── MY CIRCLES header ───────────────────────────────────────────── -->
    <div class="header-row">
      <div>
        <h2 class="section-title">My Circles</h2>
        <p class="section-sub">Groups of people who can view or manage your medications.</p>
      </div>
      <button class="btn-new" @click="openCreate">+ New Circle</button>
    </div>

    <!-- empty state -->
    <div class="empty-state" v-if="circles.length === 0">
      <span class="empty-icon">👨‍👩‍👧</span>
      <p class="empty-title">No circles yet</p>
      <p class="empty-sub">Create a circle and invite family or caregivers.</p>
    </div>

    <!-- circle cards -->
    <div class="circle-grid" v-else>
      <div
        class="circle-card"
        v-for="c in circles"
        :key="c.circle_id"
        @click="openDetail(c)"
      >
        <div class="circle-card__icon">{{ (c.circle_name || '?').charAt(0).toUpperCase() }}</div>
        <div class="circle-card__body">
          <p class="circle-card__name">{{ c.circle_name }}</p>
          <p class="circle-card__meta">
            {{ c.member_count }} member{{ c.member_count !== 1 ? 's' : '' }}
            <template v-if="c.pending_count > 0">
              · <span class="pending-chip">{{ c.pending_count }} pending</span>
            </template>
          </p>
        </div>
        <span class="circle-card__arrow">›</span>
      </div>
    </div>
    
<!-- ── JOINED CIRCLES ──────────────────────────────────────────────── -->
    <template v-if="joinedCircles.length > 0">
      <div class="header-row" style="margin-top: 28px;">
        <div>
          <h2 class="section-title">Circles I've Joined</h2>
          <p class="section-sub">Circles you are a member of.</p>
        </div>
      </div>
      <div class="circle-grid">
        <div
          class="circle-card"
          v-for="c in joinedCircles"
          :key="c.circle_id"
          @click="openDetail(c)"
        >
          <div class="circle-card__icon">{{ (c.circle_name || '?').charAt(0).toUpperCase() }}</div>
          <div class="circle-card__body">
            <p class="circle-card__name">{{ c.circle_name }}</p>
            <p class="circle-card__meta">
              {{ c.member_count }} member{{ c.member_count !== 1 ? 's' : '' }}
              · owned by <strong>{{ c.owner_username }}</strong>
              · <span class="perm-chip" :class="'perm--' + c.permission">{{ permLabel(c.permission) }}</span>
            </p>
          </div>
          <span class="circle-card__arrow">›</span>
        </div>
      </div>
    </template>
    

    <!-- ── CREATE CIRCLE MODAL ─────────────────────────────────────────── -->
    <Teleport to="body">
      <div class="overlay" v-if="showCreate" @click.self="showCreate = false">
        <div class="sheet">
          <div class="sheet-handle"></div>
          <h3 class="sheet-title">Create a Circle</h3>
          <p v-if="createError" class="err">{{ createError }}</p>
          <input
            id="new-circle-name"
            class="field"
            type="text"
            placeholder="Circle name (e.g. Family)"
            v-model="newCircleName"
            @keyup.enter="createCircle"
            autofocus
          />
          <button class="btn-primary" @click="createCircle" :disabled="isCreating">
            {{ isCreating ? 'Creating…' : 'Create Circle' }}
          </button>
          <button class="btn-ghost" @click="showCreate = false">Cancel</button>
        </div>
      </div>
    </Teleport>

    <!-- ── CIRCLE DETAIL SHEET ─────────────────────────────────────────── -->
    <Teleport to="body">
      <div class="overlay" v-if="activeCircle" @click.self="closeDetail">
        <div class="sheet sheet--tall">
          <div class="sheet-handle"></div>

          <!-- title / rename -->
          <div v-if="!renaming" class="sheet-title-row">
            <h3 class="sheet-title">{{ activeCircle.circle_name }}</h3>
            <button class="btn-icon" @click="startRename" title="Rename">✏️</button>
            <button class="btn-icon btn-icon--danger" @click="deleteCircle" title="Delete circle">🗑</button>
          </div>
          <div v-else class="rename-row">
            <input class="field field--sm" v-model="renameValue" @keyup.enter="saveRename" />
            <button class="btn-accent" @click="saveRename">Save</button>
            <button class="btn-ghost-sm" @click="renaming = false">✕</button>
          </div>
          <p v-if="detailError" class="err">{{ detailError }}</p>

          <!-- ── Members ── -->
          <p class="list-label">Members</p>
          <p class="empty-members" v-if="activeMembers.length === 0">
            No accepted members yet.
          </p>
          <div class="member-row" v-for="m in activeMembers" :key="m.user_id">
            <div class="m-avatar">{{ m.username.charAt(0).toUpperCase() }}</div>
            <div class="m-info">
              <p class="m-name">{{ m.username }}</p>
            </div>
            <select class="perm-select" v-model="m.permission" @change="updatePerm(m)">
              <option value="canview">👁 View</option>
              <option value="canedit">✏️ Edit</option>
            </select>
            <button class="btn-remove" @click="removeMember(m)" title="Remove">✕</button>
          </div>

          <!-- ── Sent invites for this circle ── -->
          <template v-if="sentForCircle.length > 0">
            <p class="list-label" style="margin-top:12px">Sent Invites</p>
            <div class="sent-row" v-for="s in sentForCircle" :key="s.circle_member_id">
              <span class="m-name">{{ s.invitee_username }}</span>
              <span class="status-chip" :class="'status--' + s.status">{{ s.status }}</span>
            </div>
          </template>

          <!-- ── Invite a Member ── -->
          <p class="list-label" style="margin-top:16px">Invite a Member</p>
          <p v-if="inviteError" class="err">{{ inviteError }}</p>
          <input
            id="invite-username"
            class="field field--sm"
            type="text"
            placeholder="Their username"
            v-model="inviteUsername"
          />
          <select class="field field--sm" v-model="invitePermission">
            <option value="canview">👁 View Only</option>
            <option value="canedit">✏️ Can Edit</option>
          </select>
          <button class="btn-primary" @click="sendInvite" :disabled="isSending">
            {{ isSending ? 'Sending…' : 'Send Invite' }}
          </button>

          <button class="btn-ghost" @click="closeDetail" style="margin-top:4px">Close</button>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'

// ── STATE ──────────────────────────────────────────────────────────
const circles        = ref([])
const pendingInvites = ref([])
const sentInvites    = ref([])

// create circle modal
const showCreate    = ref(false)
const newCircleName = ref('')
const createError   = ref('')
const isCreating    = ref(false)

// detail sheet
const activeCircle  = ref(null)
const activeMembers = ref([])
const detailError   = ref('')

// rename
const renaming    = ref(false)
const renameValue = ref('')

// invite form
const inviteUsername   = ref('')
const invitePermission = ref('canview')
const inviteError      = ref('')
const isSending        = ref(false)

// sent invites filtered to the currently open circle
const sentForCircle = computed(() =>
  activeCircle.value
    ? sentInvites.value.filter(s => s.circle_id === activeCircle.value.circle_id)
    : []
)

const joinedCircles = ref([])

// ── HELPERS ────────────────────────────────────────────────────────
function permLabel(p) {
  return p === 'canedit' ? '✏️ Can Edit' : '👁 View Only'
}

// ── INIT ───────────────────────────────────────────────────────────
onMounted(() => Promise.all([loadCircles(), loadJoinedCircles(), loadPendingInvites(), loadSentInvites()]))

async function loadJoinedCircles() {
  try { joinedCircles.value = (await api.get('/circle/joined')).data }
  catch (e) { console.error('loadJoinedCircles', e) }
}

async function loadCircles() {
  try { circles.value = (await api.get('/circle/mine')).data }
  catch (e) { console.error('loadCircles', e) }
}

async function loadPendingInvites() {
  try { pendingInvites.value = (await api.get('/circle/invites/pending')).data }
  catch (e) { console.error('loadPendingInvites', e) }
}

async function loadSentInvites() {
  try { sentInvites.value = (await api.get('/circle/invites/sent')).data }
  catch (e) { console.error('loadSentInvites', e) }
}

// ── CREATE ─────────────────────────────────────────────────────────
function openCreate() {
  newCircleName.value = ''
  createError.value   = ''
  showCreate.value    = true
}

async function createCircle() {
  createError.value = ''
  if (!newCircleName.value.trim()) { createError.value = 'Please enter a name.'; return }
  isCreating.value = true
  try {
    await api.post('/circle/create', { circle_name: newCircleName.value.trim() })
    showCreate.value = false
    await loadCircles()
  } catch (e) {
    createError.value = e.response?.data?.error || 'Failed to create circle.'
  } finally { isCreating.value = false }
}

// ── DETAIL ─────────────────────────────────────────────────────────
async function openDetail(c) {
  activeCircle.value = { ...c }
  detailError.value  = ''
  inviteUsername.value = ''
  inviteError.value    = ''
  renaming.value       = false
  await Promise.all([loadMembers(), loadSentInvites()])
}

function closeDetail() {
  activeCircle.value  = null
  activeMembers.value = []
}

async function loadMembers() {
  if (!activeCircle.value) return
  try {
    activeMembers.value = (await api.get(`/circle/${activeCircle.value.circle_id}/members`)).data
  } catch (e) { console.error('loadMembers', e) }
}

// ── RENAME ─────────────────────────────────────────────────────────
function startRename() {
  renameValue.value = activeCircle.value.circle_name
  renaming.value    = true
}

async function saveRename() {
  if (!renameValue.value.trim()) return
  try {
    const res = await api.put(`/circle/${activeCircle.value.circle_id}/rename`, {
      circle_name: renameValue.value.trim()
    })
    activeCircle.value.circle_name = res.data.circle_name
    renaming.value = false
    await loadCircles()
  } catch (e) { detailError.value = e.response?.data?.error || 'Rename failed.' }
}

// ── DELETE ─────────────────────────────────────────────────────────
async function deleteCircle() {
  if (!confirm(`Delete "${activeCircle.value.circle_name}"? This cannot be undone.`)) return
  try {
    await api.delete(`/circle/${activeCircle.value.circle_id}`)
    closeDetail()
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
      circle_id:  activeCircle.value.circle_id,
      username:   inviteUsername.value.trim(),
      permission: invitePermission.value,
    })
    inviteUsername.value = ''
    invitePermission.value = 'canview'
    await Promise.all([loadSentInvites(), loadCircles()])
  } catch (e) {
    inviteError.value = e.response?.data?.error || 'Failed to send invite.'
  } finally { isSending.value = false }
}

// ── RESPOND ────────────────────────────────────────────────────────
async function respondInvite(circleMemberId, action) {
  try {
    await api.post(`/circle/invite/${circleMemberId}/respond`, { action })
    await Promise.all([loadPendingInvites(), loadCircles()])
  } catch (e) { console.error('respondInvite', e) }
}

// ── PERMISSION ─────────────────────────────────────────────────────
async function updatePerm(member) {
  try {
    await api.post('/circle/update_permission', {
      circle_id:  activeCircle.value.circle_id,
      user_id:    member.user_id,
      permission: member.permission,
    })
  } catch (e) { detailError.value = e.response?.data?.error || 'Update failed.' }
}

// ── REMOVE ─────────────────────────────────────────────────────────
async function removeMember(member) {
  if (!confirm(`Remove ${member.username} from this circle?`)) return
  try {
    await api.post('/circle/remove_member', {
      circle_id: activeCircle.value.circle_id,
      user_id:   member.user_id,
    })
    await Promise.all([loadMembers(), loadCircles()])
  } catch (e) { detailError.value = e.response?.data?.error || 'Remove failed.' }
}
</script>

<style scoped>
/* ─── layout ─────────────────────────────────────────────────────── */
.tab { padding: 20px 20px 100px; }

/* ─── header row ──────────────────────────────────────────────────── */
.header-row {
  display: flex; align-items: flex-start;
  justify-content: space-between; gap: 12px;
  margin-bottom: 18px;
}
.section-title { font-size: 20px; font-weight: 800; color: var(--color-text-dark); margin-bottom: 2px; }
.section-sub   { font-size: 13px; color: var(--color-text-muted); }

/* ─── pending invites ─────────────────────────────────────────────── */
.pending-section { margin-bottom: 24px; }
.section-label {
  font-size: 12px; font-weight: 700; color: var(--color-text-muted);
  text-transform: uppercase; letter-spacing: .06em; margin-bottom: 10px;
}
.invite-card {
  background: var(--color-white);
  border-left: 4px solid var(--color-primary);
  border-radius: 14px; padding: 14px 16px;
  display: flex; align-items: center; gap: 12px;
  box-shadow: var(--shadow-card); margin-bottom: 10px;
}
.invite-info   { flex: 1; }
.invite-circle { font-size: 15px; font-weight: 700; color: var(--color-text-dark); }
.invite-meta   { font-size: 12px; color: var(--color-text-muted); margin-top: 3px; }
.invite-actions { display: flex; gap: 8px; flex-shrink: 0; }
.perm-chip {
  display: inline-block; font-size: 11px; font-weight: 600;
  padding: 2px 8px; border-radius: 20px;
}
.perm--canview { background: #e0f2fe; color: #0369a1; }
.perm--canedit { background: #dcfce7; color: #15803d; }

/* ─── circle grid ─────────────────────────────────────────────────── */
.circle-grid { display: flex; flex-direction: column; gap: 12px; }
.circle-card {
  background: var(--color-white);
  border-radius: 16px; padding: 16px;
  display: flex; align-items: center; gap: 14px;
  box-shadow: var(--shadow-card); cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.circle-card:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.1); }
.circle-card__icon {
  width: 48px; height: 48px; border-radius: 14px; flex-shrink: 0;
  background: var(--color-primary-light); color: var(--color-primary-dark);
  font-size: 20px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
}
.circle-card__body { flex: 1; }
.circle-card__name { font-size: 16px; font-weight: 700; color: var(--color-text-dark); }
.circle-card__meta { font-size: 13px; color: var(--color-text-muted); margin-top: 2px; }
.circle-card__arrow { font-size: 22px; color: var(--color-text-muted); }
.pending-chip { color: #b45309; background: #fef3c7; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 20px; }

/* ─── empty ───────────────────────────────────────────────────────── */
.empty-state { text-align: center; padding: 40px 20px; color: var(--color-text-muted); }
.empty-icon  { font-size: 48px; display: block; margin-bottom: 12px; }
.empty-title { font-size: 17px; font-weight: 700; color: var(--color-text-dark); margin-bottom: 6px; }
.empty-sub   { font-size: 14px; }

/* ─── overlay + sheet ─────────────────────────────────────────────── */
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: flex-end; justify-content: center;
  z-index: 300; padding: 0;
}
.sheet {
  background: var(--color-white);
  border-radius: 24px 24px 0 0;
  padding: 12px 24px 40px;
  width: 100%; max-width: 500px;
  max-height: 85vh; overflow-y: auto;
  display: flex; flex-direction: column; gap: 10px;
  animation: slideUp .22s ease;
}
.sheet--tall { max-height: 92vh; }
.sheet-handle {
  width: 40px; height: 4px; background: #cbd5e1;
  border-radius: 2px; margin: 0 auto 8px;
  flex-shrink: 0;
}
@keyframes slideUp {
  from { transform: translateY(36px); opacity: 0; }
  to   { transform: translateY(0);    opacity: 1; }
}

/* ─── sheet internals ─────────────────────────────────────────────── */
.sheet-title     { font-size: 19px; font-weight: 800; color: var(--color-text-dark); }
.sheet-title-row { display: flex; align-items: center; gap: 8px; }
.rename-row      { display: flex; align-items: center; gap: 8px; }
.list-label {
  font-size: 11px; font-weight: 700; color: var(--color-text-muted);
  text-transform: uppercase; letter-spacing: .06em; margin-bottom: 4px; margin-top: 4px;
}
.empty-members { font-size: 13px; color: var(--color-text-muted); }

/* ─── member rows ─────────────────────────────────────────────────── */
.member-row {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 0; border-bottom: 1px solid var(--color-border);
}
.m-avatar {
  width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
  background: var(--color-primary-light); color: var(--color-primary-dark);
  font-size: 14px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
}
.m-info { flex: 1; }
.m-name { font-size: 14px; font-weight: 700; color: var(--color-text-dark); }
.perm-select {
  padding: 6px 10px; border-radius: 8px;
  border: 2px solid var(--color-border);
  background: var(--color-input-bg);
  font-size: 12px; font-family: var(--font-main);
  color: var(--color-text-dark); cursor: pointer;
}

/* ─── sent invites ────────────────────────────────────────────────── */
.sent-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 0; border-bottom: 1px solid var(--color-border);
}
.status-chip {
  font-size: 11px; font-weight: 700; padding: 3px 10px;
  border-radius: 20px; text-transform: capitalize;
}
.status--pending  { background: #fef9c3; color: #a16207; }
.status--accepted { background: #dcfce7; color: #15803d; }
.status--rejected { background: #fee2e2; color: #b91c1c; }

/* ─── fields ──────────────────────────────────────────────────────── */
.field {
  width: 100%; padding: 13px 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-input);
  font-size: 15px; font-family: var(--font-main);
  color: #1e293b; background: var(--color-input-bg);
  outline: none; box-sizing: border-box;
  transition: border-color .2s;
}
.field:focus { border-color: var(--color-primary); }
.field--sm { padding: 10px 14px; font-size: 14px; flex: 1; }

/* ─── buttons ─────────────────────────────────────────────────────── */
.btn-new {
  flex-shrink: 0; padding: 10px 16px;
  background: var(--color-primary); color: var(--color-white);
  border: none; border-radius: 12px;
  font-size: 14px; font-weight: 700; font-family: var(--font-main);
  cursor: pointer; white-space: nowrap; transition: background .2s;
}
.btn-new:hover { background: var(--color-primary-dark); }

.btn-primary {
  width: 100%; padding: 14px;
  background: var(--color-primary); border: none;
  border-radius: var(--radius-btn);
  color: var(--color-white); font-size: 15px; font-weight: 800;
  font-family: var(--font-main); cursor: pointer; transition: background .2s;
}
.btn-primary:hover:not(:disabled) { background: var(--color-primary-dark); }
.btn-primary:disabled { opacity: .6; cursor: not-allowed; }

.btn-ghost {
  width: 100%; padding: 12px;
  background: none; border: 2px solid var(--color-border);
  border-radius: var(--radius-btn);
  color: var(--color-text-muted); font-size: 14px; font-weight: 600;
  font-family: var(--font-main); cursor: pointer;
}
.btn-accept {
  padding: 7px 14px; border-radius: 10px; border: none;
  background: var(--color-primary); color: white;
  font-size: 13px; font-weight: 700; font-family: var(--font-main);
  cursor: pointer; transition: background .2s;
}
.btn-accept:hover { background: var(--color-primary-dark); }
.btn-reject {
  padding: 7px 14px; border-radius: 10px;
  border: 2px solid #ef4444; background: none;
  color: #ef4444; font-size: 13px; font-weight: 700;
  font-family: var(--font-main); cursor: pointer;
  transition: background .2s, color .2s;
}
.btn-reject:hover { background: #ef4444; color: white; }

.btn-icon {
  background: none; border: none;
  font-size: 17px; cursor: pointer; padding: 4px; line-height: 1;
}
.btn-icon--danger { margin-left: auto; }

.btn-accent {
  padding: 9px 14px; border-radius: 10px; border: none;
  background: var(--color-primary); color: white;
  font-size: 13px; font-weight: 700; font-family: var(--font-main); cursor: pointer;
}
.btn-ghost-sm {
  padding: 9px 12px; border-radius: 10px;
  border: 2px solid var(--color-border); background: none;
  color: var(--color-text-muted); font-size: 13px; font-weight: 600;
  font-family: var(--font-main); cursor: pointer;
}
.btn-remove {
  width: 28px; height: 28px; border-radius: 50%; border: none; flex-shrink: 0;
  background: #fee2e2; color: #ef4444; font-size: 13px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background .2s;
}
.btn-remove:hover { background: #ef4444; color: white; }

.err { font-size: 13px; color: #ef4444; font-weight: 600; }
</style>