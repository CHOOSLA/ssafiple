import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useModalStore = defineStore('modal', () => {
  const isOpen = ref(false)
  const targetId = ref(null)
  const targetType = ref('') // 'post' or 'comment'
  const actionType = ref('') // 'edit' or 'delete'
  const resolvePromise = ref(null)

  const openPasswordModal = (id, type, action) => {
    targetId.value = id
    targetType.value = type
    actionType.value = action
    isOpen.value = true

    return new Promise((resolve) => {
      resolvePromise.value = resolve
    })
  }

  const closePasswordModal = (success = false, password = '') => {
    isOpen.value = false
    if (resolvePromise.value) {
      resolvePromise.value({ success, password })
      resolvePromise.value = null
    }
  }

  return {
    isOpen,
    targetId,
    targetType,
    actionType,
    openPasswordModal,
    closePasswordModal
  }
})
