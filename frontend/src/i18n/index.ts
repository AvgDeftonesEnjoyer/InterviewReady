import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import AsyncStorage from '@react-native-async-storage/async-storage'
import en from '../locales/en.json'
import uk from '../locales/uk.json'

const LANGUAGE_KEY = 'ui_language'

export const initI18n = async () => {
  // Read saved language from storage
  const savedLang = await AsyncStorage.getItem(LANGUAGE_KEY)

  await i18n
    .use(initReactI18next)
    .init({
      resources: {
        en: { translation: en },
        uk: { translation: uk },
      },
      lng: savedLang || 'en',
      fallbackLng: 'en',
      interpolation: {
        escapeValue: false,
      },
    })
}

export const changeLanguage = async (lang: 'en' | 'uk') => {
  await i18n.changeLanguage(lang)
  await AsyncStorage.setItem(LANGUAGE_KEY, lang)
}

export default i18n
