'use client'

import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import { useLanguage } from '@/i18n'

export default function AboutPage() {
  const { language } = useLanguage()

  return (
    <>
      <Navbar />

      <main className="min-h-screen pt-20">
        {/* Hero */}
        <section className="py-20 bg-gradient-to-b from-emerald-500/10 to-transparent">
          <div className="max-w-6xl mx-auto px-4 text-center">
            <h1 className="text-5xl font-bold mb-6">
              {language === 'es' ? 'Sobre FK94 Security' : 'About FK94 Security'}
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              {language === 'es'
                ? 'Herramientas de OPSEC y privacidad para todos'
                : 'OPSEC and privacy tools for everyone'}
            </p>
          </div>
        </section>

        {/* Mission */}
        <section className="py-20">
          <div className="max-w-4xl mx-auto px-4">
            <div className="prose prose-invert prose-lg mx-auto">
              <h2 className="text-3xl font-bold mb-6">
                {language === 'es' ? 'Nuestra Misión' : 'Our Mission'}
              </h2>
              <p className="text-zinc-400 mb-6">
                {language === 'es'
                  ? 'En una era donde las filtraciones de datos son cada vez más comunes y la información personal está constantemente en riesgo, FK94 Security fue fundada con una misión clara: hacer que la seguridad de nivel profesional sea accesible para todos.'
                  : 'In an era where data breaches are increasingly common and personal information is constantly at risk, FK94 Security was founded with a clear mission: to make professional-grade security accessible to everyone.'}
              </p>
              <p className="text-zinc-400 mb-6">
                {language === 'es'
                  ? 'Creemos que todos merecen saber si sus datos personales han sido comprometidos y tener las herramientas para protegerse. Por eso ofrecemos herramientas gratuitas de OPSEC y hardening, además de escaneos premium para quienes necesitan verificar su exposición.'
                  : 'We believe everyone deserves to know if their personal data has been compromised and have the tools to protect themselves. That\'s why we offer free OPSEC and hardening tools, plus premium scans for those who need to verify their exposure.'}
              </p>

              <h2 className="text-3xl font-bold mb-6 mt-12">
                {language === 'es' ? 'Qué Hacemos' : 'What We Do'}
              </h2>
              <p className="text-zinc-400 mb-6">
                {language === 'es'
                  ? 'FK94 Security combina educación en OPSEC con herramientas prácticas y acceso a bases de datos de filtraciones para proporcionar evaluaciones de seguridad completas.'
                  : 'FK94 Security combines OPSEC education with practical tools and breach database access to provide comprehensive security assessments.'}
              </p>

              <div className="grid md:grid-cols-2 gap-8 my-12">
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                  <div className="text-4xl mb-4">📋</div>
                  <h3 className="text-xl font-semibold mb-2">
                    {language === 'es' ? 'Educación OPSEC' : 'OPSEC Education'}
                  </h3>
                  <p className="text-zinc-400 text-sm">
                    {language === 'es'
                      ? 'Checklist interactivo con 54 prácticas de seguridad organizadas por prioridad.'
                      : 'Interactive checklist with 54 security practices organized by priority.'}
                  </p>
                </div>
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                  <div className="text-4xl mb-4">🛡️</div>
                  <h3 className="text-xl font-semibold mb-2">
                    {language === 'es' ? 'Scripts de Hardening' : 'Hardening Scripts'}
                  </h3>
                  <p className="text-zinc-400 text-sm">
                    {language === 'es'
                      ? 'Scripts personalizados para asegurar Mac, Windows y Linux según tu perfil de riesgo.'
                      : 'Custom scripts to secure Mac, Windows, and Linux based on your risk profile.'}
                  </p>
                </div>
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                  <div className="text-4xl mb-4">🔍</div>
                  <h3 className="text-xl font-semibold mb-2">
                    {language === 'es' ? 'Escaneos de Seguridad' : 'Security Scans'}
                  </h3>
                  <p className="text-zinc-400 text-sm">
                    {language === 'es'
                      ? 'Verificá emails, usernames, wallets, teléfonos y dominios en bases de datos de filtraciones.'
                      : 'Check emails, usernames, wallets, phones, and domains against breach databases.'}
                  </p>
                </div>
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                  <div className="text-4xl mb-4">👤</div>
                  <h3 className="text-xl font-semibold mb-2">
                    {language === 'es' ? 'Consultoría 1:1' : '1:1 Consulting'}
                  </h3>
                  <p className="text-zinc-400 text-sm">
                    {language === 'es'
                      ? 'Asesoría personalizada para individuos de alto riesgo que necesitan protección continua.'
                      : 'Personalized advisory for high-risk individuals who need ongoing protection.'}
                  </p>
                </div>
              </div>

              <h2 className="text-3xl font-bold mb-6 mt-12">
                {language === 'es' ? 'Nuestra Tecnología' : 'Our Technology'}
              </h2>
              <p className="text-zinc-400 mb-6">
                {language === 'es'
                  ? 'Utilizamos múltiples fuentes de datos y tecnología de vanguardia para proporcionar análisis de seguridad completos:'
                  : 'We leverage multiple data sources and cutting-edge technology to provide comprehensive security analysis:'}
              </p>
              <ul className="text-zinc-400 space-y-3">
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-400 mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>
                    <strong>Have I Been Pwned (HIBP)</strong> - {language === 'es' ? 'El servicio de notificación de filtraciones más grande del mundo' : 'The world\'s largest breach notification service'}
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-400 mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>
                    <strong>Dehashed</strong> - {language === 'es' ? 'Base de datos con 15+ mil millones de registros' : 'Database with 15+ billion records'}
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-400 mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>
                    <strong>{language === 'es' ? 'Herramientas OSINT' : 'OSINT Tools'}</strong> - {language === 'es' ? 'Inteligencia de fuentes abiertas para análisis de huella digital' : 'Open source intelligence for digital footprint analysis'}
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Expertise */}
        <section className="py-20 bg-zinc-950">
          <div className="max-w-6xl mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">
              {language === 'es' ? 'Nuestra Expertise' : 'Our Expertise'}
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-center">
                <div className="w-20 h-20 bg-emerald-500/20 rounded-full mx-auto mb-6 flex items-center justify-center">
                  <svg className="w-10 h-10 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">OPSEC</h3>
                <p className="text-zinc-400">
                  {language === 'es'
                    ? 'Seguridad operacional para proteger tu identidad y actividades'
                    : 'Operational security to protect your identity and activities'}
                </p>
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-center">
                <div className="w-20 h-20 bg-blue-500/20 rounded-full mx-auto mb-6 flex items-center justify-center">
                  <svg className="w-10 h-10 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">OSINT</h3>
                <p className="text-zinc-400">
                  {language === 'es'
                    ? 'Recolección y análisis de inteligencia de fuentes abiertas'
                    : 'Open source intelligence gathering and analysis'}
                </p>
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 text-center">
                <div className="w-20 h-20 bg-purple-500/20 rounded-full mx-auto mb-6 flex items-center justify-center">
                  <svg className="w-10 h-10 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">{language === 'es' ? 'Privacidad' : 'Privacy'}</h3>
                <p className="text-zinc-400">
                  {language === 'es'
                    ? 'Protección de privacidad personal y reducción de huella digital'
                    : 'Personal privacy protection and digital footprint reduction'}
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-20">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold mb-6">
              {language === 'es' ? '¿Querés Saber Más?' : 'Want to Learn More?'}
            </h2>
            <p className="text-xl text-zinc-400 mb-8">
              {language === 'es'
                ? 'Empezá con el checklist gratuito o contactanos para discutir tus necesidades de seguridad.'
                : 'Start with the free checklist or contact us to discuss your security needs.'}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/checklist"
                className="bg-emerald-600 hover:bg-emerald-500 px-8 py-4 rounded-xl font-semibold text-lg transition"
              >
                {language === 'es' ? 'Empezar Gratis' : 'Start Free'}
              </Link>
              <Link
                href="/contact"
                className="border border-zinc-700 hover:border-zinc-500 px-8 py-4 rounded-xl font-semibold text-lg transition"
              >
                {language === 'es' ? 'Contactanos' : 'Contact Us'}
              </Link>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  )
}
