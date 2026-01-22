/**
 * FK94 Security Platform - Database Service
 * Handles saving/loading audits from Supabase
 */

import { supabase, isSupabaseConfigured } from './supabase'

export interface AuditRecord {
  id?: string
  user_id: string
  audit_type: string
  query_value: string
  security_score: number
  risk_level: string
  result_data: object
  ai_analysis?: string
  recommendations: string[]
  created_at?: string
}

export interface UserProfile {
  id: string
  email: string
  full_name?: string
  plan: 'free' | 'pro' | 'enterprise'
  audits_remaining: number
  audits_total: number
}

/**
 * Get user profile
 */
export async function getProfile(userId: string): Promise<UserProfile | null> {
  if (!isSupabaseConfigured) return null

  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .single()

  if (error) {
    console.error('Error fetching profile:', error)
    return null
  }

  return data
}

/**
 * Save an audit to the database
 */
export async function saveAudit(audit: AuditRecord): Promise<{ id: string } | null> {
  if (!isSupabaseConfigured) return null

  const { data, error } = await supabase
    .from('audits')
    .insert({
      user_id: audit.user_id,
      audit_type: audit.audit_type,
      query_value: audit.query_value,
      security_score: audit.security_score,
      risk_level: audit.risk_level,
      result_data: audit.result_data,
      ai_analysis: audit.ai_analysis,
      recommendations: audit.recommendations,
    })
    .select('id')
    .single()

  if (error) {
    console.error('Error saving audit:', error)
    return null
  }

  return data
}

/**
 * Get user's audit history
 */
export async function getAuditHistory(userId: string, limit = 20): Promise<AuditRecord[]> {
  if (!isSupabaseConfigured) return []

  const { data, error } = await supabase
    .from('audits')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: false })
    .limit(limit)

  if (error) {
    console.error('Error fetching audits:', error)
    return []
  }

  return data || []
}

/**
 * Get a specific audit by ID
 */
export async function getAudit(auditId: string, userId: string): Promise<AuditRecord | null> {
  if (!isSupabaseConfigured) return null

  const { data, error } = await supabase
    .from('audits')
    .select('*')
    .eq('id', auditId)
    .eq('user_id', userId)
    .single()

  if (error) {
    console.error('Error fetching audit:', error)
    return null
  }

  return data
}

/**
 * Check if user can perform an audit (has remaining audits)
 */
export async function canPerformAudit(userId: string): Promise<boolean> {
  if (!isSupabaseConfigured) return true // Allow if not configured

  const profile = await getProfile(userId)
  if (!profile) return false

  // Pro users have unlimited
  if (profile.plan === 'pro' || profile.plan === 'enterprise') {
    return true
  }

  return profile.audits_remaining > 0
}

/**
 * Track API usage (for rate limiting)
 */
export async function trackApiUsage(userId: string, endpoint: string, ipAddress?: string): Promise<void> {
  if (!isSupabaseConfigured) return

  await supabase.from('api_usage').insert({
    user_id: userId,
    endpoint,
    ip_address: ipAddress,
  })
}

/**
 * Get today's API usage count for a user
 */
export async function getTodayUsageCount(userId: string): Promise<number> {
  if (!isSupabaseConfigured) return 0

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const { count, error } = await supabase
    .from('api_usage')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', userId)
    .gte('created_at', today.toISOString())

  if (error) {
    console.error('Error fetching usage:', error)
    return 0
  }

  return count || 0
}
