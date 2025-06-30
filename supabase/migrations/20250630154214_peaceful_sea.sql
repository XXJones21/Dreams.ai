/*
  # Comprehensive Database Schema Consolidation

  This migration consolidates all database schema, policies, and functions into a single,
  authoritative migration that replaces all previous policy-related migrations.

  ## What this migration does:
  1. Completely rebuilds all RLS policies from scratch
  2. Ensures all tables have proper structure and constraints
  3. Creates all necessary functions and triggers
  4. Sets up storage policies correctly
  5. Provides a clean, conflict-free foundation

  ## Tables affected:
  - profiles (user profile data)
  - dreams (user-generated dreams)
  - user_sessions (session tracking)
  - auth_logs (security logging)

  ## Storage buckets:
  - profile-pictures (user avatar storage)
*/

-- =====================================================
-- STEP 1: CLEAN SLATE - Remove all existing policies
-- =====================================================

-- Drop all existing RLS policies to start fresh
DO $$
DECLARE
    r RECORD;
BEGIN
    -- Drop all policies on profiles table
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'profiles' AND schemaname = 'public') LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.profiles', r.policyname);
    END LOOP;
    
    -- Drop all policies on dreams table
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'dreams' AND schemaname = 'public') LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.dreams', r.policyname);
    END LOOP;
    
    -- Drop all policies on user_sessions table
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'user_sessions' AND schemaname = 'public') LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.user_sessions', r.policyname);
    END LOOP;
    
    -- Drop all policies on auth_logs table
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'auth_logs' AND schemaname = 'public') LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.auth_logs', r.policyname);
    END LOOP;
    
    -- Drop all storage policies
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'objects' AND schemaname = 'storage') LOOP
        IF r.policyname LIKE '%profile%' OR r.policyname LIKE '%picture%' THEN
            EXECUTE format('DROP POLICY IF EXISTS %I ON storage.objects', r.policyname);
        END IF;
    END LOOP;
END $$;

-- =====================================================
-- STEP 2: ENSURE PROPER TABLE STRUCTURE
-- =====================================================

-- Profiles table with all necessary columns and constraints
CREATE TABLE IF NOT EXISTS public.profiles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid UNIQUE NOT NULL,
    full_name text NOT NULL,
    email text UNIQUE NOT NULL,
    profile_picture_url text,
    bio text,
    date_of_birth date NOT NULL,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Add foreign key constraint if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'profiles_user_id_fkey' 
        AND table_name = 'profiles'
        AND constraint_schema = 'public'
    ) THEN
        ALTER TABLE public.profiles 
        ADD CONSTRAINT profiles_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Add check constraints if they don't exist
DO $$
BEGIN
    -- Full name length constraint
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'profiles_full_name_length'
        AND constraint_schema = 'public'
    ) THEN
        ALTER TABLE public.profiles 
        ADD CONSTRAINT profiles_full_name_length 
        CHECK (char_length(full_name) >= 2 AND char_length(full_name) <= 100);
    END IF;

    -- Bio length constraint
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'profiles_bio_check'
        AND constraint_schema = 'public'
    ) THEN
        ALTER TABLE public.profiles 
        ADD CONSTRAINT profiles_bio_check 
        CHECK (char_length(bio) <= 250);
    END IF;

    -- Age constraint (must be at least 13 years old)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'profiles_age_check'
        AND constraint_schema = 'public'
    ) THEN
        ALTER TABLE public.profiles 
        ADD CONSTRAINT profiles_age_check 
        CHECK (date_of_birth <= CURRENT_DATE - INTERVAL '13 years');
    END IF;
END $$;

-- Dreams table
CREATE TABLE IF NOT EXISTS public.dreams (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid,
    dream_name text NOT NULL,
    story_prompt text,
    initial_goal text,
    pitch text,
    created_at timestamptz DEFAULT now(),
    image_url text,
    is_public boolean DEFAULT false
);

-- Add foreign key for dreams if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'dreams_user_id_fkey' 
        AND table_name = 'dreams'
        AND constraint_schema = 'public'
    ) THEN
        ALTER TABLE public.dreams 
        ADD CONSTRAINT dreams_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES auth.users(id);
    END IF;
END $$;

-- User sessions table
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    session_token text NOT NULL,
    device_info jsonb,
    ip_address inet,
    user_agent text,
    created_at timestamptz DEFAULT now(),
    last_accessed_at timestamptz DEFAULT now(),
    expires_at timestamptz NOT NULL,
    is_active boolean DEFAULT true
);

