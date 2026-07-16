import { createI18n } from 'vue-i18n'
import commonKo from './locales/ko/common'
import mapKo from './locales/ko/map'
import boardKo from './locales/ko/board'
import chatKo from './locales/ko/chat'
import commonEn from './locales/en/common'
import mapEn from './locales/en/map'
import boardEn from './locales/en/board'
import chatEn from './locales/en/chat'

export const STORAGE_KEY = 'ssafiple_locale'
export const SUPPORTED_LOCALES = ['ko', 'en']

const getInitialLocale = () => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved && SUPPORTED_LOCALES.includes(saved)) return saved
  return navigator.language?.toLowerCase().startsWith('en') ? 'en' : 'ko'
}

const i18n = createI18n({
  legacy: false,
  locale: getInitialLocale(),
  fallbackLocale: 'ko',
  messages: {
    ko: { common: commonKo, map: mapKo, board: boardKo, chat: chatKo },
    en: { common: commonEn, map: mapEn, board: boardEn, chat: chatEn }
  }
})

export const setLocale = (locale) => {
  if (!SUPPORTED_LOCALES.includes(locale)) return
  i18n.global.locale.value = locale
  localStorage.setItem(STORAGE_KEY, locale)
}

export default i18n
