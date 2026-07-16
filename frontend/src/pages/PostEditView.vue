<template>
  <div class="write-shell">
    <header class="write-header">
      <button type="button" class="text-btn" @click="handleCancel">{{ $t('common.actions.cancel') }}</button>
      <span class="write-title">{{ isEdit ? $t('board.editPostTitle') : $t('board.writePostTitle') }}</span>
      <span class="header-spacer" aria-hidden="true"></span>
    </header>

    <div class="write-body">
      <div class="write-subtitle">{{ $t('board.writeSubtitle') }}</div>
      <input v-model="title" class="title-input" :placeholder="$t('board.titlePlaceholder')" />
      <textarea
        v-model="content"
        class="content-input"
        :placeholder="$t('board.contentPlaceholder')"
      ></textarea>

      <div class="attach-row">
        <label class="attach-btn" for="imageFile">{{ $t('board.attachPhoto') }}</label>
        <input id="imageFile" type="file" accept="image/*" hidden @change="handleImageUpload" />
        <span v-if="uploading" class="helper-text">{{ $t('board.uploading') }}</span>
        <span v-else-if="uploadError" class="helper-text error">{{ uploadError }}</span>
        <span v-else-if="imageUrl" class="helper-text">{{ $t('board.imageAttached') }}</span>
      </div>
      <img v-if="imageUrl" :src="resolvedImageUrl" class="preview-image" :alt="$t('board.imagePreviewAlt')" />
    </div>

    <footer class="write-footer">
      <button type="button" class="footer-btn cancel" @click="handleCancel">{{ $t('common.actions.cancel') }}</button>
      <button type="button" class="footer-btn submit" :disabled="submitDisabled" @click="openAuthModal">{{ $t('common.actions.submit') }}</button>
    </footer>
  </div>

  <div v-if="showAuthModal" class="modal-backdrop" @click.self="closeAuthModal">
    <div class="auth-modal panel-card">
      <h4>{{ isEdit ? $t('board.confirmPasswordTitle') : $t('board.authorInfoTitle') }}</h4>

      <div v-if="!isEdit" class="form-group">
        <label for="authorInput">{{ $t('board.nicknameLabel') }}</label>
        <input id="authorInput" v-model="authorInput" class="form-control" :placeholder="$t('board.nicknamePlaceholder')" />
      </div>
      <div class="form-group">
        <label for="passwordInput">{{ $t('board.passwordLabel') }}</label>
        <input
          id="passwordInput"
          v-model="passwordInput"
          type="password"
          class="form-control"
          :placeholder="$t('board.passwordInputPlaceholder')"
          @keyup.enter="confirmAuthModal"
        />
      </div>
      <p v-if="authError" class="helper-text error">{{ authError }}</p>

      <div class="modal-actions">
        <button type="button" class="footer-btn cancel" @click="closeAuthModal">{{ $t('common.actions.cancel') }}</button>
        <button type="button" class="footer-btn submit" @click="confirmAuthModal">{{ $t('common.actions.confirm') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useMapStore } from '@/stores/mapStore'
import api from '../api'

const route = useRoute()
const router = useRouter()
const mapStore = useMapStore()
const { t } = useI18n()

const isEdit = computed(() => !!route.params.id)
const title = ref('')
const content = ref('')
const imageUrl = ref('')
const uploading = ref(false)
const uploadError = ref('')

const showAuthModal = ref(false)
const authorInput = ref('')
const passwordInput = ref('')
const authError = ref('')

const submitDisabled = computed(() => !title.value.trim() || !content.value.trim())

// 백엔드가 /uploads/... 상대경로를 반환하므로, 프론트 origin이 아닌 백엔드 origin 기준으로 풀어줘야 함
const resolvedImageUrl = computed(() => {
  if (!imageUrl.value) return ''
  if (/^https?:\/\//.test(imageUrl.value)) return imageUrl.value
  return `${import.meta.env.VITE_API_BASE_URL}${imageUrl.value}`
})

const fetchPost = async () => {
  if (!isEdit.value) return
  const { data } = await api.get(`/posts/${route.params.id}`)
  title.value = data.title
  content.value = data.content
  imageUrl.value = data.image_url || ''
}

const handleImageUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  uploading.value = true
  uploadError.value = ''
  try {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post('/posts/upload-image', formData)
    imageUrl.value = data.image_url
  } catch (err) {
    uploadError.value = t('board.imageUploadError')
  } finally {
    uploading.value = false
  }
}

const openAuthModal = () => {
  if (submitDisabled.value) return
  authorInput.value = ''
  passwordInput.value = ''
  authError.value = ''
  showAuthModal.value = true
}

const closeAuthModal = () => {
  showAuthModal.value = false
}

const confirmAuthModal = async () => {
  if (!isEdit.value && !authorInput.value.trim()) {
    authError.value = t('board.nicknameRequiredError')
    return
  }
  if (!passwordInput.value) {
    authError.value = t('board.passwordRequiredError')
    return
  }

  try {
    if (isEdit.value) {
      await api.put(`/posts/${route.params.id}`, {
        title: title.value,
        content: content.value,
        password: passwordInput.value
      })
    } else {
      const locId = route.params.location_id || mapStore.selectedLocation?.id
      await api.post('/posts/', {
        title: title.value,
        content: content.value,
        author: authorInput.value,
        password: passwordInput.value,
        image_url: imageUrl.value || null,
        location_id: locId || null
      })
    }
    showAuthModal.value = false
    router.push(`/locations/${route.params.location_id}/posts`)
  } catch (err) {
    authError.value = err.response?.status === 403 ? t('board.passwordMismatchError') : t('board.saveError')
  }
}

const handleCancel = () => {
  if (isEdit.value) {
    router.push(`/locations/${route.params.location_id}/posts/${route.params.id}`)
  } else {
    router.push(`/locations/${route.params.location_id}/posts`)
  }
}

onMounted(fetchPost)
</script>

<style scoped>
.write-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  padding: 0;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(248, 245, 239, 0.96));
}

