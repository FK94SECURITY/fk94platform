'use client'

import Link from 'next/link'
import { useState } from 'react'
import { useLanguage } from '@/i18n'
import { useAuth } from '@/contexts/AuthContext'
import LanguageToggle from './LanguageToggle'
import AuthModal from './AuthModal'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const { t, language } = useLanguage()
  const { user, signOut, isConfigured } = useAuth()

  return (
    <nav className="fixed w-full z-50 bg-black/80 backdrop-blur-md border-b border-zinc-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center font-bold text-black">
              FK
            </div>
            <span className="font-bold text-xl">FK94</span>
          </Link>

          {/* Desktop menu */}
          <div className="hidden md:flex items-center space-x-1">
            {/* Free Tools Dropdown Visual */}
            <div className="flex items-center space-x-1 px-3 py-1 rounded-lg bg-zinc-900/50">
              <span className="text-xs text-emerald-400 font-medium mr-2">{t.nav.free}</span>
              <Link href="/checklist" className="text-zinc-300 hover:text-white px-3 py-2 rounded-lg hover:bg-zinc-800 transition">
                {t.nav.checklist}
              </Link>
              <Link href="/harden" className="text-zinc-300 hover:text-white px-3 py-2 rounded-lg hover:bg-zinc-800 transition">
                {t.nav.harden}
              </Link>
            </div>

            <Link href="/pricing" className="text-zinc-400 hover:text-white px-3 py-2 transition">
              {t.nav.pricing}
            </Link>

            <LanguageToggle />

            <Link
              href="/audit"
              className="bg-emerald-600 hover:bg-emerald-500 px-5 py-2 rounded-lg font-medium transition ml-2"
            >
              {t.nav.scanNow}
            </Link>

            {/* Auth button */}
            {isConfigured && (
              user ? (
                <div className="flex items-center gap-2 ml-2">
                  <Link
                    href="/dashboard"
                    className="text-zinc-300 hover:text-white text-sm px-3 py-2"
                  >
                    {language === 'es' ? 'Panel' : 'Dashboard'}
                  </Link>
                  <span className="text-zinc-600">|</span>
                  <span className="text-zinc-400 text-sm">{user.email?.split('@')[0]}</span>
                  <button
                    onClick={() => signOut()}
                    className="text-zinc-400 hover:text-red-400 text-sm px-2 py-1"
                  >
                    {language === 'es' ? 'Cerrar sesión' : 'Logout'}
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="text-zinc-300 hover:text-white px-3 py-2 ml-2"
                >
                  {language === 'es' ? 'Iniciar sesión' : 'Login'}
                </button>
              )
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center gap-2">
            <LanguageToggle />
            <button
              className="text-zinc-400"
              onClick={() => setIsOpen(!isOpen)}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {isOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {isOpen && (
          <div className="md:hidden py-4 space-y-2">
            <div className="text-xs text-emerald-400 font-medium px-3 mb-2">{t.nav.freeTools}</div>
            <Link href="/checklist" className="block text-zinc-300 hover:text-white px-3 py-2 hover:bg-zinc-800 rounded-lg">
              {t.nav.checklist}
            </Link>
            <Link href="/harden" className="block text-zinc-300 hover:text-white px-3 py-2 hover:bg-zinc-800 rounded-lg">
              {t.nav.harden}
            </Link>
            <div className="border-t border-zinc-800 my-3"></div>
            <Link href="/pricing" className="block text-zinc-400 hover:text-white px-3 py-2">
              {t.nav.pricing}
            </Link>
            <Link href="/audit" className="block bg-emerald-600 text-center py-3 rounded-lg font-medium mt-2">
              {t.nav.scanNow}
            </Link>
            {isConfigured && (
              user ? (
                <div className="space-y-2">
                  <Link
                    href="/dashboard"
                    className="block text-zinc-300 hover:text-white px-3 py-2 hover:bg-zinc-800 rounded-lg"
                    onClick={() => setIsOpen(false)}
                  >
                    {language === 'es' ? 'Panel' : 'Dashboard'}
                  </Link>
                  <button
                    onClick={() => {
                      signOut()
                      setIsOpen(false)
                    }}
                    className="block w-full text-left text-zinc-400 hover:text-red-400 px-3 py-2"
                  >
                    {language === 'es' ? 'Cerrar sesión' : 'Logout'}
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => {
                    setShowAuthModal(true)
                    setIsOpen(false)
                  }}
                  className="block w-full text-center text-zinc-300 py-3 mt-2"
                >
                  {language === 'es' ? 'Iniciar sesión' : 'Login'}
                </button>
              )
            )}
          </div>
        )}
      </div>

      {/* Auth Modal */}
      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
    </nav>
  )
}
