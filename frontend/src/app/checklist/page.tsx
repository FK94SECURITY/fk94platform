'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { useLanguage } from '@/i18n';
import {
  checklistData,
  getAllItems,
  Priority,
  PRIORITY_CONFIG,
  STATS,
  ChecklistItem,
  ChecklistCategory,
  getLocalizedText,
  Language,
} from '@/data/checklist-data';

const STORAGE_KEY = 'fk94-checklist-progress';
const INTRO_SEEN_KEY = 'fk94-intro-seen';

// FK94 Protocol Steps
const getProtocolSteps = (lang: Language) => [
  {
    number: '01',
    title: lang === 'es' ? 'IDENTIFICAR' : 'IDENTIFY',
    subtitle: lang === 'es' ? 'Conocé tus vulnerabilidades' : 'Know your vulnerabilities',
    description: lang === 'es'
      ? 'El primer paso es entender qué información tuya está expuesta. Email, username, teléfono - todo deja rastros.'
      : 'The first step is understanding what information is exposed. Email, username, phone - everything leaves traces.',
    icon: '🔍',
    color: 'red',
  },
  {
    number: '02',
    title: lang === 'es' ? 'PROTEGER' : 'PROTECT',
    subtitle: lang === 'es' ? 'Implementá las defensas' : 'Implement defenses',
    description: lang === 'es'
      ? 'Usá 2FA, passwords únicos, encriptá tus datos. Cada capa de protección reduce el riesgo exponencialmente.'
      : 'Use 2FA, unique passwords, encrypt your data. Each layer of protection reduces risk exponentially.',
    icon: '🛡️',
    color: 'yellow',
  },
  {
    number: '03',
    title: lang === 'es' ? 'VERIFICAR' : 'VERIFY',
    subtitle: lang === 'es' ? 'Confirmá que funciona' : 'Confirm it works',
    description: lang === 'es'
      ? 'Ejecutá escaneos de seguridad, verificá tus configuraciones. La seguridad sin verificación es solo esperanza.'
      : 'Run security scans, verify your settings. Security without verification is just hope.',
    icon: '✓',
    color: 'blue',
  },
  {
    number: '04',
    title: lang === 'es' ? 'MANTENER' : 'MAINTAIN',
    subtitle: lang === 'es' ? 'Monitoreo continuo' : 'Continuous monitoring',
    description: lang === 'es'
      ? 'La seguridad no es un evento, es un proceso. Revisá periódicamente y actualizá tus defensas.'
      : 'Security is not an event, it\'s a process. Review periodically and update your defenses.',
    icon: '🔄',
    color: 'emerald',
  },
];

