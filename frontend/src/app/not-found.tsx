'use client'

import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import { useLanguage } from '@/i18n'

export default function NotFound() {
  const { language } = useLanguage()

  return (
    <>
      <Navbar />

      <main className="min-h-screen pt-20 flex items-center justify-center">
        <div className="max-w-2xl mx-auto px-4 text-center py-20">
          <div className="text-8xl font-bold text-emerald-500 mb-6">404</div>
          <h1 className="text-4xl font-bold mb-4">
            {language === 'es' ? 'Página no encontrada' : 'Page Not Found'}
          </h1>
          <p className="text-xl text-zinc-400 mb-8">
            {language === 'es'
              ? 'La página que buscás no existe o fue movida.'
              : 'The page you are looking for does not exist or has been moved.'}
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link
              href="/"
              className="bg-emerald-600 hover:bg-emerald-500 px-8 py-3 rounded-xl font-semibold transition"
            >
              {language === 'es' ? 'Volver al Inicio' : 'Back to Home'}
            </Link>
            <Link
              href="/audit"
              className="border border-zinc-700 hover:border-zinc-500 px-8 py-3 rounded-xl font-semibold transition"
            >
              {language === 'es' ? 'Escaneo de Seguridad' : 'Security Scan'}
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </>
  )
}
