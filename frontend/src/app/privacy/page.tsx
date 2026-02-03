'use client'

import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import { useLanguage } from '@/i18n'

export default function PrivacyPage() {
  const { language } = useLanguage()
  const isEs = language === 'es'

  return (
    <>
      <Navbar />

      <main className="min-h-screen pt-20">
        <section className="py-20 bg-gradient-to-b from-emerald-500/10 to-transparent">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h1 className="text-5xl font-bold mb-6">
              {isEs ? 'Política de Privacidad' : 'Privacy Policy'}
            </h1>
            <p className="text-xl text-zinc-400">
              {isEs ? 'Última actualización: Febrero 2026' : 'Last updated: February 2026'}
            </p>
          </div>
        </section>

        <section className="py-16">
          <div className="max-w-4xl mx-auto px-4 space-y-12">
            {/* Section 1 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '1. Información que Recopilamos' : '1. Information We Collect'}
              </h2>
              <div className="text-zinc-400 leading-relaxed space-y-3">
                <p>
                  {isEs
                    ? 'Recopilamos la siguiente información cuando usás nuestro Servicio:'
                    : 'We collect the following information when you use our Service:'}
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>
                    <strong className="text-zinc-300">{isEs ? 'Datos de cuenta:' : 'Account data:'}</strong>{' '}
                    {isEs
                      ? 'Email y datos de autenticación cuando creás una cuenta (procesados por Supabase).'
                      : 'Email and authentication data when you create an account (processed by Supabase).'}
                  </li>
                  <li>
                    <strong className="text-zinc-300">{isEs ? 'Datos de escaneo:' : 'Scan data:'}</strong>{' '}
                    {isEs
                      ? 'Los datos que ingresás para escaneos (emails, usernames, etc.) se procesan en tiempo real y no se almacenan permanentemente en nuestros servidores.'
                      : 'Data you input for scans (emails, usernames, etc.) is processed in real-time and is not permanently stored on our servers.'}
                  </li>
                  <li>
                    <strong className="text-zinc-300">{isEs ? 'Datos de uso:' : 'Usage data:'}</strong>{' '}
                    {isEs
                      ? 'Información técnica como tipo de navegador, dirección IP, y patrones de uso general.'
                      : 'Technical information such as browser type, IP address, and general usage patterns.'}
                  </li>
                  <li>
                    <strong className="text-zinc-300">{isEs ? 'Datos de pago:' : 'Payment data:'}</strong>{' '}
                    {isEs
                      ? 'Los pagos son procesados por Stripe. No almacenamos datos de tarjetas de crédito.'
                      : 'Payments are processed by Stripe. We do not store credit card data.'}
                  </li>
                </ul>
              </div>
            </div>

            {/* Section 2 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '2. Cómo Usamos tu Información' : '2. How We Use Your Information'}
              </h2>
              <div className="text-zinc-400 leading-relaxed space-y-3">
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>{isEs ? 'Para proveer y mantener el Servicio.' : 'To provide and maintain the Service.'}</li>
                  <li>{isEs ? 'Para procesar tus escaneos de seguridad.' : 'To process your security scans.'}</li>
                  <li>{isEs ? 'Para gestionar tu cuenta y suscripción.' : 'To manage your account and subscription.'}</li>
                  <li>{isEs ? 'Para mejorar y optimizar el Servicio.' : 'To improve and optimize the Service.'}</li>
                  <li>{isEs ? 'Para comunicarnos contigo sobre actualizaciones del Servicio.' : 'To communicate with you about Service updates.'}</li>
                </ul>
              </div>
            </div>

            {/* Section 3 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '3. Seguridad de Passwords' : '3. Password Security'}
              </h2>
              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-6">
                <p className="text-zinc-300 leading-relaxed">
                  {isEs
                    ? 'Cuando verificás un password en nuestro servicio, usamos el protocolo k-anonymity de Have I Been Pwned. Tu password NUNCA se envía a nuestros servidores ni a terceros. Solo se envía un hash parcial (los primeros 5 caracteres del hash SHA-1), lo que hace imposible reconstruir tu password.'
                    : 'When you check a password in our service, we use the k-anonymity protocol from Have I Been Pwned. Your password is NEVER sent to our servers or third parties. Only a partial hash (the first 5 characters of the SHA-1 hash) is sent, making it impossible to reconstruct your password.'}
                </p>
              </div>
            </div>

            {/* Section 4 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '4. Herramientas Gratuitas' : '4. Free Tools'}
              </h2>
              <p className="text-zinc-400 leading-relaxed">
                {isEs
                  ? 'Las herramientas gratuitas (Checklist OPSEC y Scripts de Hardening) funcionan completamente en tu navegador. Tu progreso del checklist se almacena localmente en tu dispositivo (localStorage) y nunca se envía a nuestros servidores.'
                  : 'Free tools (OPSEC Checklist and Hardening Scripts) run entirely in your browser. Your checklist progress is stored locally on your device (localStorage) and is never sent to our servers.'}
              </p>
            </div>

            {/* Section 5 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '5. Servicios de Terceros' : '5. Third-Party Services'}
              </h2>
              <div className="text-zinc-400 leading-relaxed space-y-3">
                <p>{isEs ? 'Utilizamos los siguientes servicios de terceros:' : 'We use the following third-party services:'}</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong className="text-zinc-300">Supabase:</strong> {isEs ? 'Autenticación y gestión de usuarios.' : 'Authentication and user management.'}</li>
                  <li><strong className="text-zinc-300">Stripe:</strong> {isEs ? 'Procesamiento de pagos.' : 'Payment processing.'}</li>
                  <li><strong className="text-zinc-300">Have I Been Pwned:</strong> {isEs ? 'Verificación de brechas de datos.' : 'Data breach verification.'}</li>
                  <li><strong className="text-zinc-300">Vercel:</strong> {isEs ? 'Hosting del frontend.' : 'Frontend hosting.'}</li>
                  <li><strong className="text-zinc-300">Render:</strong> {isEs ? 'Hosting del backend.' : 'Backend hosting.'}</li>
                </ul>
              </div>
            </div>

            {/* Section 6 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '6. Retención de Datos' : '6. Data Retention'}
              </h2>
              <p className="text-zinc-400 leading-relaxed">
                {isEs
                  ? 'Los resultados de escaneos se retienen temporalmente para generar reportes y análisis AI. Los datos de cuenta se retienen mientras tu cuenta esté activa. Podés solicitar la eliminación de tu cuenta y datos asociados en cualquier momento contactándonos.'
                  : 'Scan results are retained temporarily to generate reports and AI analysis. Account data is retained while your account is active. You can request deletion of your account and associated data at any time by contacting us.'}
              </p>
            </div>

            {/* Section 7 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '7. Tus Derechos' : '7. Your Rights'}
              </h2>
              <div className="text-zinc-400 leading-relaxed space-y-3">
                <p>{isEs ? 'Tenés derecho a:' : 'You have the right to:'}</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>{isEs ? 'Acceder a tus datos personales.' : 'Access your personal data.'}</li>
                  <li>{isEs ? 'Solicitar la corrección de datos inexactos.' : 'Request correction of inaccurate data.'}</li>
                  <li>{isEs ? 'Solicitar la eliminación de tus datos.' : 'Request deletion of your data.'}</li>
                  <li>{isEs ? 'Exportar tus datos en un formato legible.' : 'Export your data in a readable format.'}</li>
                  <li>{isEs ? 'Revocar tu consentimiento en cualquier momento.' : 'Revoke your consent at any time.'}</li>
                </ul>
              </div>
            </div>

            {/* Section 8 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '8. Contacto' : '8. Contact'}
              </h2>
              <p className="text-zinc-400 leading-relaxed">
                {isEs
                  ? 'Para preguntas sobre privacidad o para ejercer tus derechos, contactanos en '
                  : 'For privacy questions or to exercise your rights, contact us at '}
                <a href="mailto:contact@fk94security.com" className="text-emerald-400 hover:text-emerald-300 transition">
                  contact@fk94security.com
                </a>
              </p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  )
}
