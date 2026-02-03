'use client'

import { LanguageProvider } from '@/i18n'
import { AuthProvider } from '@/contexts/AuthContext'
import { Toaster } from 'sonner'
import { ReactNode } from 'react'

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <LanguageProvider>
        {children}
        <Toaster theme="dark" position="bottom-right" richColors />
      </LanguageProvider>
    </AuthProvider>
  )
}
