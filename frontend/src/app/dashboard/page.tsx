'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import { useLanguage } from '@/i18n'
import { useAuth } from '@/contexts/AuthContext'
import { getProfile, getAuditHistory, AuditRecord, UserProfile } from '@/lib/db'
import { getRiskColor, getRiskLabel } from '@/lib/api'

export default function DashboardPage() {
  const { language } = useLanguage()
  const { user, loading, isConfigured } = useAuth()
  const router = useRouter()

  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [audits, setAudits] = useState<AuditRecord[]>([])
  const [loadingData, setLoadingData] = useState(true)

  useEffect(() => {
    if (!loading && !user && isConfigured) {
      router.push('/')
    }
  }, [user, loading, isConfigured, router])

  useEffect(() => {
    async function loadData() {
      if (user) {
        const [profileData, auditsData] = await Promise.all([
          getProfile(user.id),
          getAuditHistory(user.id),
        ])
        setProfile(profileData)
        setAudits(auditsData)
      }
      setLoadingData(false)
    }
    if (user) {
      loadData()
    }
  }, [user])

  if (loading || loadingData) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen pt-20">
          <div className="max-w-6xl mx-auto px-4 py-12">
            {/* Header skeleton */}
            <div className="mb-8">
              <div className="h-8 w-48 bg-zinc-800 rounded-lg animate-pulse mb-2" />
              <div className="h-5 w-64 bg-zinc-800/60 rounded-lg animate-pulse" />
            </div>
            {/* Stats skeleton */}
            <div className="grid sm:grid-cols-3 gap-6 mb-12">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                  <div className="h-4 w-24 bg-zinc-800 rounded animate-pulse mb-3" />
                  <div className="h-8 w-16 bg-zinc-800 rounded animate-pulse" />
                </div>
              ))}
            </div>
            {/* Actions skeleton */}
            <div className="flex gap-4 mb-12">
              <div className="h-12 w-36 bg-zinc-800 rounded-xl animate-pulse" />
              <div className="h-12 w-36 bg-zinc-800 rounded-xl animate-pulse" />
            </div>
            {/* History skeleton */}
            <div className="h-6 w-48 bg-zinc-800 rounded animate-pulse mb-6" />
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-zinc-800 rounded-lg animate-pulse" />
                      <div>
                        <div className="h-5 w-40 bg-zinc-800 rounded animate-pulse mb-2" />
                        <div className="h-4 w-28 bg-zinc-800/60 rounded animate-pulse" />
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="h-8 w-12 bg-zinc-800 rounded animate-pulse mb-1" />
                      <div className="h-4 w-16 bg-zinc-800/60 rounded animate-pulse" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
        <Footer />
      </>
    )
  }

  if (!user) {
    return null
  }

  const auditTypeIcons: Record<string, string> = {
    email: '📧',
    username: '👤',
    phone: '📱',
    domain: '🌐',
    name: '🔍',
    ip: '📍',
    wallet: '💰',
  }

  return (
    <>
      <Navbar />

      <main className="min-h-screen pt-20">
        <div className="max-w-6xl mx-auto px-4 py-12">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">
              {language === 'es' ? 'Dashboard' : 'Dashboard'}
            </h1>
            <p className="text-zinc-400">
              {language === 'es'
                ? `Bienvenido, ${user.email}`
                : `Welcome, ${user.email}`}
            </p>
          </div>

          {/* Stats */}
          <div className="grid sm:grid-cols-3 gap-6 mb-12">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <p className="text-zinc-400 text-sm mb-1">
                {language === 'es' ? 'Plan' : 'Plan'}
              </p>
              <p className="text-2xl font-bold capitalize">
                {profile?.plan || 'Free'}
              </p>
            </div>
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <p className="text-zinc-400 text-sm mb-1">
                {language === 'es' ? 'Escaneos Restantes' : 'Scans Remaining'}
              </p>
              <p className="text-2xl font-bold">
                {profile?.plan === 'pro' || profile?.plan === 'enterprise'
                  ? '∞'
                  : profile?.audits_remaining ?? 5}
              </p>
            </div>
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <p className="text-zinc-400 text-sm mb-1">
                {language === 'es' ? 'Total de Escaneos' : 'Total Scans'}
              </p>
              <p className="text-2xl font-bold">{profile?.audits_total || 0}</p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex gap-4 mb-12">
            <Link
              href="/audit"
              className="bg-emerald-600 hover:bg-emerald-500 px-6 py-3 rounded-xl font-medium transition"
            >
              {language === 'es' ? 'Nuevo Escaneo' : 'New Scan'}
            </Link>
            {profile?.plan === 'free' && (
              <Link
                href="/pricing"
                className="bg-purple-600 hover:bg-purple-500 px-6 py-3 rounded-xl font-medium transition"
              >
                {language === 'es' ? 'Upgrade a Pro' : 'Upgrade to Pro'}
              </Link>
            )}
          </div>

          {/* Audit History */}
          <div>
            <h2 className="text-xl font-bold mb-6">
              {language === 'es' ? 'Historial de Escaneos' : 'Scan History'}
            </h2>

            {audits.length === 0 ? (
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-12 text-center">
                <p className="text-zinc-400 mb-4">
                  {language === 'es'
                    ? 'Todavía no realizaste ningún escaneo'
                    : "You haven't performed any scans yet"}
                </p>
                <Link
                  href="/audit"
                  className="inline-block bg-emerald-600 hover:bg-emerald-500 px-6 py-3 rounded-xl font-medium transition"
                >
                  {language === 'es' ? 'Realizar primer escaneo' : 'Run your first scan'}
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {audits.map((audit) => (
                  <div
                    key={audit.id}
                    className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:border-zinc-700 transition"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <span className="text-2xl">
                          {auditTypeIcons[audit.audit_type] || '🔍'}
                        </span>
                        <div>
                          <p className="font-semibold">{audit.query_value}</p>
                          <p className="text-zinc-500 text-sm capitalize">
                            {audit.audit_type} •{' '}
                            {new Date(audit.created_at!).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-2xl font-bold">{audit.security_score}</p>
                          <p
                            className="text-sm font-medium"
                            style={{ color: getRiskColor(audit.risk_level) }}
                          >
                            {getRiskLabel(audit.risk_level)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </>
  )
}
