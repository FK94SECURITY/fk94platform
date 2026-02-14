'use client'

import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import { useLanguage } from '@/i18n'

export default function TermsPage() {
  const { language } = useLanguage()
  const isEs = language === 'es'

  return (
    <>
      <Navbar />

      <main className="min-h-screen pt-20">
        <section className="py-20 bg-gradient-to-b from-emerald-500/10 to-transparent">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h1 className="text-5xl font-bold mb-6">
              {isEs ? 'Términos de Servicio' : 'Terms of Service'}
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
                {isEs ? '1. Aceptación de los Términos' : '1. Acceptance of Terms'}
              </h2>
              <p className="text-zinc-400 leading-relaxed">
                {isEs
                  ? 'Al acceder y utilizar FK94 Security ("el Servicio"), aceptás cumplir con estos Términos de Servicio. Si no estás de acuerdo con alguna parte de estos términos, no podés acceder al Servicio.'
                  : 'By accessing and using FK94 Security ("the Service"), you agree to be bound by these Terms of Service. If you disagree with any part of these terms, you may not access the Service.'}
              </p>
            </div>

            {/* Section 2 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '2. Descripción del Servicio' : '2. Description of Service'}
              </h2>
              <p className="text-zinc-400 leading-relaxed">
                {isEs
                  ? 'FK94 Security proporciona herramientas de ciberseguridad y OSINT (Open Source Intelligence) incluyendo: checklists de seguridad, scripts de hardening, escaneos de brechas de datos, análisis de wallets crypto, y reportes de seguridad. Ofrecemos herramientas gratuitas y servicios premium por suscripción.'
                  : 'FK94 Security provides cybersecurity and OSINT (Open Source Intelligence) tools including: security checklists, hardening scripts, data breach scanning, crypto wallet analysis, and security reports. We offer free tools and premium subscription-based services.'}
              </p>
            </div>

            {/* Section 3 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '3. Uso Aceptable' : '3. Acceptable Use'}
              </h2>
              <div className="text-zinc-400 leading-relaxed space-y-3">
                <p>
                  {isEs
                    ? 'Al utilizar el Servicio, aceptás que:'
                    : 'By using the Service, you agree that:'}
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>
                    {isEs
                      ? 'Solo escanearás datos que te pertenezcan o para los que tengas autorización explícita.'
                      : 'You will only scan data that belongs to you or for which you have explicit authorization.'}
                  </li>
                  <li>
                    {isEs
                      ? 'No usarás el Servicio para actividades ilegales, acoso, o vigilancia no autorizada.'
                      : 'You will not use the Service for illegal activities, harassment, or unauthorized surveillance.'}
                  </li>
                  <li>
                    {isEs
                      ? 'No intentarás evadir límites de uso o medidas de seguridad.'
                      : 'You will not attempt to bypass usage limits or security measures.'}
                  </li>
                  <li>
                    {isEs
                      ? 'No redistribuirás ni revenderás los datos obtenidos a través del Servicio.'
                      : 'You will not redistribute or resell data obtained through the Service.'}
                  </li>
                </ul>
              </div>
            </div>

            {/* Section 4 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '4. Cuentas y Suscripciones' : '4. Accounts and Subscriptions'}
              </h2>
              <div className="text-zinc-400 leading-relaxed space-y-3">
                <p>
                  {isEs
                    ? 'Para acceder a funciones premium, necesitás crear una cuenta y suscribirte a un plan de pago. Sos responsable de mantener la confidencialidad de tu cuenta.'
                    : 'To access premium features, you need to create an account and subscribe to a paid plan. You are responsible for maintaining the confidentiality of your account.'}
                </p>
                <p>
                  {isEs
                    ? 'Los pagos se procesan a través de Stripe. Las suscripciones se renuevan automáticamente a menos que canceles antes de la fecha de renovación. No ofrecemos reembolsos por períodos parciales.'
                    : 'Payments are processed through Stripe. Subscriptions renew automatically unless you cancel before the renewal date. We do not offer refunds for partial periods.'}
                </p>
              </div>
            </div>

            {/* Section 5 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '5. Propiedad Intelectual' : '5. Intellectual Property'}
              </h2>
              <p className="text-zinc-400 leading-relaxed">
                {isEs
                  ? 'El Servicio y su contenido original, características y funcionalidad son propiedad de FK94 Security y están protegidos por leyes internacionales de derechos de autor, marcas registradas y otros derechos de propiedad intelectual.'
                  : 'The Service and its original content, features, and functionality are owned by FK94 Security and are protected by international copyright, trademark, and other intellectual property laws.'}
              </p>
            </div>

            {/* Section 6 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '6. Limitación de Responsabilidad' : '6. Limitation of Liability'}
              </h2>
              <div className="text-zinc-400 leading-relaxed space-y-3">
                <p>
                  {isEs
                    ? 'El Servicio se proporciona "tal cual" y "según disponibilidad". FK94 Security no garantiza que los resultados de los escaneos sean completos o exactos. No nos hacemos responsables por:'
                    : 'The Service is provided "as is" and "as available." FK94 Security does not guarantee that scan results are complete or accurate. We are not liable for:'}
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>
                    {isEs
                      ? 'Pérdidas directas o indirectas derivadas del uso del Servicio.'
                      : 'Direct or indirect losses resulting from use of the Service.'}
                  </li>
                  <li>
                    {isEs
                      ? 'Acciones tomadas basándose en los resultados de los escaneos.'
                      : 'Actions taken based on scan results.'}
                  </li>
                  <li>
                    {isEs
                      ? 'Interrupciones del servicio o pérdida de datos.'
                      : 'Service interruptions or data loss.'}
                  </li>
                </ul>
              </div>
            </div>

            {/* Section 7 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '7. Cambios en los Términos' : '7. Changes to Terms'}
              </h2>
              <p className="text-zinc-400 leading-relaxed">
                {isEs
                  ? 'Nos reservamos el derecho de modificar estos términos en cualquier momento. Los cambios entrarán en vigencia inmediatamente después de su publicación en el Servicio. El uso continuado del Servicio después de los cambios constituye la aceptación de los nuevos términos.'
                  : 'We reserve the right to modify these terms at any time. Changes will be effective immediately upon posting on the Service. Continued use of the Service after changes constitutes acceptance of the new terms.'}
              </p>
            </div>

            {/* Section 8 */}
            <div>
              <h2 className="text-2xl font-bold mb-4">
                {isEs ? '8. Contacto' : '8. Contact'}
              </h2>
              <p className="text-zinc-400 leading-relaxed">
                {isEs
                  ? 'Si tenés preguntas sobre estos Términos de Servicio, contactanos en '
                  : 'If you have questions about these Terms of Service, contact us at '}
                <a href="mailto:info@fk94security.com" className="text-emerald-400 hover:text-emerald-300 transition">
                  info@fk94security.com
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
