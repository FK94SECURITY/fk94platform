'use client'

import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import { useLanguage } from '@/i18n'

export default function Home() {
  const { t, language } = useLanguage()
  const isEs = language === 'es'

  const whyProItems = isEs
    ? [
        {
          title: 'Monitoreo continuo',
          description: 'No es un chequeo único. Detecta cambios nuevos y te avisa automáticamente.',
          icon: '⏱️',
        },
        {
          title: 'Todo en un solo panel',
          description: 'Breaches, wallet, dominio, teléfono y username sin saltar entre herramientas.',
          icon: '📊',
        },
        {
          title: 'Priorización accionable',
          description: 'Te mostramos qué corregir primero para bajar riesgo real, no ruido.',
          icon: '🎯',
        },
        {
          title: 'Historial y reportes',
          description: 'Seguimiento de evolución y reportes listos para decisiones de negocio.',
          icon: '🧾',
        },
      ]
    : [
        {
          title: 'Continuous monitoring',
          description: 'Not a one-time check. It detects new exposure and alerts you automatically.',
          icon: '⏱️',
        },
        {
          title: 'Everything in one dashboard',
          description: 'Breaches, wallet, domain, phone, and username in one place.',
          icon: '📊',
        },
        {
          title: 'Actionable prioritization',
          description: 'We show what to fix first to reduce real risk, not noise.',
          icon: '🎯',
        },
        {
          title: 'History and reports',
          description: 'Track risk evolution and export reports for team decisions.',
          icon: '🧾',
        },
      ]

  const modelCards = isEs
    ? [
        {
          badge: 'GRATIS',
          title: 'DIY Security',
          description: 'Checklist + hardening para quien quiere hacerlo por su cuenta.',
          cta: 'Empezar Gratis',
          href: '/checklist',
          className: 'border-zinc-800',
        },
        {
          badge: 'PRO',
          title: 'Monitoreo SaaS',
          description: 'Escaneos + alertas + historial para mantener seguridad activa mes a mes.',
          cta: 'Ver Plan Pro',
          href: '/pricing',
          className: 'border-emerald-500/60',
        },
        {
          badge: 'CONCIERGE',
          title: 'Consultoría Premium',
          description: 'Para casos de alto riesgo: implementación 1:1 y plan personalizado.',
          cta: 'Contactar Equipo',
          href: '/contact',
          className: 'border-purple-500/40',
        },
      ]
    : [
        {
          badge: 'FREE',
          title: 'DIY Security',
          description: 'Checklist + hardening for users who want to do it themselves.',
          cta: 'Start Free',
          href: '/checklist',
          className: 'border-zinc-800',
        },
        {
          badge: 'PRO',
          title: 'SaaS Monitoring',
          description: 'Scans + alerts + history to keep your security active month after month.',
          cta: 'View Pro Plan',
          href: '/pricing',
          className: 'border-emerald-500/60',
        },
        {
          badge: 'CONCIERGE',
          title: 'Premium Consulting',
          description: 'For high-risk cases: 1:1 implementation and custom protection plan.',
          cta: 'Contact Team',
          href: '/contact',
          className: 'border-purple-500/40',
        },
      ]

  return (
    <>
      <Navbar />

      {/* Hero Section */}
      <section className="min-h-screen flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/10 via-transparent to-transparent" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />

        <div className="relative z-10 max-w-6xl mx-auto px-4 text-center pt-20">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            {t.hero.title.split(t.hero.highlight || ' Made Simple')[0]}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
              {' '}{t.hero.highlight || 'Made Simple'}
            </span>
          </h1>

          <p className="text-xl text-zinc-400 max-w-2xl mx-auto mb-10">
            {t.hero.subtitle}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/checklist"
              className="bg-emerald-600 hover:bg-emerald-500 px-8 py-4 rounded-xl font-semibold text-lg transition transform hover:scale-105"
            >
              {t.hero.cta.free}
            </Link>
            <Link
              href="/audit"
              className="border border-zinc-700 hover:border-zinc-500 px-8 py-4 rounded-xl font-semibold text-lg transition"
            >
              {t.hero.cta.scan}
            </Link>
          </div>
        </div>
      </section>

      {/* Why Pro Section */}
      <section className="py-24 border-b border-zinc-800">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-4xl font-bold mb-4">
              {isEs ? 'Por qué pagar Pro' : 'Why Pay for Pro'}
            </h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">
              {isEs
                ? 'Lo gratuito sirve para empezar. Pro sirve para mantenerte protegido sin perder tiempo.'
                : 'Free tools help you start. Pro keeps you protected without wasting time.'}
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {whyProItems.map((item) => (
              <div key={item.title} className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-6">
                <div className="text-2xl mb-3">{item.icon}</div>
                <h3 className="font-semibold mb-2">{item.title}</h3>
                <p className="text-zinc-500 text-sm">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* What is OPSEC Section */}
      <section className="py-24 border-b border-zinc-800">
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6">{t.whatIsOpsec.title}</h2>
              <p className="text-zinc-400 mb-6 text-lg">
                {t.whatIsOpsec.description}
              </p>
            </div>
            <div className="space-y-4">
              <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-red-500/10 rounded-lg flex items-center justify-center text-red-400 text-xl">
                    1
                  </div>
                  <div>
                    <h3 className="font-semibold">{t.whatIsOpsec.steps.identify.title}</h3>
                    <p className="text-zinc-500 text-sm">{t.whatIsOpsec.steps.identify.description}</p>
                  </div>
                </div>
              </div>
              <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-yellow-500/10 rounded-lg flex items-center justify-center text-yellow-400 text-xl">
                    2
                  </div>
                  <div>
                    <h3 className="font-semibold">{t.whatIsOpsec.steps.analyze.title}</h3>
                    <p className="text-zinc-500 text-sm">{t.whatIsOpsec.steps.analyze.description}</p>
                  </div>
                </div>
              </div>
              <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center text-blue-400 text-xl">
                    3
                  </div>
                  <div>
                    <h3 className="font-semibold">{t.whatIsOpsec.steps.assess.title}</h3>
                    <p className="text-zinc-500 text-sm">{t.whatIsOpsec.steps.assess.description}</p>
                  </div>
                </div>
              </div>
              <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-emerald-500/10 rounded-lg flex items-center justify-center text-emerald-400 text-xl">
                    4
                  </div>
                  <div>
                    <h3 className="font-semibold">{t.whatIsOpsec.steps.protect.title}</h3>
                    <p className="text-zinc-500 text-sm">{t.whatIsOpsec.steps.protect.description}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Who is this for Section */}
      <section className="py-24">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">{t.whoNeeds.title}</h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-zinc-900/30 border border-zinc-800 rounded-xl p-6 text-center">
              <div className="text-4xl mb-4">💰</div>
              <h3 className="font-semibold mb-2">{t.whoNeeds.profiles.crypto.title}</h3>
              <p className="text-zinc-500 text-sm">{t.whoNeeds.profiles.crypto.description}</p>
            </div>
            <div className="bg-zinc-900/30 border border-zinc-800 rounded-xl p-6 text-center">
              <div className="text-4xl mb-4">💼</div>
              <h3 className="font-semibold mb-2">{t.whoNeeds.profiles.professionals.title}</h3>
              <p className="text-zinc-500 text-sm">{t.whoNeeds.profiles.professionals.description}</p>
            </div>
            <div className="bg-zinc-900/30 border border-zinc-800 rounded-xl p-6 text-center">
              <div className="text-4xl mb-4">📰</div>
              <h3 className="font-semibold mb-2">{t.whoNeeds.profiles.activists.title}</h3>
              <p className="text-zinc-500 text-sm">{t.whoNeeds.profiles.activists.description}</p>
            </div>
            <div className="bg-zinc-900/30 border border-zinc-800 rounded-xl p-6 text-center">
              <div className="text-4xl mb-4">👤</div>
              <h3 className="font-semibold mb-2">{t.whoNeeds.profiles.privacy.title}</h3>
              <p className="text-zinc-500 text-sm">{t.whoNeeds.profiles.privacy.description}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Free Tools Section */}
      <section className="py-24 bg-zinc-950">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-emerald-400 text-sm font-medium mb-4">
              100% {t.common.free}
            </span>
            <h2 className="text-4xl font-bold mb-4">{t.freeTools.title}</h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">
              {t.freeTools.subtitle}
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Checklist */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 hover:border-emerald-500/50 transition group">
              <div className="w-14 h-14 bg-emerald-500/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-emerald-500/20 transition text-3xl">
                📋
              </div>
              <h3 className="text-2xl font-semibold mb-3">{t.freeTools.checklist.title}</h3>
              <p className="text-zinc-400 mb-6">
                {t.freeTools.checklist.description}
              </p>
              <Link href="/checklist" className="text-emerald-400 hover:text-emerald-300 font-medium inline-flex items-center gap-2">
                {t.freeTools.checklist.cta}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>

            {/* Harden Script */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 hover:border-emerald-500/50 transition group">
              <div className="w-14 h-14 bg-blue-500/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-blue-500/20 transition text-3xl">
                🛡️
              </div>
              <h3 className="text-2xl font-semibold mb-3">{t.freeTools.harden.title}</h3>
              <p className="text-zinc-400 mb-6">
                {t.freeTools.harden.description}
              </p>
              <Link href="/harden" className="text-blue-400 hover:text-blue-300 font-medium inline-flex items-center gap-2">
                {t.freeTools.harden.cta}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Paid Service Section */}
      <section className="py-24">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1 bg-purple-500/10 border border-purple-500/30 rounded-full text-purple-400 text-sm font-medium mb-4">
              {t.premium.badge}
            </span>
            <h2 className="text-4xl font-bold mb-4">{t.premium.title}</h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">
              {t.premium.subtitle}
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 hover:border-purple-500/30 transition">
              <div className="text-2xl mb-3">📧</div>
              <h3 className="font-semibold mb-2">{t.premium.scans.email.title}</h3>
              <p className="text-zinc-500 text-sm">{t.premium.scans.email.description}</p>
            </div>

            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 hover:border-purple-500/30 transition">
              <div className="text-2xl mb-3">🔐</div>
              <h3 className="font-semibold mb-2">{t.premium.scans.password.title}</h3>
              <p className="text-zinc-500 text-sm">{t.premium.scans.password.description}</p>
            </div>

            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 hover:border-purple-500/30 transition">
              <div className="text-2xl mb-3">👤</div>
              <h3 className="font-semibold mb-2">{t.premium.scans.username.title}</h3>
              <p className="text-zinc-500 text-sm">{t.premium.scans.username.description}</p>
            </div>

            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 hover:border-purple-500/30 transition">
              <div className="text-2xl mb-3">🌐</div>
              <h3 className="font-semibold mb-2">{t.premium.scans.domain.title}</h3>
              <p className="text-zinc-500 text-sm">{t.premium.scans.domain.description}</p>
            </div>

            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 hover:border-purple-500/30 transition">
              <div className="text-2xl mb-3">💰</div>
              <h3 className="font-semibold mb-2">{t.premium.scans.wallet.title}</h3>
              <p className="text-zinc-500 text-sm">{t.premium.scans.wallet.description}</p>
            </div>

            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 hover:border-purple-500/30 transition">
              <div className="text-2xl mb-3">📱</div>
              <h3 className="font-semibold mb-2">{t.premium.scans.phone.title}</h3>
              <p className="text-zinc-500 text-sm">{t.premium.scans.phone.description}</p>
            </div>
          </div>

          <div className="text-center mt-12">
            <Link
              href="/audit"
              className="inline-block bg-purple-600 hover:bg-purple-500 px-8 py-4 rounded-xl font-semibold text-lg transition"
            >
              {t.premium.cta}
            </Link>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-24 bg-zinc-950">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">{t.pricing.title}</h2>
            <p className="text-zinc-400">{t.pricing.subtitle}</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Free */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8">
              <h3 className="text-xl font-semibold mb-2">{t.pricing.free.title}</h3>
              <p className="text-zinc-500 mb-6">{t.pricing.free.period}</p>
              <div className="mb-8">
                <span className="text-4xl font-bold">{t.pricing.free.price}</span>
              </div>
              <ul className="space-y-3 mb-8 text-zinc-300">
                {t.pricing.free.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                {t.pricing.free.cta}
              </Link>
            </div>

            {/* Pro */}
            <div className="bg-zinc-900 border-2 border-emerald-500 rounded-2xl p-8 relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-emerald-500 text-black text-xs font-bold rounded-full">
                RECOMMENDED
              </div>
              <h3 className="text-xl font-semibold mb-2">{t.pricing.pro.title}</h3>
              <p className="text-zinc-500 mb-6">{t.pricing.pro.description}</p>
              <div className="mb-8">
                <span className="text-4xl font-bold">{t.pricing.pro.price}</span>
                <span className="text-zinc-500">{t.pricing.pro.period}</span>
              </div>
              <ul className="space-y-3 mb-8 text-zinc-300">
                {t.pricing.pro.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
              <Link
                href="/audit"
                className="block text-center py-3 bg-emerald-600 hover:bg-emerald-500 rounded-xl font-medium transition"
              >
                {t.pricing.pro.cta}
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Business Model Section */}
      <section className="py-24">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-4xl font-bold mb-4">
              {isEs ? 'Un modelo para cada necesidad' : 'A model for every need'}
            </h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">
              {isEs
                ? 'Entrás gratis, escalás a monitoreo y subís a consultoría solo si realmente lo necesitás.'
                : 'Start free, upgrade to monitoring, and move to consulting only when needed.'}
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {modelCards.map((card) => (
              <div key={card.title} className={`bg-zinc-900 border rounded-2xl p-7 ${card.className}`}>
                <span className="inline-block text-xs font-semibold px-2.5 py-1 rounded-full bg-zinc-800 mb-4">
                  {card.badge}
                </span>
                <h3 className="text-2xl font-semibold mb-2">{card.title}</h3>
                <p className="text-zinc-400 mb-6">{card.description}</p>
                <Link
                  href={card.href}
                  className="inline-block bg-zinc-800 hover:bg-zinc-700 px-5 py-2.5 rounded-lg font-medium transition"
                >
                  {card.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Consulting CTA */}
      <section className="py-24">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">{t.consulting.title}</h2>
          <p className="text-zinc-400 mb-8 max-w-2xl mx-auto">
            {t.consulting.description}
          </p>
          <Link
            href="/contact"
            className="inline-block border border-zinc-700 hover:border-zinc-500 px-8 py-4 rounded-xl font-semibold transition"
          >
            {t.consulting.cta}
          </Link>
        </div>
      </section>

      <Footer />
    </>
  )
}
