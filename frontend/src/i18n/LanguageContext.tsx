'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { en } from './en'
import { es } from './es'

type Language = 'en' | 'es'
type Translations = typeof en

interface LanguageContextType {
  language: Language
  setLanguage: (lang: Language) => void
  t: Translations
}

const translations = { en, es }

// Default context value for SSR
const defaultContextValue: LanguageContextType = {
  language: 'en',
  setLanguage: () => {},
  t: en,
}

const LanguageContext = createContext<LanguageContextType>(defaultContextValue)

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>('en')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    // Check localStorage first
    const saved = localStorage.getItem('fk94-language') as Language
    if (saved && (saved === 'en' || saved === 'es')) {
      setLanguageState(saved)
      return
    }

    // Detect browser language
    const browserLang = navigator.language.toLowerCase()
    if (browserLang.startsWith('es')) {
      setLanguageState('es')
    }
  }, [])

  const setLanguage = (lang: Language) => {
    setLanguageState(lang)
    localStorage.setItem('fk94-language', lang)
  }

  const t = translations[language]

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  return useContext(LanguageContext)
}
