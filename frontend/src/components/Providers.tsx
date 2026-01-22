'use client'

import { LanguageProvider } from '@/i18n'
import { AuthProvider } from '@/contexts/AuthContext'
import { ReactNode } from 'react'

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <LanguageProvider>{children}</LanguageProvider>
    </AuthProvider>
  )
}
