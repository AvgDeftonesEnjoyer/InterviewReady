import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import { Platform } from 'react-native'
import en from '../locales/en.json'
import uk from '../locales/uk.json'

const LANGUAGE_KEY = 'ui_language'

// Get saved language with fallback for web
const getSavedLanguage = async (): Promise<string | null> => {
  try {
    if (Platform.OS === 'web') {
      return localStorage.getItem(LANGUAGE_KEY)
    }
    const AsyncStorage = (await import('@react-native-async-storage/async-storage')).default
    return await AsyncStorage.getItem(LANGUAGE_KEY)
  } catch (e) {
    console.warn('Failed to get saved language:', e)
    return null
  }
}

// Set language with fallback for web
const setLanguageStorage = async (lang: string): Promise<void> => {
  try {
    if (Platform.OS === 'web') {
      localStorage.setItem(LANGUAGE_KEY, lang)
      return
    }
    const AsyncStorage = (await import('@react-native-async-storage/async-storage')).default
    await AsyncStorage.setItem(LANGUAGE_KEY, lang)
  } catch (e) {
    console.warn('Failed to save language:', e)
  }
}

export const initI18n = async () => {
  // Read saved language from storage
  const savedLang = await getSavedLanguage()

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
  await setLanguageStorage(lang)
}

export default i18n
