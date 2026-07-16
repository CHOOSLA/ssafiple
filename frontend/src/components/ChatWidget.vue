<template>
  <div>
    <!-- 펼침: 대화창 -->
    <div v-if="chat.isOpen" class="chat-panel anim-pop">
      <div class="chat-header">
        <span class="chat-title">SSAFIPLE AI</span>
        <button class="close-btn" type="button" :aria-label="$t('chat.closeAria')" @click="chat.toggleOpen">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M2 2L14 14M14 2L2 14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
          </svg>
        </button>
      </div>

      <div ref="messageListEl" class="message-list">
        <div
          v-for="m in chat.messages"
          :key="m.id"
          class="message-row"
          :class="m.sender"
        >
          <div class="bubble">{{ m.textKey ? $t(m.textKey) : m.text }}</div>
          <div v-if="m.locations && m.locations.length" class="place-chips">
            <button
              v-for="loc in m.locations"
              :key="loc.id"
              type="button"
              class="place-chip"
              @click="chat.focusOnLocation(loc)"
            >
              📍 {{ locale === 'en' ? loc.name_en || loc.name : loc.name }}
            </button>
          </div>
        </div>

        <div v-if="chat.isLoading" class="message-row ai">
          <div class="bubble anim-typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="quick-actions">
        <button
          v-for="action in QUICK_ACTIONS"
          :key="action.query"
          type="button"
          class="quick-chip"
          :disabled="chat.isLoading"
          @click="handleQuickAction(action.query)"
        >
          {{ action.label }}
        </button>
      </div>

      <form class="input-area" @submit.prevent="handleSend">
        <div class="input-wrapper">
          <input
            v-model="draft"
            class="input-rounded"
            type="text"
            :placeholder="$t('chat.messagePlaceholder')"
            :disabled="chat.isLoading"
          />
        </div>
        <button class="send-btn" type="submit" :aria-label="$t('chat.sendAria')" :disabled="chat.isLoading || !draft.trim()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#fff">
            <polygon points="4,3 22,12 4,21 4,14 15,12 4,10" />
          </svg>
        </button>
      </form>
    </div>

    <!-- 접힘: 플로팅 버튼 -->
    <button v-else class="fab" type="button" :aria-label="$t('chat.openAria')" @click="chat.toggleOpen">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path
          d="M4 4h16v11H8l-4 4V4z"
          stroke="#fff"
          stroke-width="1.8"
          stroke-linejoin="round"
        />
      </svg>
    </button>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useChatStore } from '../stores/chat'

// 추천 칩은 표시 라벨을 그대로 질의로 전송한다 — EN 모드에서는 영어 질문이 가고,
// 백엔드가 lang 파라미터에 맞춰 영어로 답변한다 (장소 검색은 다국어 임베딩으로 동작).
const { t, locale } = useI18n()
const QUICK_ACTIONS = computed(() =>
  [1, 2, 3].map((idx) => {
    const label = t(`chat.quickAction${idx}`)
    return { query: label, label }
  })
)

const chat = useChatStore()
const draft = ref('')
const messageListEl = ref(null)

const scrollToBottom = () => {
  nextTick(() => {
    const el = messageListEl.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

watch(() => chat.messages.length, scrollToBottom)
watch(() => chat.isLoading, scrollToBottom)
watch(() => chat.isOpen, (open) => {
  if (open) scrollToBottom()
})

const handleSend = async () => {
  const text = draft.value
  draft.value = ''
  await chat.sendMessage(text)
}

const handleQuickAction = (query) => {
  if (chat.isLoading) return
  chat.sendMessage(query)
}
</script>

<style scoped>
.fab {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: var(--accent);
  box-shadow: 0 4px 12px rgba(241, 91, 76, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.chat-panel {
  width: 360px;
  height: 520px;
  background: var(--surface);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.anim-pop {
  animation: lh-pop 0.5s ease both;
}

.chat-header {
  flex: none;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-title {
  font-weight: 800;
  font-size: 15px;
}

.close-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 50%;
}

.close-btn:hover {
  background: var(--surface-muted);
}

.message-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message-row {
  display: flex;
  flex-direction: column;
}

.message-row.user {
  align-items: flex-end;
}

.message-row.ai,
.message-row.system {
  align-items: flex-start;
}

.bubble {
  max-width: 78%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14.5px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-row.user .bubble {
  background: var(--accent);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message-row.ai .bubble,
.message-row.system .bubble {
  background: var(--surface-muted);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.place-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
  max-width: 78%;
}

.place-chip {
  white-space: nowrap;
  background: var(--surface);
  border: 1px solid var(--accent);
  color: var(--accent);
  border-radius: 16px;
  padding: 5px 11px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.place-chip:hover {
  background: var(--accent);
  color: #fff;
}

.anim-typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 14px;
}

.anim-typing span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #a8a49b;
  animation: lh-blink 1.2s infinite;
}

.anim-typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.anim-typing span:nth-child(3) {
  animation-delay: 0.4s;
}

.quick-actions {
  flex: none;
  display: flex;
  gap: 6px;
  padding: 9px 12px;
  overflow-x: auto;
  border-top: 1px solid #f0eee9;
}

.quick-chip {
  flex: none;
  white-space: nowrap;
  background: var(--surface-muted);
  border: 1px solid #e8e5de;
  border-radius: 16px;
  padding: 6px 12px;
  font-size: 12px;
  color: #4a4843;
  cursor: pointer;
}

.quick-chip:hover:not(:disabled) {
  background: #eceae4;
}

.quick-chip:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.input-area {
  flex: none;
  padding: 12px;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-wrapper {
  flex: 1;
}

.input-rounded {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border-input);
  border-radius: 22px;
  padding: 12px 18px;
  font-size: 14.5px;
  color: var(--text-primary);
  outline: none;
}

.input-rounded:disabled {
  background: var(--surface-sunken);
  color: var(--text-muted);
}

.send-btn {
  flex: none;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.send-btn:disabled {
  background: var(--text-muted);
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .chat-panel {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    border-radius: 0;
  }
}
</style>
