'use client';

import { useState } from 'react';
import { askAI, AuditResult } from '@/lib/api';
import { useLanguage } from '@/i18n';

interface AIChatProps {
  auditContext?: AuditResult;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const GREETINGS = {
  es: '¡Hola! Soy el asistente de seguridad de FK94. Puedo ayudarte a entender los resultados de tu auditoría o responder cualquier pregunta sobre ciberseguridad. ¿En qué te puedo ayudar?',
  en: 'Hi! I\'m the FK94 security assistant. I can help you understand your audit results or answer any cybersecurity questions. How can I help?',
};

const ERROR_MESSAGES = {
  es: 'Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.',
  en: 'Sorry, there was an error processing your message. Please try again.',
};

export default function AIChat({ auditContext }: AIChatProps) {
  const { language } = useLanguage();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: GREETINGS[language],
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const context = auditContext ? {
        email: auditContext.email,
        security_score: auditContext.security_score,
        breach_check: auditContext.breach_check,
      } : undefined;

      const response = await askAI(userMessage, context);
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: ERROR_MESSAGES[language],
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[500px] bg-gray-900 rounded-xl border border-gray-700">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <h3 className="font-semibold text-white">FK94 AI Security Analyst</h3>
          <p className="text-xs text-gray-400">Powered by DeepSeek</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] px-4 py-3 rounded-2xl ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-md'
                  : 'bg-gray-800 text-gray-100 rounded-bl-md'
              }`}
            >
              <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 px-4 py-3 rounded-2xl rounded-bl-md">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={language === 'es' ? 'Preguntame sobre seguridad...' : 'Ask me about security...'}
            className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-xl transition-all"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
