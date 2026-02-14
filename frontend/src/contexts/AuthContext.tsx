'use client'

import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { toast } from 'sonner'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import { User, Session } from '@supabase/supabase-js'
import { trackEvent } from '@/lib/api'

const PROTECTED_ROUTES = ['/dashboard', '/audit']

type AuthContextType = {
  user: User | null
  session: Session | null
  loading: boolean
  isConfigured: boolean
  signIn: (email: string, password: string) => Promise<{ error: Error | null }>
  signUp: (email: string, password: string) => Promise<{ error: Error | null }>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(isSupabaseConfigured)
  const router = useRouter()
  const pathname = usePathname()

  const redirectIfProtected = useCallback(() => {
    if (PROTECTED_ROUTES.some((r) => pathname.startsWith(r))) {
      router.replace('/')
    }
  }, [pathname, router])

  useEffect(() => {
    if (!isSupabaseConfigured) {
      return
    }

    supabase.auth.getSession().then(({ data: { session }, error }) => {
      if (error) {
        console.error('Failed to restore session:', error.message)
        setSession(null)
        setUser(null)
      } else {
        setSession(session)
        setUser(session?.user ?? null)
      }
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setSession(session)
      setUser(session?.user ?? null)

      if (event === 'TOKEN_REFRESHED') {
        console.debug('Auth token refreshed')
      }

      if (event === 'SIGNED_OUT') {
        setSession(null)
        setUser(null)
      }

      // Handle expired or invalid session - redirect from protected routes
      if (!session && event !== 'SIGNED_OUT' && event !== 'INITIAL_SESSION') {
        toast.error('Your session has expired. Please sign in again.')
        redirectIfProtected()
      }
    })

    return () => subscription.unsubscribe()
  }, [redirectIfProtected])

  const signIn = async (email: string, password: string) => {
    if (!isSupabaseConfigured) {
      return { error: new Error('Authentication not configured') }
    }
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (!error) {
      trackEvent({
        event_type: 'signin_completed',
        payload: { email_domain: email.split('@')[1] || '' },
        source: 'auth',
      })
    }
    return { error }
  }

  const signUp = async (email: string, password: string) => {
    if (!isSupabaseConfigured) {
      return { error: new Error('Authentication not configured') }
    }
    const redirectTo = typeof window !== 'undefined'
      ? `${window.location.origin}/auth/callback`
      : 'https://fk94platform.vercel.app/auth/callback'
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { emailRedirectTo: redirectTo }
    })
    if (!error) {
      trackEvent({
        event_type: 'signup_completed',
        payload: { email_domain: email.split('@')[1] || '' },
        source: 'auth',
      })
    }
    return { error }
  }

  const signOut = async () => {
    if (!isSupabaseConfigured) return
    await supabase.auth.signOut()
    router.replace('/')
  }

  return (
    <AuthContext.Provider value={{
      user,
      session,
      loading,
      isConfigured: isSupabaseConfigured,
      signIn,
      signUp,
      signOut
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
