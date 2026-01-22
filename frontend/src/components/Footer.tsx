'use client'

import Link from 'next/link'
import { useLanguage } from '@/i18n'

export default function Footer() {
  const { t } = useLanguage()

  return (
    <footer className="bg-zinc-950 border-t border-zinc-800">
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center font-bold text-black">
                FK
              </div>
              <span className="font-bold text-xl">FK94</span>
            </Link>
            <p className="text-zinc-500 text-sm">
              {t.footer.tagline}
            </p>
          </div>

          {/* Free Tools */}
          <div>
            <h4 className="font-semibold mb-4 text-zinc-300">{t.footer.freeTools}</h4>
            <ul className="space-y-2 text-zinc-500">
              <li>
                <Link href="/checklist" className="hover:text-white transition">
                  {t.nav.checklist}
                </Link>
              </li>
              <li>
                <Link href="/harden" className="hover:text-white transition">
                  {t.nav.harden}
                </Link>
              </li>
            </ul>
          </div>

          {/* Premium */}
          <div>
            <h4 className="font-semibold mb-4 text-zinc-300">{t.footer.premium}</h4>
            <ul className="space-y-2 text-zinc-500">
              <li>
                <Link href="/audit" className="hover:text-white transition">
                  {t.footer.securityScan}
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="hover:text-white transition">
                  {t.nav.pricing}
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-semibold mb-4 text-zinc-300">{t.footer.company}</h4>
            <ul className="space-y-2 text-zinc-500">
              <li>
                <Link href="/contact" className="hover:text-white transition">
                  {t.footer.contact}
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/fk94security"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition"
                >
                  GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-zinc-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-zinc-600 text-sm">
            &copy; {new Date().getFullYear()} FK94 Security
          </p>
          <div className="flex gap-6 text-zinc-600 text-sm">
            <Link href="/privacy" className="hover:text-white transition">
              {t.footer.privacy}
            </Link>
            <Link href="/terms" className="hover:text-white transition">
              {t.footer.terms}
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
