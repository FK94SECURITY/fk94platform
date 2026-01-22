'use client'

import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import { useLanguage } from '@/i18n'

export default function ServicesPage() {
  const { language } = useLanguage()

  return (
    <>
      <Navbar />

      <main className="min-h-screen pt-20">
        {/* Hero */}
        <section className="py-20 bg-gradient-to-b from-emerald-500/10 to-transparent">
          <div className="max-w-6xl mx-auto px-4 text-center">
            <h1 className="text-5xl font-bold mb-6">
              {language === 'es' ? 'Nuestros Servicios' : 'Our Services'}
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              {language === 'es'
                ? 'Soluciones de seguridad para proteger tu identidad digital y privacidad'
                : 'Security solutions to protect your digital identity and privacy'}
            </p>
          </div>
        </section>

        {/* Free Tools */}
        <section id="free" className="py-20">
          <div className="max-w-6xl mx-auto px-4">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <div className="inline-block px-3 py-1 bg-emerald-500/10 text-emerald-400 text-sm rounded-full mb-4">
                  {language === 'es' ? 'Gratis' : 'Free'}
                </div>
                <h2 className="text-4xl font-bold mb-6">
                  {language === 'es' ? 'Herramientas Gratuitas' : 'Free Tools'}
                </h2>
                <p className="text-zinc-400 mb-6">
                  {language === 'es'
                    ? 'Empezá a protegerte hoy sin costo. Checklist interactivo y scripts de hardening personalizados para tu sistema operativo.'
                    : 'Start protecting yourself today at no cost. Interactive checklist and personalized hardening scripts for your operating system.'}
                </p>
                <ul className="space-y-3 mb-8">
                  <ServiceFeature color="emerald">
                    {language === 'es' ? 'Checklist OPSEC con 54 items' : 'OPSEC Checklist with 54 items'}
                  </ServiceFeature>
                  <ServiceFeature color="emerald">
                    {language === 'es' ? 'Scripts de hardening personalizados' : 'Personalized hardening scripts'}
                  </ServiceFeature>
                  <ServiceFeature color="emerald">
                    {language === 'es' ? 'Soporte Mac, Windows y Linux' : 'Mac, Windows & Linux support'}
                  </ServiceFeature>
                  <ServiceFeature color="emerald">
                    {language === 'es' ? 'Seguimiento de progreso' : 'Progress tracking'}
                  </ServiceFeature>
                </ul>
                <div className="flex gap-4">
                  <Link href="/checklist" className="inline-block bg-emerald-600 hover:bg-emerald-500 px-6 py-3 rounded-xl font-medium transition">
                    {language === 'es' ? 'Abrir Checklist' : 'Open Checklist'}
                  </Link>
                  <Link href="/harden" className="inline-block border border-zinc-700 hover:border-zinc-500 px-6 py-3 rounded-xl font-medium transition">
                    {language === 'es' ? 'Generar Script' : 'Generate Script'}
                  </Link>
                </div>
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8">
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-3 bg-zinc-800 rounded-lg">
                    <span className="text-2xl">📋</span>
                    <div>
                      <p className="font-semibold">{language === 'es' ? 'Checklist Interactivo' : 'Interactive Checklist'}</p>
                      <p className="text-sm text-zinc-500">54 {language === 'es' ? 'prácticas de seguridad' : 'security practices'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-zinc-800 rounded-lg">
                    <span className="text-2xl">🛡️</span>
                    <div>
                      <p className="font-semibold">{language === 'es' ? 'Scripts Personalizados' : 'Custom Scripts'}</p>
                      <p className="text-sm text-zinc-500">{language === 'es' ? 'Basados en tu perfil de riesgo' : 'Based on your risk profile'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-zinc-800 rounded-lg">
                    <span className="text-2xl">💾</span>
                    <div>
                      <p className="font-semibold">{language === 'es' ? 'Progreso Guardado' : 'Progress Saved'}</p>
                      <p className="text-sm text-zinc-500">{language === 'es' ? 'En tu navegador' : 'In your browser'}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Pro Scanning */}
        <section id="scanning" className="py-20 bg-zinc-950">
          <div className="max-w-6xl mx-auto px-4">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div className="order-2 md:order-1 bg-zinc-900 border border-zinc-800 rounded-2xl p-8">
                <h3 className="font-semibold mb-4 text-purple-400">
                  {language === 'es' ? 'Tipos de Escaneo' : 'Scan Types'}
                </h3>
                <div className="space-y-3">
                  {[
                    { icon: '📧', label: language === 'es' ? 'Email - Filtraciones de datos' : 'Email - Data breaches' },
                    { icon: '👤', label: language === 'es' ? 'Username - OSINT en 300+ plataformas' : 'Username - OSINT across 300+ platforms' },
                    { icon: '💰', label: language === 'es' ? 'Wallet - Vinculación de identidad' : 'Wallet - Identity linking' },
                    { icon: '📱', label: language === 'es' ? 'Teléfono - Info de carrier y breaches' : 'Phone - Carrier info and breaches' },
                    { icon: '🌐', label: language === 'es' ? 'Dominio - SSL, DNS, SPF, DMARC' : 'Domain - SSL, DNS, SPF, DMARC' },
                    { icon: '📍', label: language === 'es' ? 'IP - Reputación y listas negras' : 'IP - Reputation and blacklists' },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-3 p-3 bg-zinc-800 rounded-lg">
                      <span className="text-xl">{item.icon}</span>
                      <span className="text-zinc-300">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="order-1 md:order-2">
                <div className="inline-block px-3 py-1 bg-purple-500/10 text-purple-400 text-sm rounded-full mb-4">
                  PRO - $10/{language === 'es' ? 'mes' : 'month'}
                </div>
                <h2 className="text-4xl font-bold mb-6">
                  {language === 'es' ? 'Escaneos de Seguridad' : 'Security Scans'}
                </h2>
                <p className="text-zinc-400 mb-6">
                  {language === 'es'
                    ? 'Escaneá tu email, username, wallet, teléfono, dominio o IP para encontrar exposiciones de seguridad y filtraciones de datos.'
                    : 'Scan your email, username, wallet, phone, domain, or IP to find security exposures and data breaches.'}
                </p>
                <ul className="space-y-3 mb-8">
                  <ServiceFeature color="purple">
                    {language === 'es' ? 'Acceso a bases de datos con 15B+ registros' : 'Access to databases with 15B+ records'}
                  </ServiceFeature>
                  <ServiceFeature color="purple">
                    {language === 'es' ? 'Escaneos ilimitados' : 'Unlimited scans'}
                  </ServiceFeature>
                  <ServiceFeature color="purple">
                    {language === 'es' ? 'Reportes PDF descargables' : 'Downloadable PDF reports'}
                  </ServiceFeature>
                  <ServiceFeature color="purple">
                    {language === 'es' ? 'Monitoreo de dark web' : 'Dark web monitoring'}
                  </ServiceFeature>
                </ul>
                <Link href="/audit" className="inline-block bg-purple-600 hover:bg-purple-500 px-6 py-3 rounded-xl font-medium transition">
                  {language === 'es' ? 'Empezar a Escanear' : 'Start Scanning'}
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Consulting */}
        <section id="consulting" className="py-20">
          <div className="max-w-6xl mx-auto px-4 text-center">
            <div className="inline-block px-3 py-1 bg-amber-500/10 text-amber-400 text-sm rounded-full mb-4">
              {language === 'es' ? 'Consultoría' : 'Consulting'}
            </div>
            <h2 className="text-4xl font-bold mb-6">
              {language === 'es' ? 'Asesoría 1 a 1' : '1:1 Advisory'}
            </h2>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto mb-12">
              {language === 'es'
                ? 'Para individuos de alto riesgo que necesitan atención personalizada y protección continua.'
                : 'For high-risk individuals who need personalized attention and ongoing protection.'}
            </p>

            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8">
                <h3 className="text-xl font-semibold mb-4">
                  {language === 'es' ? 'Evaluación de Seguridad' : 'Security Assessment'}
                </h3>
                <p className="text-zinc-400 mb-6">
                  {language === 'es'
                    ? 'Evaluación completa de tu postura de seguridad personal o empresarial'
                    : 'Complete evaluation of your personal or business security posture'}
                </p>
                <p className="text-2xl font-bold text-amber-400">$500</p>
                <p className="text-zinc-500 text-sm">{language === 'es' ? 'Único pago' : 'One-time'}</p>
              </div>
              <div className="bg-zinc-900 border border-amber-500/50 rounded-2xl p-8 relative">
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-amber-500 text-black text-xs font-medium rounded-full">
                  {language === 'es' ? 'Popular' : 'Popular'}
                </div>
                <h3 className="text-xl font-semibold mb-4">
                  {language === 'es' ? 'Respuesta a Incidentes' : 'Incident Response'}
                </h3>
                <p className="text-zinc-400 mb-6">
                  {language === 'es'
                    ? 'Soporte 24/7 para incidentes de seguridad, breaches y emergencias'
                    : '24/7 support for security incidents, breaches, and emergencies'}
                </p>
                <p className="text-2xl font-bold text-amber-400">$200/{language === 'es' ? 'hora' : 'hr'}</p>
                <p className="text-zinc-500 text-sm">{language === 'es' ? 'Según necesidad' : 'As needed'}</p>
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8">
                <h3 className="text-xl font-semibold mb-4">
                  {language === 'es' ? 'Retainer Mensual' : 'Monthly Retainer'}
                </h3>
                <p className="text-zinc-400 mb-6">
                  {language === 'es'
                    ? 'Asesor de seguridad continuo para protección permanente'
                    : 'Ongoing security advisor for continuous protection'}
                </p>
                <p className="text-2xl font-bold text-amber-400">$2,000/{language === 'es' ? 'mes' : 'mo'}</p>
                <p className="text-zinc-500 text-sm">{language === 'es' ? 'Facturado mensualmente' : 'Billed monthly'}</p>
              </div>
            </div>

            <div className="mt-12">
              <Link href="/contact" className="inline-block bg-amber-600 hover:bg-amber-500 px-8 py-4 rounded-xl font-medium transition">
                {language === 'es' ? 'Agendar Consulta' : 'Schedule a Consultation'}
              </Link>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-20 bg-gradient-to-r from-emerald-900/50 to-purple-900/50">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-4xl font-bold mb-6">
              {language === 'es' ? '¿No Sabés Por Dónde Empezar?' : 'Not Sure Where to Start?'}
            </h2>
            <p className="text-xl text-zinc-300 mb-8">
              {language === 'es'
                ? 'Empezá con el checklist gratuito para entender tu nivel de seguridad actual.'
                : 'Start with the free checklist to understand your current security level.'}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/checklist"
                className="bg-white text-black px-8 py-4 rounded-xl font-semibold text-lg hover:bg-zinc-200 transition"
              >
                {language === 'es' ? 'Empezar Gratis' : 'Start Free'}
              </Link>
              <Link
                href="/pricing"
                className="border border-white/50 hover:border-white px-8 py-4 rounded-xl font-semibold text-lg transition"
              >
                {language === 'es' ? 'Ver Precios' : 'View Pricing'}
              </Link>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  )
}

function ServiceFeature({ children, color }: { children: React.ReactNode; color: 'emerald' | 'purple' | 'amber' }) {
  const colorClass = {
    emerald: 'text-emerald-400',
    purple: 'text-purple-400',
    amber: 'text-amber-400',
  }[color]

  return (
    <li className="flex items-center gap-3 text-zinc-300">
      <svg className={`w-5 h-5 ${colorClass}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
      {children}
    </li>
  )
}
