'use client';

import { useState } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { useLanguage } from '@/i18n';
import { useAuth } from '@/contexts/AuthContext';
import SecurityScoreDisplay from '@/components/SecurityScore';
import AIChat from '@/components/AIChat';
import {
  runFullAudit, runMultiAudit, downloadReport,
  AuditResult, AuditType, getRiskLevel
} from '@/lib/api';
import { saveAudit, canPerformAudit, getProfile } from '@/lib/db';

type Step = 'input' | 'loading' | 'results';

const AUDIT_TYPES: AuditType[] = ['email', 'username', 'phone', 'wallet', 'domain', 'ip'];

// Translated configs
const getAuditTypeConfig = (language: 'en' | 'es') => ({
  email: {
    label: language === 'es' ? 'Email' : 'Email',
    placeholder: 'you@example.com',
    icon: '📧',
    description: language === 'es'
      ? 'Verificá filtraciones de datos y passwords expuestos'
      : 'Check for data breaches and leaked passwords',
  },
  username: {
    label: 'Username',
    placeholder: 'johndoe',
    icon: '👤',
    description: language === 'es'
      ? 'Encontrá cuentas en 300+ plataformas'
      : 'Find accounts across 300+ platforms',
  },
  phone: {
    label: language === 'es' ? 'Teléfono' : 'Phone',
    placeholder: '+1234567890',
    icon: '📱',
    description: language === 'es'
      ? 'Verificá info del carrier y exposición en filtraciones'
      : 'Check carrier info and breach exposure',
  },
  wallet: {
    label: 'Wallet',
    placeholder: '0x... / bc1...',
    icon: '💰',
    description: language === 'es'
      ? 'Verificá si tu wallet está vinculada a tu identidad'
      : 'Check if your wallet is linked to your identity',
  },
  domain: {
    label: language === 'es' ? 'Dominio' : 'Domain',
    placeholder: 'example.com',
    icon: '🌐',
    description: language === 'es'
      ? 'Verificá SSL, DNS, SPF, configuración DMARC'
      : 'Check SSL, DNS, SPF, DMARC configuration',
  },
  name: {
    label: language === 'es' ? 'Nombre' : 'Name',
    placeholder: 'John Doe',
    icon: '🔍',
    description: language === 'es'
      ? 'Buscá información pública'
      : 'Search for public information',
  },
  ip: {
    label: language === 'es' ? 'IP' : 'IP Address',
    placeholder: '8.8.8.8',
    icon: '📍',
    description: language === 'es'
      ? 'Verificá reputación y estado en listas negras'
      : 'Check reputation and blacklist status',
  },
});

