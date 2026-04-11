<template>
  <div class="tab">
    <h2 class="section-title">My Circle</h2>
    <p class="section-sub">People who can view or manage your medications.</p>

    <div class="empty-state" v-if="familyMembers.length === 0">
      <span class="empty-icon">👨‍👩‍👧</span>
      <p class="empty-title">No members added yet</p>
      <p class="empty-sub">Add a family member or caregiver below.</p>
    </div>

    <div class="member-list" v-else>
      <div class="member-card" v-for="member in familyMembers" :key="member.id">
        <div class="member-card__avatar">{{ member.name.charAt(0).toUpperCase() }}</div>
        <div class="member-card__info">
          <p class="member-card__name">{{ member.name }}</p>
          <div class="badges">
            <span class="badge" :class="{ 'badge--on': member.canView }">👁 View</span>
            <span class="badge" :class="{ 'badge--on': member.canEdit }">✏️ Edit</span>
          </div>
        </div>
        <button class="btn-icon" @click="openEdit(member)">⚙️</button>
      </div>
    </div>

    <div class="form-card">
      <p class="form-title">Add a Member</p>
      <input class="input" type="text" placeholder="Enter their username" v-model="newMemberName" />
      <div class="toggle-row">
        <label class="toggle-label"><input type="checkbox" v-model="newCanView" /> Can View</label>
        <label class="toggle-label"><input type="checkbox" v-model="newCanEdit" /> Can Edit</label>
      </div>
      <button class="btn-primary" @click="addMember">Add to Circle</button>
    </div>

    <div class="modal-overlay" v-if="editingMember" @click.self="editingMember = null">
      <div class="modal">
        <h3 class="modal-title">Edit Permissions</h3>
        <p class="modal-sub">{{ editingMember.name }}</p>
        <div class="toggle-row">
          <label class="toggle-label"><input type="checkbox" v-model="editingMember.canView" /> Can View</label>
          <label class="toggle-label"><input type="checkbox" v-model="editingMember.canEdit" /> Can Edit</label>
        </div>
        <button class="btn-primary" @click="editingMember = null">Save</button>
        <button class="btn-danger" @click="removeMember(editingMember)">Remove Member</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const familyMembers  = ref([])
const newMemberName  = ref('')
const newCanView     = ref(true)
const newCanEdit     = ref(false)
const editingMember  = ref(null)  // null = modal closed

function addMember() {
  if (!newMemberName.value.trim()) {
    alert('Please enter a username.')
    return
  }
  familyMembers.value.push({
    id: Date.now(),
    name: newMemberName.value.trim(),
    canView: newCanView.value,
    canEdit: newCanEdit.value,
  })
  // Reset form
  newMemberName.value = ''
  newCanView.value    = true
  newCanEdit.value    = false
}

function openEdit(member) {
  editingMember.value = member
}

function removeMember(member) {
  familyMembers.value = familyMembers.value.filter(m => m.id !== member.id)
  editingMember.value = null
}
</script>

<style scoped>
.tab { padding: 20px 20px 100px; }
.section-title { font-size: 20px; font-weight: 800; color: var(--color-text-dark); margin-bottom: 4px; }
.section-sub   { font-size: 13px; color: var(--color-text-muted); margin-bottom: 16px; }
.empty-state { text-align: center; padding: 40px 20px; color: var(--color-text-muted); }
.empty-icon  { font-size: 48px; display: block; margin-bottom: 12px; }
.empty-title { font-size: 17px; font-weight: 700; color: var(--color-text-dark); margin-bottom: 6px; }
.empty-sub   { font-size: 14px; }
.member-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.member-card {
  background: var(--color-white);
  border-radius: 14px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: var(--shadow-card);
}
.member-card__avatar {
  width: 42px; height: 42px;
  border-radius: 50%;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 16px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.member-card__info { flex: 1; }
.member-card__name { font-size: 15px; font-weight: 700; color: var(--color-text-dark); }
.badges { display: flex; gap: 6px; margin-top: 4px; }
.badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 20px; background: #e2e8f0; color: #94a3b8; }
.badge--on { background: var(--color-primary-light); color: var(--color-primary-dark); }
.btn-icon { background: none; border: none; font-size: 20px; cursor: pointer; padding: 4px; }
.form-card { background: var(--color-white); border-radius: 16px; padding: 20px; box-shadow: var(--shadow-card); }
.form-title { font-size: 15px; font-weight: 700; color: var(--color-text-dark); margin-bottom: 12px; }
.input {
  width: 100%;
  padding: 13px 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-input);
  font-size: 16px;
  font-family: var(--font-main);
  color: #1e293b;
  background: var(--color-input-bg);
  outline: none;
  margin-bottom: 12px;
  transition: border-color 0.2s;
}
.input:focus { border-color: var(--color-primary); }
.toggle-row { display: flex; gap: 20px; margin-bottom: 14px; }
.toggle-label { display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; color: var(--color-text-body); cursor: pointer; }
.btn-primary { width: 100%; padding: 14px; background: var(--color-primary); border: none; border-radius: var(--radius-btn); color: var(--color-white); font-size: 15px; font-weight: 800; font-family: var(--font-main); cursor: pointer; transition: background 0.2s; }
.btn-primary:hover { background: var(--color-primary-dark); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 20px; }
.modal { background: var(--color-white); border-radius: 20px; padding: 28px 24px; width: 100%; max-width: 340px; }
.modal-title { font-size: 18px; font-weight: 800; color: var(--color-text-dark); margin-bottom: 4px; }
.modal-sub   { font-size: 14px; color: var(--color-text-muted); margin-bottom: 16px; }
.btn-danger { width: 100%; padding: 12px; background: none; border: 2px solid #ef4444; border-radius: var(--radius-btn); color: #ef4444; font-size: 15px; font-weight: 700; font-family: var(--font-main); cursor: pointer; margin-top: 10px; transition: background 0.2s, color 0.2s; }
.btn-danger:hover { background: #ef4444; color: white; }
</style>