export default function ChecklistPage() {
  const { t, language } = useLanguage();
  const lang = language as Language;
  const [completedItems, setCompletedItems] = useState<Set<string>>(() => {
    if (typeof window === 'undefined') return new Set();
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) return new Set(JSON.parse(saved));
    } catch {
      // Invalid data, start fresh
    }
    return new Set();
  });
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<Priority | 'all'>('all');
  const [isLoaded] = useState(() => typeof window !== 'undefined');
  const [showIntro, setShowIntro] = useState(() => {
    if (typeof window === 'undefined') return false;
    return !localStorage.getItem(INTRO_SEEN_KEY);
  });
  const [introStep, setIntroStep] = useState(0);

  const protocolSteps = getProtocolSteps(lang);

  // Save to localStorage when items change
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...completedItems]));
    }
  }, [completedItems, isLoaded]);

  const handleIntroComplete = () => {
    localStorage.setItem(INTRO_SEEN_KEY, 'true');
    setShowIntro(false);
  };

  const handleNextStep = () => {
    if (introStep < protocolSteps.length - 1) {
      setIntroStep(introStep + 1);
    } else {
      handleIntroComplete();
    }
  };

  const toggleItem = (itemId: string) => {
    setCompletedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  const allItems = getAllItems();
  const completedCount = completedItems.size;
  const totalCount = allItems.length;
  const progressPercent = Math.round((completedCount / totalCount) * 100);

  const getScoreLevel = (percent: number) => {
    if (lang === 'es') {
      if (percent >= 80) return { label: 'Excelente', color: 'text-emerald-400' };
      if (percent >= 60) return { label: 'Bueno', color: 'text-green-400' };
      if (percent >= 40) return { label: 'Regular', color: 'text-yellow-400' };
      if (percent >= 20) return { label: 'Mejorable', color: 'text-orange-400' };
      return { label: 'En Riesgo', color: 'text-red-400' };
    }
    if (percent >= 80) return { label: 'Excellent', color: 'text-emerald-400' };
    if (percent >= 60) return { label: 'Good', color: 'text-green-400' };
    if (percent >= 40) return { label: 'Fair', color: 'text-yellow-400' };
    if (percent >= 20) return { label: 'Needs Work', color: 'text-orange-400' };
    return { label: 'At Risk', color: 'text-red-400' };
  };

  const scoreLevel = getScoreLevel(progressPercent);

  const getCategoryProgress = (category: ChecklistCategory) => {
    const categoryCompleted = category.items.filter(item => completedItems.has(item.id)).length;
    return { completed: categoryCompleted, total: category.items.length };
  };

  const resetProgress = () => {
    const msg = lang === 'es'
      ? '¿Estás seguro de que querés reiniciar todo el progreso?'
      : 'Are you sure you want to reset all progress?';
    if (confirm(msg)) {
      setCompletedItems(new Set());
    }
  };

  const showIntroAgain = () => {
    setIntroStep(0);
    setShowIntro(true);
  };

  if (!isLoaded) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen pt-20 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        </main>
      </>
    );
  }

  // Show intro if not seen before
  if (showIntro) {
    const step = protocolSteps[introStep];
    const colorClasses: Record<string, { bg: string; border: string; text: string }> = {
      red: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400' },
      yellow: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400' },
      blue: { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400' },
      emerald: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400' },
    };
    const colors = colorClasses[step.color];

    return (
      <>
        <Navbar />
        <main className="min-h-screen pt-20 flex items-center justify-center">
          <div className="max-w-2xl mx-auto px-4 py-12">
            {/* Header */}
            {introStep === 0 && (
              <div className="text-center mb-12 animate-fade-in">
                <div className="inline-block px-4 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-emerald-400 text-sm font-medium mb-6">
                  {lang === 'es' ? 'PROTOCOLO FK94' : 'FK94 PROTOCOL'}
                </div>
                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                  {lang === 'es' ? 'Seguridad' : 'Security'}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
                    {' '}{lang === 'es' ? 'Simplificada' : 'Made Simple'}
                  </span>
                </h1>
                <p className="text-zinc-400 text-lg">
                  {lang === 'es'
                    ? '4 pasos para proteger tu identidad digital'
                    : '4 steps to protect your digital identity'}
                </p>
              </div>
            )}

            {/* Progress Dots */}
            <div className="flex justify-center gap-2 mb-8">
              {protocolSteps.map((_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full transition-all duration-300 ${
                    i === introStep
                      ? 'w-8 bg-emerald-500'
                      : i < introStep
                        ? 'bg-emerald-500/50'
                        : 'bg-zinc-700'
                  }`}
                />
              ))}
            </div>

            {/* Step Card */}
            <div className={`${colors.bg} border ${colors.border} rounded-2xl p-8 mb-8 transition-all duration-500`}>
              <div className="flex items-start gap-6">
                <div className={`text-5xl ${colors.text} flex-shrink-0`}>
                  {step.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`text-sm font-mono ${colors.text}`}>{step.number}</span>
                    <h2 className="text-2xl font-bold">{step.title}</h2>
                  </div>
                  <p className={`${colors.text} font-medium mb-3`}>{step.subtitle}</p>
                  <p className="text-zinc-400">{step.description}</p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-between items-center">
              <button
                onClick={handleIntroComplete}
                className="text-zinc-500 hover:text-zinc-300 text-sm transition"
              >
                {lang === 'es' ? 'Saltar intro' : 'Skip intro'}
              </button>
              <button
                onClick={handleNextStep}
                className="bg-emerald-600 hover:bg-emerald-500 px-6 py-3 rounded-xl font-medium transition flex items-center gap-2"
              >
                {introStep < protocolSteps.length - 1
                  ? (lang === 'es' ? 'Siguiente' : 'Next')
                  : (lang === 'es' ? 'Comenzar Checklist' : 'Start Checklist')}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Navbar />

      <main className="min-h-screen pt-20">
        {/* Hero with Protocol Summary */}
        <section className="py-12 bg-gradient-to-b from-emerald-500/10 to-transparent">
          <div className="max-w-6xl mx-auto px-4">
            {/* Protocol Mini Banner */}
            <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
              {protocolSteps.map((step, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    i === 0 ? 'bg-red-500/20 text-red-400' :
                    i === 1 ? 'bg-yellow-500/20 text-yellow-400' :
                    i === 2 ? 'bg-blue-500/20 text-blue-400' :
                    'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {i + 1}
                  </span>
                  <span className="text-zinc-400">{step.title}</span>
                  {i < protocolSteps.length - 1 && (
                    <svg className="w-4 h-4 text-zinc-600 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  )}
                </div>
              ))}
              <button
                onClick={showIntroAgain}
                className="text-emerald-400 text-xs hover:underline ml-2"
              >
                {lang === 'es' ? 'Ver intro' : 'View intro'}
              </button>
            </div>

            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div>
                <h1 className="text-4xl font-bold mb-2">{t.checklist.title}</h1>
                <p className="text-zinc-400">
                  {STATS.totalItems} {lang === 'es' ? 'prácticas de seguridad en' : 'security practices across'} {STATS.totalCategories} {lang === 'es' ? 'categorías' : 'categories'}
                </p>
              </div>

              {/* Progress Circle */}
              <div className="flex items-center gap-6">
                <div className="relative w-24 h-24">
                  <svg className="w-24 h-24 transform -rotate-90">
                    <circle
                      cx="48"
                      cy="48"
                      r="40"
                      stroke="currentColor"
                      strokeWidth="8"
                      fill="none"
                      className="text-zinc-800"
                    />
                    <circle
                      cx="48"
                      cy="48"
                      r="40"
                      stroke="currentColor"
                      strokeWidth="8"
                      fill="none"
                      strokeDasharray={`${progressPercent * 2.51} 251`}
                      className="text-emerald-500 transition-all duration-500"
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold">{progressPercent}%</span>
                  </div>
                </div>
                <div>
                  <p className={`text-lg font-semibold ${scoreLevel.color}`}>{scoreLevel.label}</p>
                  <p className="text-zinc-500 text-sm">{completedCount}/{totalCount} {t.checklist.completed.toLowerCase()}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Filters */}
        <section className="py-6 border-b border-zinc-800 sticky top-16 bg-zinc-950/95 backdrop-blur z-40">
          <div className="max-w-6xl mx-auto px-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              {/* Priority Filter */}
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setPriorityFilter('all')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                    priorityFilter === 'all'
                      ? 'bg-zinc-700 text-white'
                      : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800'
                  }`}
                >
                  {t.checklist.filters.all} ({STATS.totalItems})
                </button>
                <button
                  onClick={() => setPriorityFilter('essential')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                    priorityFilter === 'essential'
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                      : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800'
                  }`}
                >
                  {t.checklist.filters.essential} ({STATS.essentialItems})
                </button>
                <button
                  onClick={() => setPriorityFilter('recommended')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                    priorityFilter === 'recommended'
                      ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                      : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800'
                  }`}
                >
                  {t.checklist.filters.recommended} ({STATS.recommendedItems})
                </button>
                <button
                  onClick={() => setPriorityFilter('advanced')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                    priorityFilter === 'advanced'
                      ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      : 'bg-zinc-800/50 text-zinc-400 hover:bg-zinc-800'
                  }`}
                >
                  {t.checklist.filters.advanced} ({STATS.advancedItems})
                </button>
              </div>

              {/* Reset Button */}
              <button
                onClick={resetProgress}
                className="text-zinc-500 hover:text-zinc-300 text-sm transition"
              >
                {lang === 'es' ? 'Reiniciar Progreso' : 'Reset Progress'}
              </button>
            </div>
          </div>
        </section>

        {/* Category Navigation */}
        <section className="py-6">
          <div className="max-w-6xl mx-auto px-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
              {checklistData.map((category) => {
                const progress = getCategoryProgress(category);
                const isComplete = progress.completed === progress.total;
                return (
                  <button
                    key={category.id}
                    onClick={() => setActiveCategory(activeCategory === category.id ? null : category.id)}
                    className={`p-4 rounded-xl border transition text-center ${
                      activeCategory === category.id
                        ? 'bg-emerald-500/10 border-emerald-500/50'
                        : isComplete
                        ? 'bg-emerald-500/5 border-emerald-500/20'
                        : 'bg-zinc-900/50 border-zinc-800 hover:border-zinc-700'
                    }`}
                  >
                    <div className="text-2xl mb-1">{category.icon}</div>
                    <div className="text-xs font-medium truncate">{getLocalizedText(category.name, lang)}</div>
                    <div className={`text-xs mt-1 ${isComplete ? 'text-emerald-400' : 'text-zinc-500'}`}>
                      {progress.completed}/{progress.total}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        {/* Checklist Items */}
        <section className="py-6 pb-20">
          <div className="max-w-6xl mx-auto px-4">
            <div className="space-y-8">
              {checklistData
                .filter(category => !activeCategory || category.id === activeCategory)
                .map((category) => {
                  const categoryItems = priorityFilter === 'all'
                    ? category.items
                    : category.items.filter(item => item.priority === priorityFilter);

                  if (categoryItems.length === 0) return null;

                  const progress = getCategoryProgress(category);

                  return (
                    <div key={category.id} className="bg-zinc-900/30 rounded-2xl border border-zinc-800 overflow-hidden">
                      {/* Category Header */}
                      <div className="p-6 border-b border-zinc-800 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <span className="text-3xl">{category.icon}</span>
                          <div>
                            <h2 className="text-xl font-semibold">{getLocalizedText(category.name, lang)}</h2>
                            <p className="text-zinc-500 text-sm">{getLocalizedText(category.description, lang)}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-semibold">
                            {progress.completed}/{progress.total}
                          </div>
                          <div className="w-24 h-2 bg-zinc-800 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-emerald-500 transition-all duration-300"
                              style={{ width: `${(progress.completed / progress.total) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Items */}
                      <div className="divide-y divide-zinc-800/50">
                        {categoryItems.map((item) => (
                          <ChecklistItemRow
                            key={item.id}
                            item={item}
                            isCompleted={completedItems.has(item.id)}
                            onToggle={() => toggleItem(item.id)}
                            language={lang}
                          />
                        ))}
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-16 bg-gradient-to-r from-emerald-900/30 to-cyan-900/30">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold mb-4">{t.checklist.cta.title}</h2>
            <p className="text-zinc-400 mb-8">
              {t.checklist.cta.description}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/audit"
                className="bg-emerald-600 hover:bg-emerald-500 px-8 py-3 rounded-xl font-medium transition"
              >
                {t.checklist.cta.button}
              </Link>
              <Link
                href="/pricing"
                className="border border-zinc-700 hover:border-zinc-500 px-8 py-3 rounded-xl font-medium transition"
              >
                {t.nav.pricing}
              </Link>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}

function ChecklistItemRow({
  item,
  isCompleted,
  onToggle,
  language,
}: {
  item: ChecklistItem;
  isCompleted: boolean;
  onToggle: () => void;
  language: Language;
}) {
  const priorityConfig = PRIORITY_CONFIG[item.priority];
  const priorityLabel = getLocalizedText(priorityConfig.label, language);

  return (
    <div
      className={`p-4 flex items-start gap-4 transition cursor-pointer hover:bg-zinc-800/30 ${
        isCompleted ? 'opacity-60' : ''
      }`}
      onClick={onToggle}
    >
      {/* Checkbox */}
      <div
        className={`w-6 h-6 rounded-md border-2 flex-shrink-0 flex items-center justify-center transition ${
          isCompleted
            ? 'bg-emerald-500 border-emerald-500'
            : 'border-zinc-600 hover:border-zinc-500'
        }`}
      >
        {isCompleted && (
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className={`font-medium ${isCompleted ? 'line-through text-zinc-500' : ''}`}>
            {getLocalizedText(item.title, language)}
          </h3>
          <span className={`text-xs px-2 py-0.5 rounded-full ${priorityConfig.bgColor} ${priorityConfig.color}`}>
            {priorityLabel}
          </span>
        </div>
        <p className="text-zinc-500 text-sm mt-1">{getLocalizedText(item.description, language)}</p>

        {/* Tip (mini explicación propia) */}
        {item.tip && (
          <div
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-2 text-emerald-400 text-sm mt-2 bg-emerald-500/10 px-3 py-1.5 rounded-lg"
          >
            <span className="text-emerald-500">💡</span>
            <span>{getLocalizedText(item.tip, language)}</span>
          </div>
        )}
      </div>
    </div>
  );
}
