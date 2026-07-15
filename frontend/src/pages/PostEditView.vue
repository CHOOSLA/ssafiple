<template>
  <div class="write-shell">
    <header class="write-header">
      <button type="button" class="text-btn" @click="handleCancel">취소</button>
      <span class="write-title">{{ isEdit ? '게시글 수정' : '글쓰기' }}</span>
      <span class="header-spacer" aria-hidden="true"></span>
    </header>

    <div class="write-body">
      <div class="write-subtitle">자유게시판에 남기는 글 · 익명</div>
      <input v-model="title" class="title-input" placeholder="제목" />
      <textarea
        v-model="content"
        class="content-input"
        placeholder="내용을 입력하세요. 로그인 없이 익명으로 등록됩니다."
      ></textarea>

      <div class="attach-row">
        <label class="attach-btn" for="imageFile">📷 사진 첨부</label>
        <input id="imageFile" type="file" accept="image/*" hidden @change="handleImageUpload" />
        <span v-if="uploading" class="helper-text">업로드 중...</span>
        <span v-else-if="uploadError" class="helper-text error">{{ uploadError }}</span>
        <span v-else-if="imageUrl" class="helper-text">이미지 첨부됨</span>
      </div>
      <img v-if="imageUrl" :src="imageUrl" class="preview-image" alt="첨부 이미지 미리보기" />
    </div>

    <footer class="write-footer">
      <button type="button" class="footer-btn cancel" @click="handleCancel">취소</button>
      <button type="button" class="footer-btn submit" :disabled="submitDisabled" @click="openAuthModal">등록</button>
    </footer>
  </div>

  <div v-if="showAuthModal" class="modal-backdrop" @click.self="closeAuthModal">
    <div class="auth-modal panel-card">
      <h4>{{ isEdit ? '비밀번호 확인' : '작성자 정보' }}</h4>

      <div v-if="!isEdit" class="form-group">
        <label for="authorInput">닉네임</label>
        <input id="authorInput" v-model="authorInput" class="form-control" placeholder="닉네임을 입력하세요" />
      </div>
      <div class="form-group">
        <label for="passwordInput">비밀번호</label>
        <input
          id="passwordInput"
          v-model="passwordInput"
          type="password"
          class="form-control"
          placeholder="비밀번호를 입력하세요"
          @keyup.enter="confirmAuthModal"
        />
      </div>
      <p v-if="authError" class="helper-text error">{{ authError }}</p>

      <div class="modal-actions">
        <button type="button" class="footer-btn cancel" @click="closeAuthModal">취소</button>
        <button type="button" class="footer-btn submit" @click="confirmAuthModal">확인</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()

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
    uploadError.value = '이미지 업로드에 실패했습니다.'
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
    authError.value = '닉네임을 입력하세요.'
    return
  }
  if (!passwordInput.value) {
    authError.value = '비밀번호를 입력하세요.'
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
      await api.post('/posts/', {
        title: title.value,
        content: content.value,
        author: authorInput.value,
        password: passwordInput.value,
        image_url: imageUrl.value || null
      })
    }
    showAuthModal.value = false
    router.push('/posts')
  } catch (err) {
    authError.value = err.response?.status === 403 ? '비밀번호가 일치하지 않습니다.' : '저장에 실패했습니다.'
  }
}

const handleCancel = () => {
  if (isEdit.value) {
    router.push(`/posts/${route.params.id}`)
  } else {
    router.push('/posts')
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
  background: #f4f2ee;
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
