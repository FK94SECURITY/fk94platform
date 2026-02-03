'use client'

import { useState } from 'react'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import { useLanguage } from '@/i18n'
import { useAuth } from '@/contexts/AuthContext'
import { redirectToCheckout } from '@/lib/stripe'

export default function PricingPage() {
  const { language } = useLanguage()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubscribe = async () => {
    if (!user) {
      // Redirect to login with return URL
      window.location.href = '/login?redirect=/pricing'
      return
    }

    setLoading(true)
    setError(null)

    try {
      await redirectToCheckout(user.email || '', user.id)
    } catch {
      setError(language === 'es'
        ? 'Error al procesar el pago. Intentá de nuevo.'
        : 'Error processing payment. Please try again.')
      setLoading(false)
    }
  }

  const freeFeatures = language === 'es' ? [
    'Checklist OPSEC completo (54 items)',
    'Generador de scripts de hardening',
    'Soporte Mac, Windows y Linux',
    'Seguimiento de progreso',
    'Sin cuenta requerida',
  ] : [
    'Full OPSEC Checklist (54 items)',
    'Hardening script generator',
    'Mac, Windows & Linux support',
    'Progress tracking',
    'No account required',
  ]

  const proFeatures = language === 'es' ? [
    'Todo lo de Gratis',
    'Escaneo de filtraciones de email',
    'Detección de passwords expuestos',
    'Búsqueda OSINT de usernames',
    'Verificación de wallets crypto',
    'Búsqueda por número de teléfono',
    'Inteligencia de dominio',
    'Monitoreo de dark web',
    'Reportes PDF descargables',
    'Escaneos ilimitados',
  ] : [
    'Everything in Free',
    'Email breach scanning',
    'Exposed password detection',
    'Username OSINT lookups',
    'Crypto wallet verification',
    'Phone number lookup',
    'Domain intelligence',
    'Dark web monitoring',
    'Downloadable PDF reports',
    'Unlimited scans',
  ]

  const faqs = language === 'es' ? [
    {
      question: '¿Puedo cancelar cuando quiera?',
      answer: 'Sí, podés cancelar tu suscripción en cualquier momento sin penalidad. Mantenés acceso hasta el final del período facturado.',
    },
    {
      question: '¿Qué métodos de pago aceptan?',
      answer: 'Aceptamos todas las tarjetas de crédito principales y PayPal. Próximamente crypto.',
    },
    {
      question: '¿Mis datos están seguros?',
      answer: 'Absolutamente. Nunca almacenamos tus contraseñas. Los datos de auditoría se procesan en tiempo real y no se retienen.',
    },
    {
      question: '¿Qué bases de datos de filtraciones usan?',
      answer: 'Usamos múltiples fuentes incluyendo Have I Been Pwned, Dehashed, y otras bases de datos con más de 15 mil millones de registros.',
    },
    {
      question: '¿Hay límite de escaneos?',
      answer: 'Los usuarios Pro tienen escaneos ilimitados. Podés verificar tantos emails, usernames, wallets como necesites.',
    },
  ] : [
    {
      question: 'Can I cancel anytime?',
      answer: 'Yes, you can cancel your subscription at any time with no penalty. You retain access until the end of your billing period.',
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards and PayPal. Crypto payments coming soon.',
    },
    {
      question: 'Is my data secure?',
      answer: 'Absolutely. We never store your passwords. Audit data is processed in real-time and not retained.',
    },
    {
      question: 'What breach databases do you use?',
      answer: 'We use multiple sources including Have I Been Pwned, Dehashed, and other databases with over 15 billion records.',
    },
    {
      question: 'Is there a limit on scans?',
      answer: 'Pro users have unlimited scans. You can check as many emails, usernames, and wallets as you need.',
    },
  ]

  return (
    <>
      <Navbar />

      <main className="min-h-screen pt-20">
        {/* Hero */}
        <section className="py-20 bg-gradient-to-b from-emerald-500/10 to-transparent">
          <div className="max-w-6xl mx-auto px-4 text-center">
            <h1 className="text-5xl font-bold mb-6">
              {language === 'es' ? 'Precios Simples' : 'Simple Pricing'}
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              {language === 'es'
                ? 'Herramientas gratis para todos. Escaneos premium para quienes los necesitan.'
                : 'Free tools for everyone. Premium scans for those who need them.'}
            </p>
          </div>
        </section>

        {/* Pricing Cards */}
        <section className="py-20">
          <div className="max-w-4xl mx-auto px-4">
            <div className="grid md:grid-cols-2 gap-8">
              {/* Free */}
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8">
                <h3 className="text-2xl font-semibold mb-2">
                  {language === 'es' ? 'Gratis' : 'Free'}
                </h3>
                <p className="text-zinc-400 mb-6">
                  {language === 'es' ? 'Para siempre' : 'Forever free'}
                </p>
                <div className="mb-8">
                  <span className="text-5xl font-bold">$0</span>
                </div>
                <ul className="space-y-4 mb-8">
                  {freeFeatures.map((feature, i) => (
                    <li key={i} className="flex items-center gap-3 text-zinc-300">
                      <svg className="w-5 h-5 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/checklist"
                  className="block text-center py-3 border border-zinc-700 hover:border-zinc-500 rounded-xl font-medium transition"
                >
                  {language === 'es' ? 'Empezar Gratis' : 'Get Started Free'}
                </Link>
              </div>

              {/* Pro */}
              <div className="bg-zinc-900 border-2 border-emerald-500 rounded-2xl p-8 relative">
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-emerald-500 text-black text-xs font-bold rounded-full">
                  {language === 'es' ? 'RECOMENDADO' : 'RECOMMENDED'}
                </div>
                <h3 className="text-2xl font-semibold mb-2">Pro</h3>
                <p className="text-zinc-400 mb-6">
                  {language === 'es' ? 'Escaneos completos' : 'Full scanning power'}
                </p>
                <div className="mb-8">
                  <span className="text-5xl font-bold">$10</span>
                  <span className="text-zinc-500">/{language === 'es' ? 'mes' : 'month'}</span>
                </div>
                <ul className="space-y-4 mb-8">
                  {proFeatures.map((feature, i) => (
                    <li key={i} className="flex items-center gap-3 text-zinc-300">
                      <svg className="w-5 h-5 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
                <button
                  onClick={handleSubscribe}
                  disabled={loading}
                  className="w-full text-center py-3 bg-emerald-600 hover:bg-emerald-500 rounded-xl font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading
                    ? (language === 'es' ? 'Procesando...' : 'Processing...')
                    : (language === 'es' ? 'Suscribirse a Pro' : 'Subscribe to Pro')}
                </button>
                {error && (
                  <p className="mt-2 text-red-400 text-sm text-center">{error}</p>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* What's Included */}
        <section className="py-20 bg-zinc-950">
          <div className="max-w-6xl mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">
              {language === 'es' ? '¿Qué Incluye Pro?' : 'What\'s Included in Pro?'}
            </h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <ScanFeature
                icon="📧"
                title={language === 'es' ? 'Escaneo de Email' : 'Email Scan'}
                description={language === 'es'
                  ? 'Verificá si tu email aparece en filtraciones de datos conocidas'
                  : 'Check if your email appears in known data breaches'}
              />
              <ScanFeature
                icon="🔐"
                title={language === 'es' ? 'Passwords Filtrados' : 'Leaked Passwords'}
                description={language === 'es'
                  ? 'Detectá si tus contraseñas fueron expuestas en filtraciones'
                  : 'Detect if your passwords were exposed in breaches'}
              />
              <ScanFeature
                icon="👤"
                title={language === 'es' ? 'OSINT de Username' : 'Username OSINT'}
                description={language === 'es'
                  ? 'Encontrá cuentas vinculadas a tus usernames en 300+ plataformas'
                  : 'Find accounts linked to your usernames across 300+ platforms'}
              />
              <ScanFeature
                icon="💰"
                title={language === 'es' ? 'Wallet Crypto' : 'Crypto Wallet'}
                description={language === 'es'
                  ? 'Verificá si tu wallet está vinculada a tu identidad real'
                  : 'Check if your wallet is linked to your real identity'}
              />
              <ScanFeature
                icon="📱"
                title={language === 'es' ? 'Número de Teléfono' : 'Phone Number'}
                description={language === 'es'
                  ? 'Buscá datos asociados a tu número de teléfono'
                  : 'Find data associated with your phone number'}
              />
              <ScanFeature
                icon="🌐"
                title={language === 'es' ? 'Dominio' : 'Domain'}
                description={language === 'es'
                  ? 'Analizá la seguridad de tu dominio y configuraciones expuestas'
                  : 'Analyze your domain security and exposed configurations'}
              />
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-20">
          <div className="max-w-3xl mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">
              {language === 'es' ? 'Preguntas Frecuentes' : 'Frequently Asked Questions'}
            </h2>
            <div className="space-y-6">
              {faqs.map((faq, i) => (
                <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                  <h3 className="font-semibold mb-2">{faq.question}</h3>
                  <p className="text-zinc-400">{faq.answer}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-20 bg-gradient-to-r from-emerald-900/50 to-cyan-900/50">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-4xl font-bold mb-6">
              {language === 'es' ? '¿Listo para Empezar?' : 'Ready to Get Started?'}
            </h2>
            <p className="text-xl text-zinc-300 mb-8">
              {language === 'es'
                ? 'Empezá gratis con el checklist, o escaneá tus datos con Pro.'
                : 'Start free with the checklist, or scan your data with Pro.'}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/checklist"
                className="border border-zinc-500 hover:border-white px-8 py-4 rounded-xl font-semibold text-lg transition"
              >
                {language === 'es' ? 'Empezar Gratis' : 'Start Free'}
              </Link>
              <button
                onClick={handleSubscribe}
                disabled={loading}
                className="bg-white text-black px-8 py-4 rounded-xl font-semibold text-lg hover:bg-zinc-200 transition disabled:opacity-50"
              >
                {loading
                  ? (language === 'es' ? 'Procesando...' : 'Processing...')
                  : (language === 'es' ? 'Suscribirse a Pro' : 'Subscribe to Pro')}
              </button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  )
}

function ScanFeature({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6">
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <p className="text-zinc-500 text-sm">{description}</p>
    </div>
  )
}
