<template>
  <div class="chat-widget-wrapper">
    <!-- 채팅 팝업 창 (열렸을 때) -->
    <div v-if="isChatOpen" class="chat-popup">
      <div class="chat-header">
        <span class="chat-title">AI 여행 도우미</span>
        <button class="close-btn" @click="toggleChat">✕</button>
      </div>
      
      <div class="chat-body" ref="chatBody">
        <!-- 메세지 리스트 -->
        <div 
          v-for="(msg, idx) in chatMessages" 
          :key="idx" 
          class="chat-bubble-wrapper"
          :class="msg.role === 'user' ? 'is-user' : 'is-bot'"
        >
          <div class="chat-bubble">
            {{ msg.text }}
          </div>
        </div>
        
        <div v-if="isTyping" class="chat-bubble-wrapper is-bot">
          <div class="chat-bubble typing-indicator">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </div>
        </div>
      </div>
      
      <!-- 빠른 질문 버튼들 -->
      <div class="chat-quick-actions" v-if="chatMessages.length === 1">
        <button class="quick-btn" @click="sendQuickMsg('가볼만한 곳 추천')">가볼만한 곳 추천</button>
        <button class="quick-btn" @click="sendQuickMsg('한강 근처 맛집')">한강 근처 맛집</button>
      </div>

      <div class="chat-footer">
        <input 
          type="text" 
          v-model="chatInput" 
          @keyup.enter="sendChat" 
          placeholder="챗봇에게 물어보세요..." 
          class="chat-input"
        />
        <button class="send-btn" @click="sendChat" :disabled="!chatInput.trim()">전송</button>
      </div>
    </div>

    <!-- 플로팅 버튼 -->
    <button class="floating-btn" @click="toggleChat" :class="{ 'is-open': isChatOpen }">
      <span v-if="!isChatOpen" class="icon-chat">💬</span>
      <span v-else class="icon-close">✕</span>
    </button>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const isChatOpen = ref(false)
const chatInput = ref('')
const isTyping = ref(false)
const chatBody = ref(null)

const chatMessages = ref([
  { role: 'bot', text: '안녕하세요! AI 여행 도우미입니다. 서울 지역에 대해 궁금한 점을 물어보세요.' }
])

const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value
  if (isChatOpen.value) {
    scrollToBottom()
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatBody.value) {
    chatBody.value.scrollTop = chatBody.value.scrollHeight
  }
}

const sendQuickMsg = (msg) => {
  chatInput.value = msg
  sendChat()
}

const sendChat = () => {
  const text = chatInput.value.trim()
  if (!text || isTyping.value) return

  // 사용자 메세지 추가
  chatMessages.value.push({ role: 'user', text })
  chatInput.value = ''
  scrollToBottom()

  // 챗봇 응답 대기 상태 (더미)
  isTyping.value = true
  
  setTimeout(() => {
    isTyping.value = false
    chatMessages.value.push({ role: 'bot', text: 'API 연동 전 더미 응답입니다.' })
    scrollToBottom()
  }, 1000)
}
</script>

<style scoped>
.chat-widget-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.floating-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--accent, #f15b4c);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(241, 91, 76, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: all 0.2s ease;
  z-index: 50;
}

.floating-btn:hover {
  transform: scale(1.05);
  background: #d8402f;
}

.floating-btn.is-open {
  background: #1c1b1a;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.chat-popup {
  position: absolute;
  bottom: 76px;
  right: 0;
  width: 360px;
  height: 500px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(28, 27, 26, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 45;
  border: 1px solid #eceae6;
}

.chat-header {
  padding: 16px 20px;
  background: var(--accent, #f15b4c);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.chat-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #f4f2ee; /* muted bg */
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-bubble-wrapper {
  display: flex;
  width: 100%;
}

.chat-bubble-wrapper.is-user {
  justify-content: flex-end;
}

.chat-bubble-wrapper.is-bot {
  justify-content: flex-start;
}

.chat-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.4;
  word-break: break-word;
}

.is-user .chat-bubble {
  background: var(--accent, #f15b4c);
  color: white;
  border-bottom-right-radius: 4px;
}

.is-bot .chat-bubble {
  background: white;
  color: #1c1b1a;
  border: 1px solid #eceae6;
  border-bottom-left-radius: 4px;
}

.chat-quick-actions {
  display: flex;
  gap: 8px;
  padding: 8px 16px;
  background: #f4f2ee;
  overflow-x: auto;
}

.quick-btn {
  white-space: nowrap;
  background: white;
  border: 1px solid var(--accent, #f15b4c);
  color: var(--accent, #f15b4c);
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: var(--accent, #f15b4c);
  color: white;
}

.chat-footer {
  display: flex;
  padding: 12px;
  background: white;
  border-top: 1px solid #eceae6;
  gap: 8px;
}

.chat-input {
  flex: 1;
  border: 1px solid #eceae6;
  border-radius: 20px;
  padding: 8px 16px;
  outline: none;
  font-size: 14px;
}

.chat-input:focus {
  border-color: var(--accent, #f15b4c);
}

.send-btn {
  background: var(--accent, #f15b4c);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.send-btn:disabled {
  background: #d1cfc8;
  cursor: not-allowed;
}

/* Typing indicator */
.typing-indicator .dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: #a8a49b;
  border-radius: 50%;
  margin: 0 2px;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator .dot:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
