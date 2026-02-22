import { useState } from 'react'
import { changeLanguage } from '../i18n'
import { apiClient } from '../api/client'

export const useLanguage = () => {
  const [loading, setLoading] = useState(false)

  const switchLanguage = async (lang: 'en' | 'uk') => {
    setLoading(true)
    try {
      // Save locally (instant)
      await changeLanguage(lang)

      // Sync with backend
      await api.patch('/users/language/', { language: lang })
    } catch (error) {
      console.error('Failed to update language:', error)
    } finally {
      setLoading(false)
    }
  }

  return { switchLanguage, loading }
}
