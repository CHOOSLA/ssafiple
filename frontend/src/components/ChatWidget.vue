<template>
  <div>
    <!-- 펼침: 대화창 -->
    <div v-if="chat.isOpen" class="chat-panel anim-pop">
      <div class="chat-header">
        <span class="chat-title">SSAFIPLE AI</span>
        <button class="close-btn" type="button" aria-label="닫기" @click="chat.toggleOpen">
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
          <div class="bubble">{{ m.text }}</div>
        </div>

        <div v-if="chat.isLoading" class="message-row ai">
          <div class="bubble anim-typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <form class="input-area" @submit.prevent="handleSend">
        <div class="input-wrapper">
          <input
            v-model="draft"
            class="input-rounded"
            type="text"
            placeholder="익명으로 채팅 보내기"
            :disabled="chat.isLoading"
          />
        </div>
        <button class="send-btn" type="submit" aria-label="전송" :disabled="chat.isLoading || !draft.trim()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#fff">
            <polygon points="4,3 22,12 4,21 4,14 15,12 4,10" />
          </svg>
        </button>
      </form>
    </div>

    <!-- 접힘: 플로팅 버튼 -->
    <button v-else class="fab" type="button" aria-label="챗봇 열기" @click="chat.toggleOpen">
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
import { nextTick, ref, watch } from 'vue'
import { useChatStore } from '../stores/chat'

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
  background: #fff;
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
  background: #f4f2ee;
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
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.ai,
.message-row.system {
  justify-content: flex-start;
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
  background: #f4f2ee;
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
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
  background: #fff;
  border: 1px solid #e3e0d9;
  border-radius: 22px;
  padding: 12px 18px;
  font-size: 14.5px;
  color: var(--text-primary);
  outline: none;
}

.input-rounded:disabled {
  background: #f7f6f3;
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
