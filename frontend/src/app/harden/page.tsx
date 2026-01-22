'use client';

import { useState } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { useLanguage } from '@/i18n';
import {
  questions as questionsData,
  generateScript,
  getScriptFilename,
  getScriptInstructions,
  OS,
} from '@/data/hardening-config';

type Step = 'questions' | 'generating' | 'result';

// Translated questions
const getTranslatedQuestions = (language: 'en' | 'es') => {
  if (language === 'en') return questionsData;

  return [
    {
      id: 'os',
      question: '¿Qué sistema operativo usás?',
      options: [
        { value: 'macos', label: 'macOS' },
        { value: 'windows', label: 'Windows' },
        { value: 'linux', label: 'Linux' },
      ],
    },
    {
      id: 'risk_level',
      question: '¿Qué nivel de seguridad necesitás?',
      options: [
        { value: 'basic', label: 'Básico - Solo lo esencial' },
        { value: 'medium', label: 'Medio - Manejo datos sensibles' },
        { value: 'maximum', label: 'Máximo - Alto riesgo (crypto, periodista, activista)' },
      ],
    },
    {
      id: 'has_crypto',
      question: '¿Tenés criptomonedas?',
      options: [
        { value: 'yes', label: 'Sí' },
        { value: 'no', label: 'No' },
      ],
    },
    {
      id: 'uses_vpn',
      question: '¿Usás VPN actualmente?',
      options: [
        { value: 'yes', label: 'Sí, siempre' },
        { value: 'sometimes', label: 'A veces' },
        { value: 'no', label: 'No' },
      ],
    },
    {
      id: 'public_figure',
      question: '¿Sos figura pública o manejás información sensible?',
      options: [
        { value: 'yes', label: 'Sí' },
        { value: 'no', label: 'No' },
      ],
    },
    {
      id: 'work_type',
      question: '¿Qué describe mejor tu trabajo?',
      options: [
        { value: 'general', label: 'General / Oficina' },
        { value: 'tech', label: 'Tech / Desarrollador' },
        { value: 'finance', label: 'Finanzas / Trading' },
        { value: 'journalism', label: 'Periodismo / Activismo' },
      ],
    },
  ];
};

const getTranslatedInstructions = (os: OS, language: 'en' | 'es'): string[] => {
  if (language === 'en') return getScriptInstructions(os);

  if (os === 'windows') {
    return [
      'Abrir PowerShell como Administrador',
      'Navegar a la carpeta de descargas: cd Downloads',
      'Permitir ejecución de scripts: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass',
      'Ejecutar el script: .\\fk94-harden.ps1',
    ];
  }
  return [
    'Abrir Terminal',
    'Navegar a la carpeta de descargas: cd ~/Downloads',
    'Hacer ejecutable: chmod +x fk94-harden.sh',
    'Ejecutar el script: ./fk94-harden.sh',
  ];
};