-- Add foreign key for user_sessions if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'user_sessions_user_id_fkey' 
        AND table_name = 'user_sessions'
        AND constraint_schema = 'public'
    ) THEN
        ALTER TABLE public.user_sessions 
        ADD CONSTRAINT user_sessions_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Auth logs table
CREATE TABLE IF NOT EXISTS public.auth_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid,
    event_type text NOT NULL,
    ip_address inet,
    user_agent text,
    metadata jsonb,
    created_at timestamptz DEFAULT now()
);

-- Add constraints for auth_logs
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'auth_logs_user_id_fkey' 
        AND table_name = 'auth_logs'
        AND constraint_schema = 'public'
    ) THEN
        ALTER TABLE public.auth_logs 
        ADD CONSTRAINT auth_logs_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE SET NULL;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints 
        WHERE constraint_name = 'auth_logs_event_type_check'
        AND constraint_schema = 'public'
    ) THEN
        ALTER TABLE public.auth_logs 
        ADD CONSTRAINT auth_logs_event_type_check 
        CHECK (event_type IN ('login', 'logout', 'signup', 'password_reset', 'failed_login', 'profile_update'));
    END IF;
END $$;

-- =====================================================
-- STEP 3: ENABLE RLS ON ALL TABLES
-- =====================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dreams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.auth_logs ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- STEP 4: CREATE ALL RLS POLICIES (CLEAN SLATE)
-- =====================================================

-- Profiles policies
CREATE POLICY "Users can view own profile"
    ON public.profiles
    FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
    ON public.profiles
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Dreams policies
CREATE POLICY "Users can view own dreams"
    ON public.dreams
    FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own dreams"
    ON public.dreams
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own dreams"
    ON public.dreams
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own dreams"
    ON public.dreams
    FOR DELETE
    TO authenticated
    USING (auth.uid() = user_id);

-- User sessions policies
CREATE POLICY "Users can view own sessions"
    ON public.user_sessions
    FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own sessions"
    ON public.user_sessions
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own sessions"
    ON public.user_sessions
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = user_id);

-- Auth logs policies (service role only)
CREATE POLICY "Service role can manage auth logs"
    ON public.auth_logs
    FOR ALL
    TO service_role
    USING (true);

-- =====================================================
-- STEP 5: CREATE STORAGE POLICIES
-- =====================================================

-- Ensure profile-pictures bucket exists
INSERT INTO storage.buckets (id, name, public)
VALUES ('profile-pictures', 'profile-pictures', true)
ON CONFLICT (id) DO NOTHING;

-- Storage policies for profile pictures
CREATE POLICY "Users can upload own profile pictures"
    ON storage.objects
    FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'profile-pictures' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Anyone can view profile pictures"
    ON storage.objects
    FOR SELECT
    USING (bucket_id = 'profile-pictures');

CREATE POLICY "Users can update own profile pictures"
    ON storage.objects
    FOR UPDATE
    TO authenticated
    USING (
        bucket_id = 'profile-pictures' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can delete own profile pictures"
    ON storage.objects
    FOR DELETE
    TO authenticated
    USING (
        bucket_id = 'profile-pictures' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- =====================================================
-- STEP 6: CREATE INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON public.profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_dreams_user_id ON public.dreams(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON public.user_sessions(is_active, expires_at);
CREATE INDEX IF NOT EXISTS idx_auth_logs_user_id ON public.auth_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_logs_event_type ON public.auth_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_auth_logs_created_at ON public.auth_logs(created_at);

-- =====================================================
-- STEP 7: CREATE UTILITY FUNCTIONS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to handle profile updates with logging
CREATE OR REPLACE FUNCTION public.handle_profile_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the updated_at timestamp
    NEW.updated_at = now();
    
    -- Log the profile update (with error handling)
    BEGIN
        INSERT INTO public.auth_logs (user_id, event_type, metadata)
        VALUES (
            NEW.user_id,
            'profile_update',
            jsonb_build_object('updated_at', now())
        );
    EXCEPTION WHEN OTHERS THEN
        -- Ignore logging errors to prevent profile update failures
        NULL;
    END;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION public.cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    UPDATE public.user_sessions 
    SET is_active = false 
    WHERE expires_at < now() AND is_active = true;
    
    DELETE FROM public.user_sessions 
    WHERE expires_at < now() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- STEP 8: CREATE TRIGGERS
-- =====================================================

-- Drop existing triggers to avoid conflicts
DROP TRIGGER IF EXISTS update_profiles_updated_at ON public.profiles;
DROP TRIGGER IF EXISTS trigger_handle_profile_update ON public.profiles;

-- Create triggers
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER trigger_handle_profile_update
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_profile_update();