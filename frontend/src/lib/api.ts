/**
 * FK94 Security Platform - API Client
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export type AuditType = 'email' | 'username' | 'phone' | 'domain' | 'name' | 'ip' | 'wallet';

export interface SecurityScore {
  score: number;
  risk_level: 'critical' | 'high' | 'medium' | 'low' | 'safe';
  breakdown: Record<string, number>;
  issues_critical: number;
  issues_high: number;
  issues_medium: number;
  issues_low: number;
}

export interface BreachInfo {
  name: string;
  date?: string;
  data_types: string[];
  description?: string;
}

export interface BreachCheckResult {
  email: string;
  breached: boolean;
  breach_count: number;
  breaches: BreachInfo[];
  risk_level: string;
}

export interface UsernameResult {
  username: string;
  platforms_found: string[];
  platforms_checked: number;
  profile_urls: string[];
  risk_level: string;
}

export interface PhoneResult {
  phone: string;
  carrier?: string;
  line_type?: string;
  location?: string;
  breaches_found: number;
  spam_reports: number;
  risk_level: string;
  // Truecaller data
  owner_name?: string;
  tags: string[];
  email?: string;
  error?: string;
}

export interface DomainResult {
  domain: string;
  ssl_valid: boolean;
  ssl_expiry?: string;
  dns_records: Record<string, string[]>;
  spf_configured: boolean;
  dmarc_configured: boolean;
  dkim_configured: boolean;
  open_ports: number[];
  vulnerabilities: string[];
  risk_level: string;
}

export interface NameResult {
  full_name: string;
  possible_profiles: Array<{
    platform: string;
    url: string;
    confidence: string;
  }>;
  public_records: string[];
  news_mentions: string[];
  risk_level: string;
}

export interface IPResult {
  ip_address: string;
  location?: string;
  isp?: string;
  is_vpn: boolean;
  is_proxy: boolean;
  is_tor: boolean;
  blacklisted: boolean;
  blacklist_sources: string[];
  abuse_reports: number;
  risk_level: string;
}

export interface ExchangeInteraction {
  exchange: string;
  address: string;
  direction: string;
  tx_hash: string;
  value?: string;
  timestamp?: string;
}

export interface WalletResult {
  address: string;
  chain: string;
  balance?: string;
  transaction_count?: number;
  linked_addresses: string[];
  labeled: boolean;
  label?: string;
  sanctions_check: boolean;
  risk_level: string;
  // Deep scan fields
  deep_scan: boolean;
  exchange_interactions: ExchangeInteraction[];
  exchanges_detected: string[];
  is_traceable: boolean;
  traceability_score: number;
  traceability_details: string[];
  mixer_interactions: string[];
  used_mixer: boolean;
  ofac_sanctioned: boolean;
  first_tx_date?: string;
  last_tx_date?: string;
  unique_counterparties: number;
  scan_warnings: string[];
}

export interface PasswordExposure {
  found: boolean;
  count: number;
  sources: string[];
}

export interface AuditResult {
  id: string;
  audit_type: AuditType;
  query_value: string;
  email?: string;
  timestamp: string;
  security_score: SecurityScore;
  breach_check?: BreachCheckResult;
  password_exposure?: PasswordExposure;
  username_result?: UsernameResult;
  phone_result?: PhoneResult;
  domain_result?: DomainResult;
  name_result?: NameResult;
  ip_result?: IPResult;
  wallet_result?: WalletResult;
  ai_analysis?: string;
  recommendations: string[];
}

export interface AIResponse {
  response: string;
  recommendations: string[];
}

// === Retry Helper ===

async function fetchWithRetry(
  url: string,
  options: RequestInit,
  retries = 2,
  delayMs = 1000
): Promise<Response> {
  for (let attempt = 0; attempt <= retries; attempt++) {
    const response = await fetch(url, options);
    if (response.ok || response.status < 500 || attempt === retries) {
      return response;
    }
    await new Promise((r) => setTimeout(r, delayMs * (attempt + 1)));
  }
  // Unreachable, but TypeScript needs it
  return fetch(url, options);
}

// === API Functions ===

export async function checkEmail(email: string): Promise<BreachCheckResult> {
  const response = await fetchWithRetry(`${API_BASE}/check/email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });

  if (!response.ok) {
    throw new Error('Failed to check email');
  }

  return response.json();
}

export async function checkUsername(username: string): Promise<UsernameResult> {
  const response = await fetchWithRetry(`${API_BASE}/check/username`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  });

  if (!response.ok) {
    throw new Error('Failed to check username');
  }

  return response.json();
}

export async function checkPhone(phone: string, countryCode: string = 'AR'): Promise<PhoneResult> {
  const response = await fetchWithRetry(`${API_BASE}/check/phone`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, country_code: countryCode }),
  });

  if (!response.ok) {
    throw new Error('Failed to check phone');
  }

  return response.json();
}

export async function checkDomain(domain: string): Promise<DomainResult> {
  const response = await fetchWithRetry(`${API_BASE}/check/domain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ domain }),
  });

  if (!response.ok) {
    throw new Error('Failed to check domain');
  }

  return response.json();
}

export async function checkName(fullName: string, location?: string): Promise<NameResult> {
  const response = await fetchWithRetry(`${API_BASE}/check/name`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ full_name: fullName, location }),
  });

  if (!response.ok) {
    throw new Error('Failed to check name');
  }

  return response.json();
}

export async function checkIP(ipAddress: string): Promise<IPResult> {
  const response = await fetchWithRetry(`${API_BASE}/check/ip`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ip_address: ipAddress }),
  });

  if (!response.ok) {
    throw new Error('Failed to check IP');
  }

  return response.json();
}

export async function getSecurityScore(email: string): Promise<SecurityScore> {
  const response = await fetchWithRetry(`${API_BASE}/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });

  if (!response.ok) {
    throw new Error('Failed to get security score');
  }

  return response.json();
}

export async function runFullAudit(email: string, password?: string): Promise<AuditResult> {
  const response = await fetchWithRetry(`${API_BASE}/audit/full`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password: password || null,
      check_breaches: true,
      check_osint: true,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to run audit');
  }

  return response.json();
}

export async function runMultiAudit(
  auditType: AuditType,
  value: string,
  extraData?: Record<string, string>
): Promise<AuditResult> {
  const response = await fetchWithRetry(`${API_BASE}/audit/multi`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      audit_type: auditType,
      value,
      extra_data: extraData,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to run audit');
  }

  return response.json();
}

export async function askAI(query: string, context?: object): Promise<AIResponse> {
  const response = await fetchWithRetry(`${API_BASE}/ai/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, context }),
  });

  if (!response.ok) {
    throw new Error('Failed to get AI response');
  }

  return response.json();
}

export async function downloadReport(email: string): Promise<Blob> {
  const response = await fetchWithRetry(`${API_BASE}/report/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      check_breaches: true,
      check_osint: true,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate report');
  }

  return response.blob();
}

export function getRiskLevel(score: SecurityScore): string {
  if (score.score <= 20) return 'critical';
  if (score.score <= 40) return 'high';
  if (score.score <= 60) return 'medium';
  if (score.score <= 80) return 'low';
  return 'safe';
}

export function getRiskColor(level: string): string {
  const colors: Record<string, string> = {
    critical: '#ef4444',
    high: '#f97316',
    medium: '#eab308',
    low: '#22c55e',
    safe: '#10b981',
  };
  return colors[level] || '#6b7280';
}

export function getRiskLabel(level: string): string {
  const labels: Record<string, string> = {
    critical: 'CRITICAL',
    high: 'HIGH',
    medium: 'MEDIUM',
    low: 'LOW',
    safe: 'SAFE',
  };
  return labels[level] || level.toUpperCase();
}

export const AUDIT_TYPE_CONFIG: Record<AuditType, {
  label: string;
  placeholder: string;
  icon: string;
  description: string;
}> = {
  email: {
    label: 'Email',
    placeholder: 'you@example.com',
    icon: '📧',
    description: 'Check for data breaches and leaked passwords',
  },
  username: {
    label: 'Username',
    placeholder: 'johndoe',
    icon: '👤',
    description: 'Find accounts across 20+ platforms',
  },
  phone: {
    label: 'Phone',
    placeholder: '+1234567890',
    icon: '📱',
    description: 'Check carrier info and breach exposure',
  },
  domain: {
    label: 'Domain',
    placeholder: 'example.com',
    icon: '🌐',
    description: 'Check SSL, DNS, SPF, DMARC configuration',
  },
  name: {
    label: 'Name',
    placeholder: 'John Doe',
    icon: '🔍',
    description: 'Search for public information',
  },
  ip: {
    label: 'IP Address',
    placeholder: '8.8.8.8',
    icon: '📍',
    description: 'Check reputation and blacklist status',
  },
  wallet: {
    label: 'Wallet',
    placeholder: '0x...',
    icon: '💰',
    description: 'Check if your wallet is linked to your identity',
  },
};
