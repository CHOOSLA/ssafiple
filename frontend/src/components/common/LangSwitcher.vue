<template>
  <div class="lang-switcher">
    <button
      v-for="l in SUPPORTED_LOCALES"
      :key="l"
      type="button"
      class="lang-btn"
      :class="{ active: locale === l }"
      @click="setLocale(l)"
    >
      {{ l.toUpperCase() }}
    </button>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { setLocale, SUPPORTED_LOCALES } from '@/i18n'

const { locale } = useI18n()
</script>

<style scoped>
.lang-switcher {
  display: flex;
  gap: 2px;
  background: #f4f2ee;
  border-radius: 8px;
  padding: 2px;
  flex: none;
}

.lang-btn {
  border: none;
  background: none;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  color: #a8a49b;
  cursor: pointer;
}

.lang-btn.active {
  background: #fff;
  color: #1c1b1a;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}
</style>
