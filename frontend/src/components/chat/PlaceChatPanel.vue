<template>
  <div class="place-chat">
    <div ref="messageListEl" class="message-list">
      <div class="chat-hint">{{ $t('chat.placeChatHint') }}</div>

      <template v-for="m in displayMessages" :key="m.id">
        <div v-if="m.isSystem" class="system-row">
          {{ m.event === 'join' ? $t('chat.systemJoin', { nickname: m.nickname }) : $t('chat.systemLeave', { nickname: m.nickname }) }}
        </div>
        <div v-else class="message-row" :class="{ mine: m.mine }">
          <span v-if="m.showName" class="author-label">{{ m.nickname }}</span>
          <span class="bubble">{{ m.content }}</span>
        </div>
      </template>
    </div>

    <form class="input-area" @submit.prevent="handleSend">
      <input
        v-model="draft"
        class="place-chat-input"
        type="text"
        maxlength="300"
        :placeholder="$t('chat.placeChatPlaceholder')"
        :disabled="chat.status !== 'open'"
      />
      <button class="send-btn" type="submit" :aria-label="$t('chat.sendAria')" :disabled="chat.status !== 'open' || !draft.trim()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="#fff">
          <polygon points="4,3 22,12 4,21 4,14 15,12 4,10" />
        </svg>
      </button>
    </form>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { usePlaceChatStore } from '@/stores/chatStore'

const props = defineProps({
  locationId: {
    type: [String, Number],
    required: true,
  },
})

const chat = usePlaceChatStore()
const draft = ref('')
const messageListEl = ref(null)

const displayMessages = computed(() => {
  let prevNickname = null
  return chat.messages.map((m) => {
    if (m.type === 'system') {
      prevNickname = null
      return { ...m, isSystem: true }
    }
    const mine = m.nickname === chat.nickname
    const showName = !mine && prevNickname !== m.nickname
    prevNickname = m.nickname
    return { ...m, isSystem: false, mine, showName }
  })
})

const scrollToBottom = () => {
  nextTick(() => {
    const el = messageListEl.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

watch(() => chat.messages.length, scrollToBottom)

watch(
  () => props.locationId,
  (locationId) => {
    if (locationId) chat.connect(locationId)
  },
  { immediate: true }
)

onUnmounted(() => {
  chat.disconnect()
})

const handleSend = () => {
  chat.sendMessage(draft.value)
  draft.value = ''
}
</script>

<style scoped>
.place-chat {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.message-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  background: #f7f6f3;
  padding: 16px 18px;
}

.chat-hint {
  text-align: center;
  font-size: 11.5px;
  color: #b0ada5;
  margin-bottom: 16px;
}

.system-row {
  text-align: center;
  font-size: 11.5px;
  color: #b0ada5;
  margin-bottom: 12px;
}

.message-row {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 12px;
}

.message-row.mine {
  align-items: flex-end;
}

.author-label {
  font-size: 11px;
  color: #a8a49b;
  margin: 0 4px 3px;
}

.bubble {
  max-width: 72%;
  background: #fff;
  color: var(--text-primary);
  padding: 9px 13px;
  border-radius: 15px;
  font-size: 13.5px;
  line-height: 1.55;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.message-row.mine .bubble {
  background: var(--accent);
  color: #fff;
}

.input-area {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--border-color);
  background: #fff;
  flex: none;
}

.place-chat-input {
  flex: 1;
  min-width: 0;
  border: 1px solid #e3e0d9;
  border-radius: 22px;
  padding: 11px 15px;
  font-size: 13.5px;
  outline: none;
  color: var(--text-primary);
}

.place-chat-input:disabled {
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
</style>
