'use client';

import { SecurityScore, getRiskColor, getRiskLabel } from '@/lib/api';

interface SecurityScoreProps {
  score: SecurityScore;
  email?: string;
}

export default function SecurityScoreDisplay({ score, email }: SecurityScoreProps) {
  const circumference = 2 * Math.PI * 90;
  const offset = circumference - (score.score / 100) * circumference;
  const color = getRiskColor(score.risk_level);

  return (
    <div className="flex flex-col items-center space-y-6">
      {/* Score Circle */}
      <div className="relative w-64 h-64 score-ring">
        <svg className="w-full h-full transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="128"
            cy="128"
            r="90"
            stroke="#1f2937"
            strokeWidth="12"
            fill="none"
          />
          {/* Score circle */}
          <circle
            cx="128"
            cy="128"
            r="90"
            stroke={color}
            strokeWidth="12"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-5xl font-bold" style={{ color }}>
            {score.score}
          </span>
          <span className="text-gray-400 text-sm">/100</span>
        </div>
      </div>

      {/* Risk Level Badge */}
      <div
        className="px-6 py-2 rounded-full text-white font-semibold text-lg"
        style={{ backgroundColor: color }}
      >
        {getRiskLabel(score.risk_level)}
      </div>

      {email && (
        <p className="text-gray-400 text-sm">
          Auditoría de: <span className="text-white">{email}</span>
        </p>
      )}

      {/* Issues Summary */}
      <div className="grid grid-cols-4 gap-4 w-full max-w-md mt-4">
        <IssueBox count={score.issues_critical} label="Críticos" color="#ef4444" />
        <IssueBox count={score.issues_high} label="Altos" color="#f97316" />
        <IssueBox count={score.issues_medium} label="Medios" color="#eab308" />
        <IssueBox count={score.issues_low} label="Bajos" color="#22c55e" />
      </div>

      {/* Score Breakdown */}
      <div className="w-full max-w-md space-y-3 mt-6">
        <h3 className="text-lg font-semibold text-gray-300">Desglose del Score</h3>
        <BreakdownBar
          label="Breaches"
          value={score.breakdown.breaches}
          max={35}
        />
        <BreakdownBar
          label="Contraseñas"
          value={score.breakdown.passwords}
          max={30}
        />
        <BreakdownBar
          label="OSINT"
          value={score.breakdown.osint}
          max={20}
        />
        <BreakdownBar
          label="Configuración"
          value={score.breakdown.configuration}
          max={15}
        />
      </div>
    </div>
  );
}

function IssueBox({ count, label, color }: { count: number; label: string; color: string }) {
  return (
    <div className="bg-gray-800/50 rounded-lg p-3 text-center border border-gray-700">
      <div className="text-2xl font-bold" style={{ color }}>
        {count}
      </div>
      <div className="text-xs text-gray-400">{label}</div>
    </div>
  );
}

function BreakdownBar({ label, value, max }: { label: string; value: number; max: number }) {
  const percentage = (value / max) * 100;
  const color = percentage >= 80 ? '#22c55e' : percentage >= 50 ? '#eab308' : '#ef4444';

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-gray-400">{label}</span>
        <span className="text-white">{value}/{max}</span>
      </div>
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
