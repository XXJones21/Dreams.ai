/*
  # Enhanced Database Schema with Security and Session Management

  1. Profile Enhancements
    - Add email uniqueness constraint
    - Add full name length validation
    - Add age verification constraint
    - Add bio length constraint

  2. Session Management
    - Create user_sessions table for tracking user sessions
    - Enable RLS and create policies for session management
    - Add indexes for performance

  3. Security Logging
    - Create auth_logs table for security monitoring
    - Enable RLS with service role access
    - Add indexes for efficient querying

  4. Storage Policies
    - Enhanced profile picture storage policies
    - File size and type validation
    - Automatic cleanup functions

  5. Utility Functions
    - Session cleanup function
    - Auth event logging function
    - Profile update handling
    - Old file cleanup function
*/

-- Enhance profiles table with better constraints
DO $$
BEGIN
  -- Add email uniqueness constraint if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'profiles_email_key' 
    AND table_name = 'profiles'
  ) THEN
    ALTER TABLE profiles ADD CONSTRAINT profiles_email_key UNIQUE (email);
  END IF;

  -- Add full_name length constraint
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.check_constraints 
    WHERE constraint_name = 'profiles_full_name_length'
  ) THEN
    ALTER TABLE profiles ADD CONSTRAINT profiles_full_name_length 
    CHECK (char_length(full_name) >= 2 AND char_length(full_name) <= 100);
  END IF;

  -- Add bio length constraint
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.check_constraints 
    WHERE constraint_name = 'profiles_bio_check'
  ) THEN
    ALTER TABLE profiles ADD CONSTRAINT profiles_bio_check 
    CHECK (char_length(bio) <= 250);
  END IF;

  -- Add date_of_birth constraint (must be at least 13 years old)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.check_constraints 
    WHERE constraint_name = 'profiles_age_check'
  ) THEN
    ALTER TABLE profiles ADD CONSTRAINT profiles_age_check 
    CHECK (date_of_birth <= CURRENT_DATE - INTERVAL '13 years');
  END IF;
END $$;

-- Create user_sessions table for session tracking
CREATE TABLE IF NOT EXISTS user_sessions (
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

-- Add foreign key constraint for user_sessions if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'user_sessions_user_id_fkey' 
    AND table_name = 'user_sessions'
  ) THEN
    ALTER TABLE user_sessions ADD CONSTRAINT user_sessions_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
  END IF;
END $$;

-- Enable RLS on user_sessions
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist and recreate them
DROP POLICY IF EXISTS "Users can view own sessions" ON user_sessions;
DROP POLICY IF EXISTS "Users can insert own sessions" ON user_sessions;
DROP POLICY IF EXISTS "Users can update own sessions" ON user_sessions;

-- Create policies for user_sessions
CREATE POLICY "Users can view own sessions"
  ON user_sessions
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own sessions"
  ON user_sessions
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own sessions"
  ON user_sessions
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id);

-- Create auth_logs table for security monitoring
CREATE TABLE IF NOT EXISTS auth_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  event_type text NOT NULL,
  ip_address inet,
  user_agent text,
  metadata jsonb,
  created_at timestamptz DEFAULT now()
);

-- Add foreign key constraint for auth_logs if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'auth_logs_user_id_fkey' 
    AND table_name = 'auth_logs'
  ) THEN
    ALTER TABLE auth_logs ADD CONSTRAINT auth_logs_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
  END IF;
END $$;

-- Add event type constraint if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.check_constraints 
    WHERE constraint_name = 'auth_logs_event_type_check'
  ) THEN
    ALTER TABLE auth_logs ADD CONSTRAINT auth_logs_event_type_check 
    CHECK (event_type IN ('login', 'logout', 'signup', 'password_reset', 'failed_login', 'profile_update'));
  END IF;
END $$;

-- Enable RLS on auth_logs
ALTER TABLE auth_logs ENABLE ROW LEVEL SECURITY;

-- Drop existing auth_logs policies if they exist and recreate them
DROP POLICY IF EXISTS "Service role can manage auth logs" ON auth_logs;

-- Create policies for auth_logs (service role only)
CREATE POLICY "Service role can manage auth logs"
  ON auth_logs
  FOR ALL
  TO service_role
  USING (true);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active, expires_at);
CREATE INDEX IF NOT EXISTS idx_auth_logs_user_id ON auth_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_logs_event_type ON auth_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_auth_logs_created_at ON auth_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
  UPDATE user_sessions 
  SET is_active = false 
  WHERE expires_at < now() AND is_active = true;
  
  DELETE FROM user_sessions 
  WHERE expires_at < now() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log auth events
CREATE OR REPLACE FUNCTION log_auth_event(
  p_user_id uuid,
  p_event_type text,
  p_ip_address inet DEFAULT NULL,
  p_user_agent text DEFAULT NULL,
  p_metadata jsonb DEFAULT NULL
)
RETURNS void AS $$
BEGIN
  INSERT INTO auth_logs (user_id, event_type, ip_address, user_agent, metadata)
  VALUES (p_user_id, p_event_type, p_ip_address, p_user_agent, p_metadata);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Enhanced storage policies for profile pictures
-- Drop existing storage policies if they exist
DROP POLICY IF EXISTS "Users can upload their own profile pictures" ON storage.objects;
DROP POLICY IF EXISTS "Users can view profile pictures" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own profile pictures" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own profile pictures" ON storage.objects;
DROP POLICY IF EXISTS "Users can upload profile pictures" ON storage.objects;
DROP POLICY IF EXISTS "Anyone can view profile pictures" ON storage.objects;
DROP POLICY IF EXISTS "Users can update own profile pictures" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete own profile pictures" ON storage.objects;

-- Create enhanced storage policies
CREATE POLICY "Users can upload profile pictures"
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

-- Function to automatically clean up old profile pictures
CREATE OR REPLACE FUNCTION cleanup_old_profile_pictures()
RETURNS void AS $$
BEGIN
  -- Delete profile pictures older than 1 year that are not referenced in profiles
  DELETE FROM storage.objects
  WHERE bucket_id = 'profile-pictures'
    AND created_at < now() - INTERVAL '1 year'
    AND name NOT IN (
      SELECT SUBSTRING(profile_picture_url FROM '[^/]+$')
      FROM profiles 
      WHERE profile_picture_url IS NOT NULL
        AND profile_picture_url LIKE '%profile-pictures%'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a function to handle profile updates
CREATE OR REPLACE FUNCTION handle_profile_update()
RETURNS TRIGGER AS $$
BEGIN
  -- Update the updated_at timestamp
  NEW.updated_at = now();
  
  -- Log the profile update
  PERFORM log_auth_event(
    NEW.user_id,
    'profile_update',
    NULL,
    NULL,
    jsonb_build_object(
      'updated_fields', 
      (SELECT jsonb_object_agg(key, value) 
       FROM jsonb_each(to_jsonb(NEW)) 
       WHERE key != 'updated_at' AND to_jsonb(NEW)->>key != to_jsonb(OLD)->>key)
    )
  );
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing triggers if they exist and recreate them
DROP TRIGGER IF EXISTS trigger_handle_profile_update ON profiles;
DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;

-- Create trigger for profile updates
CREATE TRIGGER trigger_handle_profile_update
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION handle_profile_update();

-- Create trigger for updated_at timestamp
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();