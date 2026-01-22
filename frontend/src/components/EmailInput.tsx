'use client';

import { useState } from 'react';

interface EmailInputProps {
  onSubmit: (email: string) => void;
  loading?: boolean;
  placeholder?: string;
  buttonText?: string;
}

export default function EmailInput({
  onSubmit,
  loading = false,
  placeholder = "tu@email.com",
  buttonText = "Analizar"
}: EmailInputProps) {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Ingresá un email válido');
      return;
    }

    onSubmit(email);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-lg">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder={placeholder}
            disabled={loading}
            className="w-full px-5 py-4 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all text-lg"
          />
          {error && (
            <p className="text-red-400 text-sm mt-2">{error}</p>
          )}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all glow-blue hover:glow-blue flex items-center justify-center gap-2 text-lg"
        >
          {loading ? (
            <>
              <svg className="w-5 h-5 spinner" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>Analizando...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <span>{buttonText}</span>
            </>
          )}
        </button>
      </div>
      <p className="text-gray-500 text-sm mt-3 text-center">
        🔒 Tu email nunca se guarda ni se comparte. Solo lo usamos para la auditoría.
      </p>
    </form>
  );
}
