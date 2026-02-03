'use client'

import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { useAuth } from '@/contexts/AuthContext'

type AuthModalProps = {
  isOpen: boolean
  onClose: () => void
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [mounted, setMounted] = useState(false)

  const { signIn, signUp } = useAuth()

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!isOpen || !mounted) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Client-side validation
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRe.test(email)) {
      setError('Please enter a valid email address')
      return
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    setLoading(true)

    try {
      if (isLogin) {
        const { error } = await signIn(email, password)
        if (error) throw error
        onClose()
      } else {
        const { error } = await signUp(email, password)
        if (error) throw error
        setSuccess('Check your email to confirm your account!')
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const modalContent = (
    <>
      {/* Overlay */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          backgroundColor: 'rgba(0,0,0,0.85)',
          zIndex: 99998,
        }}
      />

      {/* Modal */}
      <div
        style={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 99999,
          width: '90%',
          maxWidth: '400px',
          backgroundColor: '#18181b',
          border: '1px solid #27272a',
          borderRadius: '16px',
          padding: '32px',
        }}
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: 'none',
            border: 'none',
            color: '#71717a',
            fontSize: '20px',
            cursor: 'pointer',
          }}
        >
          ✕
        </button>

        <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: 'white', marginBottom: '24px' }}>
          {isLogin ? 'Login' : 'Create Account'}
        </h2>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', color: '#a1a1aa', fontSize: '14px', marginBottom: '8px' }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              style={{
                width: '100%',
                backgroundColor: '#27272a',
                border: '1px solid #3f3f46',
                borderRadius: '8px',
                padding: '12px 16px',
                color: 'white',
                fontSize: '16px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', color: '#a1a1aa', fontSize: '14px', marginBottom: '8px' }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={6}
              style={{
                width: '100%',
                backgroundColor: '#27272a',
                border: '1px solid #3f3f46',
                borderRadius: '8px',
                padding: '12px 16px',
                color: 'white',
                fontSize: '16px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {error && (
            <p style={{ color: '#ef4444', fontSize: '14px', marginBottom: '16px' }}>{error}</p>
          )}

          {success && (
            <p style={{ color: '#10b981', fontSize: '14px', marginBottom: '16px' }}>{success}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              backgroundColor: '#059669',
              color: 'white',
              fontWeight: '500',
              padding: '12px',
              borderRadius: '8px',
              border: 'none',
              fontSize: '16px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.5 : 1,
            }}
          >
            {loading ? 'Loading...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <button
            onClick={() => {
              setIsLogin(!isLogin)
              setError('')
              setSuccess('')
            }}
            style={{
              background: 'none',
              border: 'none',
              color: '#a1a1aa',
              fontSize: '14px',
              cursor: 'pointer',
            }}
          >
            {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
          </button>
        </div>

        <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: '1px solid #27272a' }}>
          <p style={{ color: '#71717a', fontSize: '12px', textAlign: 'center' }}>
            Free tier includes 5 security audits per month
          </p>
        </div>
      </div>
    </>
  )

  return createPortal(modalContent, document.body)
}