.write-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 13px 14px;
  border-bottom: 1px solid var(--border-color);
  flex: none;
}

.text-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13.5px;
  color: var(--text-secondary);
  padding: 0;
}

.write-title {
  font-weight: 800;
  font-size: 15px;
}

.header-spacer {
  width: 36px;
}

.write-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding: 16px 18px;
}

.write-subtitle {
  font-size: 12px;
  color: var(--text-muted);
}

.title-input {
  width: 100%;
  border: none;
  border-bottom: 1px solid var(--border-color);
  background: transparent;
  padding: 12px 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  outline: none;
  margin-top: 12px;
  transition: border-color 0.2s ease;
}

.title-input:focus {
  border-bottom-color: var(--accent);
}

.content-input {
  width: 100%;
  border: none;
  background: transparent;
  outline: none;
  resize: none;
  flex: 1;
  min-height: 230px;
  font-size: 14.5px;
  line-height: 1.7;
  color: #2a2825;
  margin-top: 14px;
}

.attach-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px dashed var(--border-color);
  flex: none;
}

.attach-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
  background: var(--surface-muted);
  padding: 8px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.attach-btn:hover {
  background: #eeece5;
}

.preview-image {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border-radius: 14px;
  margin-top: 12px;
  border: 1px solid var(--border-color);
  flex: none;
}

.write-footer {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  flex: none;
}

.footer-btn {
  border: none;
  border-radius: 11px;
  padding: 13px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
}

.footer-btn.cancel {
  flex: 1;
  background: #f2f1ed;
  color: var(--text-secondary);
}

.footer-btn.submit {
  flex: 2;
  background: var(--accent);
  color: #fff;
}

.footer-btn.submit:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(28, 27, 26, 0.42);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.auth-modal {
  width: min(360px, 90vw);
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.auth-modal h4 {
  margin: 0;
  font-size: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--text-primary);
}

.modal-actions {
  display: flex;
  gap: 0.6rem;
  margin-top: 0.2rem;
}

.modal-actions .footer-btn {
  padding: 11px;
}
</style>
