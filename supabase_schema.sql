-- FK94 Security Platform - Supabase Schema
-- Run this in the Supabase SQL Editor after creating your project

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User profiles (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT NOT NULL,
  full_name TEXT,
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
  audits_remaining INT DEFAULT 5,
  audits_total INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audits history
CREATE TABLE IF NOT EXISTS public.audits (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  audit_type TEXT NOT NULL CHECK (audit_type IN ('email', 'username', 'phone', 'domain', 'name', 'ip', 'wallet')),
  query_value TEXT NOT NULL,
  security_score INT,
  risk_level TEXT CHECK (risk_level IN ('critical', 'high', 'medium', 'low', 'safe')),
  result_data JSONB,
  ai_analysis TEXT,
  recommendations TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Saved reports (PDFs)
CREATE TABLE IF NOT EXISTS public.reports (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  audit_id UUID REFERENCES public.audits(id) ON DELETE CASCADE,
  file_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- API usage tracking (for rate limiting)
CREATE TABLE IF NOT EXISTS public.api_usage (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  endpoint TEXT NOT NULL,
  ip_address TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_audits_user_id ON public.audits(user_id);
CREATE INDEX IF NOT EXISTS idx_audits_created_at ON public.audits(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_user_created ON public.api_usage(user_id, created_at);

-- Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_usage ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile"
  ON public.profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

-- Audits policies
CREATE POLICY "Users can view own audits"
  ON public.audits FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own audits"
  ON public.audits FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Reports policies
CREATE POLICY "Users can view own reports"
  ON public.reports FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own reports"
  ON public.reports FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- API usage policies
CREATE POLICY "Users can view own usage"
  ON public.api_usage FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "System can insert usage"
  ON public.api_usage FOR INSERT
  WITH CHECK (true);

-- Function to create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email)
  VALUES (NEW.id, NEW.email);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update audits_remaining
CREATE OR REPLACE FUNCTION public.decrement_audits()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE public.profiles
  SET
    audits_remaining = GREATEST(audits_remaining - 1, 0),
    audits_total = audits_total + 1,
    updated_at = NOW()
  WHERE id = NEW.user_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to decrement audits on new audit
DROP TRIGGER IF EXISTS on_audit_created ON public.audits;
CREATE TRIGGER on_audit_created
  AFTER INSERT ON public.audits
  FOR EACH ROW EXECUTE FUNCTION public.decrement_audits();

-- Function to reset free audits monthly (run via cron)
CREATE OR REPLACE FUNCTION public.reset_monthly_audits()
RETURNS void AS $$
BEGIN
  UPDATE public.profiles
  SET audits_remaining = 5
  WHERE plan = 'free';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
