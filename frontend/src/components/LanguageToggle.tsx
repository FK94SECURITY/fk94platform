'use client'

import { useLanguage } from '@/i18n'

export default function LanguageToggle() {
  const { language, setLanguage } = useLanguage()

  return (
    <button
      onClick={() => setLanguage(language === 'en' ? 'es' : 'en')}
      className="flex items-center gap-1 px-2 py-1 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition text-sm"
      title={language === 'en' ? 'Cambiar a Español' : 'Switch to English'}
    >
      <span className={language === 'en' ? 'opacity-100' : 'opacity-50'}>EN</span>
      <span className="text-zinc-500">/</span>
      <span className={language === 'es' ? 'opacity-100' : 'opacity-50'}>ES</span>
    </button>
  )
}