export default function AuditPage() {
  const { language } = useLanguage();
  const { user, isConfigured } = useAuth();
  const [step, setStep] = useState<Step>('input');
  const [auditType, setAuditType] = useState<AuditType>('email');
  const [inputValue, setInputValue] = useState('');
  const [passwordValue, setPasswordValue] = useState('');
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [auditsRemaining, setAuditsRemaining] = useState<number | null>(null);

  const configs = getAuditTypeConfig(language);
  const config = configs[auditType];

  const handleAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    // Check if user can perform audit (if logged in)
    if (user && isConfigured) {
      const canAudit = await canPerformAudit(user.id);
      if (!canAudit) {
        setError(language === 'es'
          ? 'Alcanzaste el límite de escaneos gratuitos. Upgrade a Pro para escaneos ilimitados.'
          : 'You reached your free scan limit. Upgrade to Pro for unlimited scans.');
        return;
      }
    }

    setStep('loading');
    setError(null);

    try {
      let result: AuditResult;
      if (auditType === 'email') {
        result = await runFullAudit(inputValue, passwordValue || undefined);
      } else {
        result = await runMultiAudit(auditType, inputValue);
      }
      setAuditResult(result);
      setStep('results');

      // Save to database if user is logged in
      if (user && isConfigured) {
        await saveAudit({
          user_id: user.id,
          audit_type: auditType,
          query_value: inputValue,
          security_score: result.security_score.score,
          risk_level: getRiskLevel(result.security_score),
          result_data: result,
          ai_analysis: result.ai_analysis,
          recommendations: result.recommendations,
        });
        // Update remaining audits count
        const profile = await getProfile(user.id);
        if (profile) {
          setAuditsRemaining(profile.audits_remaining);
        }
      }
    } catch (err) {
      setError(language === 'es'
        ? 'Error al realizar el escaneo. Por favor intentá de nuevo.'
        : 'Error performing scan. Please try again.');
      setStep('input');
    }
  };

  const handleDownloadReport = async () => {
    if (!auditResult || auditType !== 'email') return;

    try {
      const blob = await downloadReport(auditResult.query_value);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `FK94_Security_Report_${auditResult.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(language === 'es' ? 'Error generando reporte PDF' : 'Error generating PDF report');
    }
  };

  const handleNewAudit = () => {
    setStep('input');
    setAuditResult(null);
    setInputValue('');
    setPasswordValue('');
  };

  return (
    <>
      <Navbar />

      <main className="min-h-screen pt-20">
        <div className="max-w-6xl mx-auto px-4 py-12">
          {step === 'input' && (
            <div className="space-y-8">
              <div className="text-center space-y-4 max-w-2xl mx-auto">
                <span className="inline-block px-4 py-1 bg-purple-500/10 border border-purple-500/30 rounded-full text-purple-400 text-sm font-medium">
                  PRO
                </span>
                <h1 className="text-4xl sm:text-5xl font-bold leading-tight">
                  {language === 'es' ? 'Escaneo de Seguridad' : 'Security Scan'}
                </h1>
                <p className="text-xl text-zinc-400">
                  {language === 'es'
                    ? 'Descubrí tu huella digital y exposición de seguridad'
                    : 'Discover your digital footprint and security exposure'}
                </p>
              </div>

              {/* Audit Type Tabs */}
              <div className="flex flex-wrap justify-center gap-2">
                {AUDIT_TYPES.map((type) => (
                  <button
                    key={type}
                    onClick={() => {
                      setAuditType(type);
                      setInputValue('');
                      setPasswordValue('');
                    }}
                    className={`px-4 py-2 rounded-lg font-medium transition flex items-center gap-2 ${
                      auditType === type
                        ? 'bg-emerald-600 text-white'
                        : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                    }`}
                  >
                    <span>{configs[type].icon}</span>
                    <span>{configs[type].label}</span>
                  </button>
                ))}
              </div>

              {/* Input Form */}
              <form onSubmit={handleAudit} className="max-w-xl mx-auto">
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                  <p className="text-zinc-400 text-sm mb-4 text-center">
                    {config.description}
                  </p>
                  <div className="space-y-3">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder={config.placeholder}
                        className="flex-1 bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 focus:border-emerald-500 focus:outline-none transition"
                        required
                      />
                      <button
                        type="submit"
                        className="bg-emerald-600 hover:bg-emerald-500 px-6 py-3 rounded-lg font-medium transition whitespace-nowrap"
                      >
                        {language === 'es' ? 'Escanear' : 'Scan'}
                      </button>
                    </div>
                    {auditType === 'email' && (
                      <div>
                        <input
                          type="password"
                          value={passwordValue}
                          onChange={(e) => setPasswordValue(e.target.value)}
                          placeholder={language === 'es' ? 'Password a verificar (opcional)' : 'Password to check (optional)'}
                          className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 focus:border-emerald-500 focus:outline-none transition"
                        />
                        <p className="text-xs text-zinc-500 mt-1">
                          {language === 'es'
                            ? '🔒 Tu password nunca se envía - usamos k-anonymity (HIBP)'
                            : '🔒 Your password is never sent - we use k-anonymity (HIBP)'}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </form>

              {error && (
                <div className="max-w-xl mx-auto bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg text-center">
                  {error}
                </div>
              )}

              {/* Features Grid */}
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-12">
                {AUDIT_TYPES.map((type) => (
                  <div
                    key={type}
                    onClick={() => setAuditType(type)}
                    className={`bg-zinc-900/50 rounded-xl border p-6 cursor-pointer transition ${
                      auditType === type
                        ? 'border-emerald-500'
                        : 'border-zinc-800 hover:border-zinc-700'
                    }`}
                  >
                    <div className="text-3xl mb-3">{configs[type].icon}</div>
                    <h3 className="text-lg font-semibold mb-2">{configs[type].label}</h3>
                    <p className="text-zinc-400 text-sm">{configs[type].description}</p>
                  </div>
                ))}
              </div>

              {/* Pro Notice */}
              <div className="max-w-xl mx-auto bg-gradient-to-r from-purple-900/30 to-emerald-900/30 border border-purple-500/30 rounded-xl p-6 text-center">
                <h3 className="font-semibold mb-2">
                  {language === 'es' ? '¿No tenés cuenta Pro?' : 'Don\'t have a Pro account?'}
                </h3>
                <p className="text-zinc-400 text-sm mb-4">
                  {language === 'es'
                    ? 'Obtené acceso ilimitado a todos los escaneos por solo $10/mes'
                    : 'Get unlimited access to all scans for just $10/month'}
                </p>
                <Link
                  href="/pricing"
                  className="inline-block bg-emerald-600 hover:bg-emerald-500 px-6 py-2 rounded-lg font-medium transition"
                >
                  {language === 'es' ? 'Ver Planes' : 'View Plans'}
                </Link>
              </div>
            </div>
          )}

          {step === 'loading' && (
            <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6">
              <div className="w-20 h-20 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
              <div className="text-center">
                <h2 className="text-2xl font-bold mb-2">
                  {language === 'es' ? `Analizando ${config.label}...` : `Analyzing ${config.label}...`}
                </h2>
                <p className="text-zinc-400">
                  {language === 'es' ? 'Esto puede tomar unos segundos' : 'This may take a few seconds'}
                </p>
              </div>
            </div>
          )}

          {step === 'results' && auditResult && (
            <div className="space-y-8">
              <button
                onClick={handleNewAudit}
                className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                {language === 'es' ? 'Nuevo Escaneo' : 'New Scan'}
              </button>

              {/* Results Header */}
              <div className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-6">
                <div className="flex items-center gap-4 mb-4">
                  <span className="text-3xl">{configs[auditResult.audit_type]?.icon || '🔍'}</span>
                  <div>
                    <p className="text-zinc-400 text-sm">
                      {configs[auditResult.audit_type]?.label || auditResult.audit_type} {language === 'es' ? 'Escaneo' : 'Scan'}
                    </p>
                    <p className="text-xl font-semibold">{auditResult.query_value}</p>
                  </div>
                </div>
              </div>

              <div className="grid lg:grid-cols-2 gap-8">
                <div className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-8">
                  <h2 className="text-xl font-bold mb-6 text-center">
                    {language === 'es' ? 'Puntaje de Seguridad' : 'Security Score'}
                  </h2>
                  <SecurityScoreDisplay score={auditResult.security_score} email={auditResult.query_value} />
                </div>

                <div>
                  <h2 className="text-xl font-bold mb-6">
                    {language === 'es' ? 'Asistente de Seguridad' : 'Security Assistant'}
                  </h2>
                  <AIChat auditContext={auditResult} />
                </div>
              </div>

              {/* Type-specific Results */}
              {renderTypeSpecificResults(auditResult, language)}

              {/* Recommendations */}
              <div className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-8">
                <h2 className="text-xl font-bold mb-6">
                  {language === 'es' ? 'Recomendaciones' : 'Recommendations'}
                </h2>
                <div className="space-y-4">
                  {auditResult.recommendations.map((rec, i) => (
                    <div key={i} className="flex gap-3 p-4 bg-zinc-800/50 rounded-lg">
                      <span className="text-emerald-400 font-bold">{i + 1}.</span>
                      <p className="text-zinc-300">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* AI Analysis */}
              {auditResult.ai_analysis && (
                <div className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-8">
                  <h2 className="text-xl font-bold mb-6">
                    {language === 'es' ? 'Análisis AI' : 'AI Analysis'}
                  </h2>
                  <p className="text-zinc-300 whitespace-pre-wrap">{auditResult.ai_analysis}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex flex-wrap gap-4 justify-center">
                {auditResult.audit_type === 'email' && (
                  <button
                    onClick={handleDownloadReport}
                    className="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 font-semibold rounded-xl transition-all"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {language === 'es' ? 'Descargar Reporte PDF' : 'Download PDF Report'}
                  </button>
                )}
                <Link
                  href="/pricing"
                  className="flex items-center gap-2 px-6 py-3 bg-zinc-700 hover:bg-zinc-600 font-semibold rounded-xl transition-all"
                >
                  {language === 'es' ? 'Obtener Acceso Completo' : 'Get Full Access'}
                </Link>
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </>
  );
}

function renderTypeSpecificResults(result: AuditResult, language: 'en' | 'es') {
  const sections = [];

  // Password exposure (HIBP Passwords - Real data!)
  if (result.password_exposure) {
    const pe = result.password_exposure;
    sections.push(
      <div key="password" className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-8">
        <h2 className="text-xl font-bold mb-6">
          {language === 'es' ? 'Verificación de Password' : 'Password Check'}
        </h2>
        {pe.found ? (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-4xl">🚨</span>
              <div>
                <h3 className="text-xl font-bold text-red-400">
                  {language === 'es' ? 'Password Comprometido!' : 'Password Compromised!'}
                </h3>
                <p className="text-zinc-400">
                  {language === 'es'
                    ? `Encontrado ${pe.count.toLocaleString()} veces en filtraciones de datos`
                    : `Found ${pe.count.toLocaleString()} times in data breaches`}
                </p>
              </div>
            </div>
            <p className="text-sm text-red-300">
              {language === 'es'
                ? '⚠️ Deberías cambiar este password inmediatamente en todos los sitios donde lo uses.'
                : '⚠️ You should change this password immediately on all sites where you use it.'}
            </p>
          </div>
        ) : (
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-6">
            <div className="flex items-center gap-3">
              <span className="text-4xl">✅</span>
              <div>
                <h3 className="text-xl font-bold text-emerald-400">
                  {language === 'es' ? 'Password Seguro' : 'Password Safe'}
                </h3>
                <p className="text-zinc-400">
                  {language === 'es'
                    ? 'Este password no aparece en filtraciones conocidas'
                    : 'This password does not appear in known breaches'}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Email breaches
  if (result.breach_check && result.breach_check.breached) {
    sections.push(
      <div key="breaches" className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-8">
        <h2 className="text-xl font-bold mb-6">
          {language === 'es'
            ? `Filtraciones Encontradas (${result.breach_check.breach_count})`
            : `Breaches Found (${result.breach_check.breach_count})`}
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {result.breach_check.breaches.map((breach, i) => (
            <div key={i} className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
              <h3 className="font-semibold text-red-400">{breach.name}</h3>
              {breach.date && <p className="text-sm text-zinc-500">{breach.date}</p>}
              {breach.data_types.length > 0 && (
                <p className="text-sm text-zinc-400 mt-2">
                  {language === 'es' ? 'Expuesto' : 'Exposed'}: {breach.data_types.slice(0, 3).join(', ')}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  // If we have sections for email type, return them
  if (sections.length > 0 && result.audit_type === 'email') {
    return <>{sections}</>;
  }

  // Username results
  if (result.username_result) {
    const ur = result.username_result;
    return (
      <div className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-8">
        <h2 className="text-xl font-bold mb-6">
          {language === 'es'
            ? `Plataformas Encontradas (${ur.platforms_found.length}/${ur.platforms_checked})`
            : `Platforms Found (${ur.platforms_found.length}/${ur.platforms_checked})`}
        </h2>
        {ur.platforms_found.length > 0 ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {ur.platforms_found.map((platform, i) => (
              <a
                key={i}
                href={ur.profile_urls[i]}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 hover:bg-blue-500/20 transition"
              >
                <p className="font-semibold text-blue-400">{platform}</p>
                <p className="text-xs text-zinc-500 truncate">{ur.profile_urls[i]}</p>
              </a>
            ))}
          </div>
        ) : (
          <p className="text-zinc-400">
            {language === 'es'
              ? 'No se encontraron cuentas con este username.'
              : 'No accounts found with this username.'}
          </p>
        )}
      </div>
    );
  }

  // Domain results
  if (result.domain_result) {
    const dr = result.domain_result;
    return (
      <div className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-8">
        <h2 className="text-xl font-bold mb-6">
          {language === 'es' ? 'Seguridad del Dominio' : 'Domain Security'}
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className={`p-4 rounded-lg ${dr.ssl_valid ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
            <p className="text-sm text-zinc-400">{language === 'es' ? 'Certificado SSL' : 'SSL Certificate'}</p>
            <p className={`font-semibold ${dr.ssl_valid ? 'text-emerald-400' : 'text-red-400'}`}>
              {dr.ssl_valid ? (language === 'es' ? 'Válido' : 'Valid') : (language === 'es' ? 'Inválido/Faltante' : 'Invalid/Missing')}
            </p>
          </div>
          <div className={`p-4 rounded-lg ${dr.spf_configured ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-yellow-500/10 border border-yellow-500/20'}`}>
            <p className="text-sm text-zinc-400">SPF Record</p>
            <p className={`font-semibold ${dr.spf_configured ? 'text-emerald-400' : 'text-yellow-400'}`}>
              {dr.spf_configured ? (language === 'es' ? 'Configurado' : 'Configured') : (language === 'es' ? 'No Encontrado' : 'Not Found')}
            </p>
          </div>
          <div className={`p-4 rounded-lg ${dr.dmarc_configured ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-yellow-500/10 border border-yellow-500/20'}`}>
            <p className="text-sm text-zinc-400">DMARC Policy</p>
            <p className={`font-semibold ${dr.dmarc_configured ? 'text-emerald-400' : 'text-yellow-400'}`}>
              {dr.dmarc_configured ? (language === 'es' ? 'Configurado' : 'Configured') : (language === 'es' ? 'No Encontrado' : 'Not Found')}
            </p>
          </div>
          <div className={`p-4 rounded-lg ${dr.vulnerabilities.length === 0 ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
            <p className="text-sm text-zinc-400">{language === 'es' ? 'Vulnerabilidades' : 'Vulnerabilities'}</p>
            <p className={`font-semibold ${dr.vulnerabilities.length === 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {dr.vulnerabilities.length} {language === 'es' ? 'Encontradas' : 'Found'}
            </p>
          </div>
        </div>
        {dr.vulnerabilities.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-semibold text-red-400">{language === 'es' ? 'Problemas:' : 'Issues:'}</h3>
            {dr.vulnerabilities.map((v, i) => (
              <p key={i} className="text-zinc-400 text-sm">• {v}</p>
            ))}
          </div>
        )}
      </div>
    );
  }

  // IP results
  if (result.ip_result) {
    const ir = result.ip_result;
    return (
      <div className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-8">
        <h2 className="text-xl font-bold mb-6">
          {language === 'es' ? 'Información de IP' : 'IP Information'}
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-zinc-800 p-4 rounded-lg">
            <p className="text-sm text-zinc-400">{language === 'es' ? 'Ubicación' : 'Location'}</p>
            <p className="font-semibold">{ir.location || 'Unknown'}</p>
          </div>
          <div className="bg-zinc-800 p-4 rounded-lg">
            <p className="text-sm text-zinc-400">ISP</p>
            <p className="font-semibold">{ir.isp || 'Unknown'}</p>
          </div>
          <div className={`p-4 rounded-lg ${ir.is_vpn ? 'bg-blue-500/10 border border-blue-500/20' : 'bg-zinc-800'}`}>
            <p className="text-sm text-zinc-400">VPN/Proxy</p>
            <p className={`font-semibold ${ir.is_vpn ? 'text-blue-400' : ''}`}>
              {ir.is_vpn ? (language === 'es' ? 'Detectado' : 'Detected') : (language === 'es' ? 'No Detectado' : 'Not Detected')}
            </p>
          </div>
          <div className={`p-4 rounded-lg ${ir.blacklisted ? 'bg-red-500/10 border border-red-500/20' : 'bg-emerald-500/10 border border-emerald-500/20'}`}>
            <p className="text-sm text-zinc-400">{language === 'es' ? 'Lista Negra' : 'Blacklist Status'}</p>
            <p className={`font-semibold ${ir.blacklisted ? 'text-red-400' : 'text-emerald-400'}`}>
              {ir.blacklisted ? (language === 'es' ? 'En Lista Negra' : 'Blacklisted') : (language === 'es' ? 'Limpio' : 'Clean')}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Wallet results
  if (result.wallet_result) {
    const wr = result.wallet_result;
    return (
      <div className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-8">
        <h2 className="text-xl font-bold mb-6">
          {language === 'es' ? 'Información del Wallet' : 'Wallet Information'}
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-zinc-800 p-4 rounded-lg">
            <p className="text-sm text-zinc-400">Chain</p>
            <p className="font-semibold">{wr.chain}</p>
          </div>
          {wr.balance && (
            <div className="bg-zinc-800 p-4 rounded-lg">
              <p className="text-sm text-zinc-400">Balance</p>
              <p className="font-semibold">{wr.balance}</p>
            </div>
          )}
          <div className={`p-4 rounded-lg ${wr.labeled ? 'bg-yellow-500/10 border border-yellow-500/20' : 'bg-emerald-500/10 border border-emerald-500/20'}`}>
            <p className="text-sm text-zinc-400">{language === 'es' ? 'Etiquetado' : 'Labeled'}</p>
            <p className={`font-semibold ${wr.labeled ? 'text-yellow-400' : 'text-emerald-400'}`}>
              {wr.labeled ? (wr.label || (language === 'es' ? 'Sí' : 'Yes')) : (language === 'es' ? 'No' : 'No')}
            </p>
          </div>
          <div className={`p-4 rounded-lg ${wr.sanctions_check ? 'bg-red-500/10 border border-red-500/20' : 'bg-emerald-500/10 border border-emerald-500/20'}`}>
            <p className="text-sm text-zinc-400">{language === 'es' ? 'Sanciones' : 'Sanctions'}</p>
            <p className={`font-semibold ${wr.sanctions_check ? 'text-red-400' : 'text-emerald-400'}`}>
              {wr.sanctions_check ? (language === 'es' ? 'Detectado' : 'Flagged') : (language === 'es' ? 'Limpio' : 'Clean')}
            </p>
          </div>
          <div className="bg-zinc-800 p-4 rounded-lg">
            <p className="text-sm text-zinc-400">{language === 'es' ? 'Direcciones Vinculadas' : 'Linked Addresses'}</p>
            <p className="font-semibold">{wr.linked_addresses.length}</p>
          </div>
        </div>
      </div>
    );
  }

  // Name results
  if (result.name_result) {
    const nr = result.name_result;
    return (
      <div className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-8">
        <h2 className="text-xl font-bold mb-6">
          {language === 'es' ? 'Información Pública' : 'Public Information'}
        </h2>
        {nr.possible_profiles.length > 0 ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {nr.possible_profiles.map((profile, i) => (
              <a
                key={i}
                href={profile.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-zinc-800 rounded-lg p-4 hover:bg-zinc-700 transition"
              >
                <p className="font-semibold">{profile.platform}</p>
                <p className="text-xs text-zinc-500 truncate">{profile.url}</p>
                <p className="text-xs text-yellow-400 mt-1">{profile.confidence}</p>
              </a>
            ))}
          </div>
        ) : (
          <p className="text-zinc-400">
            {language === 'es' ? 'No se encontraron perfiles públicos.' : 'No public profiles found.'}
          </p>
        )}
      </div>
    );
  }

  return null;
}