export default function HardenPage() {
  const { t, language } = useLanguage();
  const [step, setStep] = useState<Step>('questions');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [generatedScript, setGeneratedScript] = useState('');

  const questions = getTranslatedQuestions(language);

  const handleAnswer = (questionId: string, value: string) => {
    const newAnswers = { ...answers, [questionId]: value };
    setAnswers(newAnswers);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Generate script
      setStep('generating');
      setTimeout(() => {
        const script = generateScript(newAnswers);
        setGeneratedScript(script);
        setStep('result');
      }, 1500);
    }
  };

  const handleBack = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleRestart = () => {
    setStep('questions');
    setCurrentQuestion(0);
    setAnswers({});
    setGeneratedScript('');
  };

  const handleDownload = () => {
    const os = answers.os as OS;
    const filename = getScriptFilename(os);
    const blob = new Blob([generatedScript], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedScript);
    alert(t.harden.result.copied);
  };

  const progress = ((currentQuestion + 1) / questions.length) * 100;

  const getOsLabel = () => {
    if (answers.os === 'macos') return 'macOS';
    if (answers.os === 'windows') return 'Windows';
    return 'Linux';
  };

  const getRiskLabel = () => {
    const riskMap: Record<string, { en: string; es: string }> = {
      basic: { en: 'Basic', es: 'Básico' },
      medium: { en: 'Medium', es: 'Medio' },
      maximum: { en: 'Maximum', es: 'Máximo' },
    };
    return riskMap[answers.risk_level]?.[language] || answers.risk_level;
  };

  return (
    <>
      <Navbar />

      <main className="min-h-screen pt-20">
        {/* Hero */}
        <section className="py-12 bg-gradient-to-b from-emerald-500/10 to-transparent">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h1 className="text-4xl font-bold mb-4">{t.harden.title}</h1>
            <p className="text-zinc-400">
              {t.harden.subtitle}
            </p>
          </div>
        </section>

        <section className="py-12">
          <div className="max-w-2xl mx-auto px-4">
            {/* Questions Step */}
            {step === 'questions' && (
              <div className="space-y-8">
                {/* Progress Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm text-zinc-500">
                    <span>{t.harden.question} {currentQuestion + 1} {t.harden.of} {questions.length}</span>
                    <span>{Math.round(progress)}%</span>
                  </div>
                  <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>

                {/* Question Card */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8">
                  <h2 className="text-2xl font-semibold mb-6">
                    {questions[currentQuestion].question}
                  </h2>

                  <div className="space-y-3">
                    {questions[currentQuestion].options.map((option) => (
                      <button
                        key={option.value}
                        onClick={() => handleAnswer(questions[currentQuestion].id, option.value)}
                        className={`w-full text-left p-4 rounded-xl border transition hover:border-emerald-500/50 hover:bg-emerald-500/5 ${
                          answers[questions[currentQuestion].id] === option.value
                            ? 'border-emerald-500 bg-emerald-500/10'
                            : 'border-zinc-700 bg-zinc-800/50'
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Navigation */}
                {currentQuestion > 0 && (
                  <button
                    onClick={handleBack}
                    className="flex items-center gap-2 text-zinc-400 hover:text-white transition"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    {t.harden.previous}
                  </button>
                )}
              </div>
            )}

            {/* Generating Step */}
            {step === 'generating' && (
              <div className="flex flex-col items-center justify-center py-20 space-y-6">
                <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                <div className="text-center">
                  <h2 className="text-2xl font-semibold mb-2">{t.harden.generating.title}</h2>
                  <p className="text-zinc-400">{t.harden.generating.description}</p>
                </div>
              </div>
            )}

            {/* Result Step */}
            {step === 'result' && (
              <div className="space-y-8">
                {/* Summary Card */}
                <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-6">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 bg-emerald-500 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold">{t.harden.result.ready}</h2>
                      <p className="text-zinc-400">
                        {getOsLabel()} • {getRiskLabel()} {language === 'es' ? 'Seguridad' : 'Security'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Download Section */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                  <h3 className="text-lg font-semibold mb-4">{t.harden.result.download}</h3>
                  <div className="flex flex-wrap gap-4">
                    <button
                      onClick={handleDownload}
                      className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 px-6 py-3 rounded-xl font-medium transition"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      {t.harden.result.download} {getScriptFilename(answers.os as OS)}
                    </button>
                    <button
                      onClick={handleCopy}
                      className="flex items-center gap-2 border border-zinc-700 hover:border-zinc-500 px-6 py-3 rounded-xl font-medium transition"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      {t.harden.result.copy}
                    </button>
                  </div>
                </div>

                {/* Instructions */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                  <h3 className="text-lg font-semibold mb-4">{t.harden.result.howToRun}</h3>
                  <ol className="space-y-3">
                    {getTranslatedInstructions(answers.os as OS, language).map((instruction, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <span className="flex-shrink-0 w-6 h-6 bg-zinc-800 rounded-full flex items-center justify-center text-sm font-medium">
                          {i + 1}
                        </span>
                        <span className="text-zinc-300">{instruction}</span>
                      </li>
                    ))}
                  </ol>
                </div>

                {/* Script Preview */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
                    <h3 className="font-medium">{t.harden.result.preview}</h3>
                    <span className="text-xs text-zinc-500">{getScriptFilename(answers.os as OS)}</span>
                  </div>
                  <pre className="p-4 overflow-x-auto text-sm text-zinc-400 max-h-96 overflow-y-auto">
                    <code>{generatedScript}</code>
                  </pre>
                </div>

                {/* Actions */}
                <div className="flex flex-wrap gap-4 justify-between">
                  <button
                    onClick={handleRestart}
                    className="flex items-center gap-2 text-zinc-400 hover:text-white transition"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {t.harden.result.newScript}
                  </button>
                  <Link
                    href="/checklist"
                    className="flex items-center gap-2 text-emerald-400 hover:text-emerald-300 transition"
                  >
                    {t.harden.result.viewChecklist}
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* CTA */}
        {step === 'result' && (
          <section className="py-16 bg-gradient-to-r from-emerald-900/30 to-cyan-900/30">
            <div className="max-w-4xl mx-auto px-4 text-center">
              <h2 className="text-3xl font-bold mb-4">{t.harden.cta.title}</h2>
              <p className="text-zinc-400 mb-8">
                {t.harden.cta.description}
              </p>
              <Link
                href="/audit"
                className="inline-block bg-emerald-600 hover:bg-emerald-500 px-8 py-3 rounded-xl font-medium transition"
              >
                {t.harden.cta.button}
              </Link>
            </div>
          </section>
        )}
      </main>

      <Footer />
    </>
  );
}
