import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Enhanced error checking for environment variables
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ Missing Supabase environment variables!');
  console.error('VITE_SUPABASE_URL:', supabaseUrl ? '✅ Set' : '❌ Missing');
  console.error('VITE_SUPABASE_ANON_KEY:', supabaseAnonKey ? '✅ Set' : '❌ Missing');
  console.error('Please check your .env file and ensure it contains valid Supabase credentials.');
}

// Validate URL format
const isValidUrl = (url: string) => {
  try {
    new URL(url);
    return url.includes('supabase.co') || url.includes('localhost');
  } catch {
    return false;
  }
};

if (supabaseUrl && !isValidUrl(supabaseUrl)) {
  console.error('❌ Invalid Supabase URL format:', supabaseUrl);
  console.error('Expected format: https://your-project-ref.supabase.co');
}

// Create Supabase client with enhanced configuration
export const supabase = createClient(
  supabaseUrl || 'https://demo.supabase.co', 
  supabaseAnonKey || 'demo-key',
  {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
      flowType: 'pkce'
    },
    global: {
      headers: {
        'X-Client-Info': 'dreams-ai-web'
      }
    },
    db: {
      schema: 'public'
    },
    realtime: {
      params: {
        eventsPerSecond: 10
      }
    }
  }
);

// Database Types
export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: Profile;
        Insert: Omit<Profile, 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Omit<Profile, 'id' | 'user_id' | 'created_at'>>;
      };
      dreams: {
        Row: Dream;
        Insert: Omit<Dream, 'id' | 'created_at'>;
        Update: Partial<Omit<Dream, 'id' | 'user_id' | 'created_at'>>;
      };
    };
  };
}

// Types
export interface Profile {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  profile_picture_url?: string;
  bio?: string;
  date_of_birth: string;
  created_at: string;
  updated_at: string;
}

export interface Dream {
  id: string;
  user_id?: string;
  dream_name: string;
  story_prompt?: string;
  initial_goal?: string;
  pitch?: string;
  created_at: string;
  image_url?: string;
  is_public: boolean;
}

export interface UserRegistrationData {
  fullName: string;
  email: string;
  password: string;
  dateOfBirth: string;
  bio?: string;
  profilePicture?: File;
}

export interface AuthError {
  message: string;
  status?: number;
}

// Simplified Connection Test Function
export const testSupabaseConnection = async (): Promise<{ success: boolean; error?: string; details?: any }> => {
  try {
    console.log('🔍 Testing Supabase connection...');

    // Check environment variables first
    if (!supabaseUrl || !supabaseAnonKey) {
      return {
        success: false,
        error: 'Missing environment variables. Please check your .env file.',
        details: {
          hasUrl: !!supabaseUrl,
          hasKey: !!supabaseAnonKey,
          envFile: 'Make sure .env file exists with VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY'
        }
      };
    }

    // Test basic auth functionality with timeout
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Connection timeout')), 10000)
    );

    const authPromise = supabase.auth.getSession();
    
    const { data, error } = await Promise.race([authPromise, timeoutPromise]) as any;
    
    if (error) {
      console.error('❌ Auth session error:', error);
      return { 
        success: false, 
        error: `Auth error: ${error.message}`,
        details: { authError: error }
      };
    }
    
    console.log('✅ Supabase connection successful');
    return { success: true };
    
  } catch (err: any) {
    console.error('❌ Supabase connection test error:', err);
    
    let errorMessage = 'Failed to connect to Supabase';
    let details: any = {
      originalError: err.message
    };
    
    if (err.message?.includes('fetch') || err.message?.includes('timeout')) {
      errorMessage = 'Network error: Unable to reach Supabase. Check your internet connection and Supabase URL.';
      details.networkIssue = true;
    }
    
    return { 
      success: false, 
      error: errorMessage,
      details
    };
  }
};

// Enhanced Auth functions with better error handling and timeouts
export const signUp = async (email: string, password: string) => {
  try {
    // Validate inputs
    if (!email || !password) {
      return { data: null, error: { message: 'Email and password are required' } };
    }

    if (password.length < 6) {
      return { data: null, error: { message: 'Password must be at least 6 characters long' } };
    }

    console.log('🔐 Attempting to sign up user:', email);

    // Add timeout to prevent hanging
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Sign up timeout')), 15000)
    );

    const signUpPromise = supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`
      }
    });

    const { data, error } = await Promise.race([signUpPromise, timeoutPromise]) as any;

    if (error) {
      console.error('❌ SignUp error:', error);
      return { data: null, error };
    }

    console.log('✅ User signed up successfully:', data.user?.email);
    return { data, error: null };
  } catch (err: any) {
    console.error('❌ SignUp exception:', err);
    if (err.message?.includes('timeout')) {
      return { data: null, error: { message: 'Sign up timed out. Please try again.' } };
    }
    return { data: null, error: { message: 'Authentication service unavailable' } };
  }
};

export const signIn = async (email: string, password: string) => {
  try {
    if (!email || !password) {
      return { data: null, error: { message: 'Email and password are required' } };
    }

    console.log('🔐 Attempting to sign in user:', email);

    // Add timeout to prevent hanging
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Sign in timeout')), 15000)
    );

    const signInPromise = supabase.auth.signInWithPassword({
      email,
      password
    });

    const { data, error } = await Promise.race([signInPromise, timeoutPromise]) as any;

    if (error) {
      console.error('❌ SignIn error:', error);
      
      // Provide user-friendly error messages
      if (error.message.includes('Invalid login credentials')) {
        return { data: null, error: { message: 'Invalid email or password' } };
      }
      
      if (error.message.includes('Email not confirmed')) {
        return { data: null, error: { message: 'Please check your email and confirm your account' } };
      }
      
      return { data: null, error };
    }

    console.log('✅ User signed in successfully:', data.user?.email);
    return { data, error: null };
  } catch (err: any) {
    console.error('❌ SignIn exception:', err);
    if (err.message?.includes('timeout')) {
      return { data: null, error: { message: 'Sign in timed out. Please try again.' } };
    }
    return { data: null, error: { message: 'Authentication service unavailable' } };
  }
};

export const signOut = async () => {
  try {
    const { error } = await supabase.auth.signOut();
    
    if (error) {
      console.error('❌ SignOut error:', error);
      return { error };
    }

    console.log('✅ User signed out successfully');
    return { error: null };
  } catch (err: any) {
    console.error('❌ SignOut exception:', err);
    return { error: { message: 'Sign out failed' } };
  }
};

export const resetPassword = async (email: string) => {
  try {
    if (!email) {
      return { data: null, error: { message: 'Email is required' } };
    }

    const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`
    });

    if (error) {
      console.error('❌ Reset password error:', error);
      return { data: null, error };
    }

    console.log('✅ Password reset email sent to:', email);
    return { data, error: null };
  } catch (err: any) {
    console.error('❌ Reset password exception:', err);
    return { data: null, error: { message: 'Password reset service unavailable' } };
  }
};

// Session Management with timeouts
export const getCurrentUser = async () => {
  try {
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Get user timeout')), 10000)
    );

    const userPromise = supabase.auth.getUser();
    
    const { data: { user }, error } = await Promise.race([userPromise, timeoutPromise]) as any;
    
    if (error) {
      console.error('❌ Get current user error:', error);
      return { user: null, error };
    }

    return { user, error: null };
  } catch (err: any) {
    console.error('❌ Get current user exception:', err);
    if (err.message?.includes('timeout')) {
      return { user: null, error: { message: 'Request timed out. Please refresh the page.' } };
    }
    return { user: null, error: { message: 'Failed to get current user' } };
  }
};

export const getCurrentSession = async () => {
  try {
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Get session timeout')), 10000)
    );

    const sessionPromise = supabase.auth.getSession();
    
    const { data: { session }, error } = await Promise.race([sessionPromise, timeoutPromise]) as any;
    
    if (error) {
      console.error('❌ Get current session error:', error);
      return { session: null, error };
    }

    return { session, error: null };
  } catch (err: any) {
    console.error('❌ Get current session exception:', err);
    if (err.message?.includes('timeout')) {
      return { session: null, error: { message: 'Session request timed out. Please refresh the page.' } };
    }
    return { session: null, error: { message: 'Failed to get current session' } };
  }
};

// Profile functions with enhanced error handling and timeouts
export const createProfile = async (profileData: Omit<Profile, 'id' | 'created_at' | 'updated_at'>) => {
  try {
    // Validate required fields
    if (!profileData.user_id || !profileData.full_name || !profileData.email || !profileData.date_of_birth) {
      return { data: null, error: { message: 'Missing required profile fields' } };
    }

    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Create profile timeout')), 15000)
    );

    const createPromise = supabase
      .from('profiles')
      .insert([profileData])
      .select()
      .single();

    const { data, error } = await Promise.race([createPromise, timeoutPromise]) as any;

    if (error) {
      console.error('❌ Create profile error:', error);
      
      if (error.code === '23505') { // Unique constraint violation
        return { data: null, error: { message: 'Profile already exists for this user' } };
      }
      
      return { data: null, error };
    }

    console.log('✅ Profile created successfully for user:', profileData.user_id);
    return { data, error: null };
  } catch (err: any) {
    console.error('❌ Create profile exception:', err);
    if (err.message?.includes('timeout')) {
      return { data: null, error: { message: 'Profile creation timed out. Please try again.' } };
    }
    return { data: null, error: { message: 'Profile creation failed' } };
  }
};

export const getProfile = async (userId: string) => {
  try {
    if (!userId) {
      return { data: null, error: { message: 'User ID is required' } };
    }

    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Get profile timeout')), 10000)
    );

    const profilePromise = supabase
      .from('profiles')
      .select('*')
      .eq('user_id', userId)
      .single();

    const { data, error } = await Promise.race([profilePromise, timeoutPromise]) as any;

    if (error) {
      console.error('❌ Get profile error:', error);
      
      if (error.code === 'PGRST116') { // No rows returned
        return { data: null, error: { message: 'Profile not found' } };
      }
      
      return { data: null, error };
    }

    return { data, error: null };
  } catch (err: any) {
    console.error('❌ Get profile exception:', err);
    if (err.message?.includes('timeout')) {
      return { data: null, error: { message: 'Profile fetch timed out. Please refresh the page.' } };
    }
    return { data: null, error: { message: 'Profile fetch failed' } };
  }
};

export const updateProfile = async (userId: string, updates: Partial<Profile>) => {
  try {
    if (!userId) {
      return { data: null, error: { message: 'User ID is required' } };
    }

    // Remove fields that shouldn't be updated
    const { id, user_id, created_at, ...allowedUpdates } = updates;

    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Update profile timeout')), 15000)
    );

    const updatePromise = supabase
      .from('profiles')
      .update({ ...allowedUpdates, updated_at: new Date().toISOString() })
      .eq('user_id', userId)
      .select()
      .single();

    const { data, error } = await Promise.race([updatePromise, timeoutPromise]) as any;

    if (error) {
      console.error('❌ Update profile error:', error);
      return { data: null, error };
    }

    console.log('✅ Profile updated successfully for user:', userId);
    return { data, error: null };
  } catch (err: any) {
    console.error('❌ Update profile exception:', err);
    if (err.message?.includes('timeout')) {
      return { data: null, error: { message: 'Profile update timed out. Please try again.' } };
    }
    return { data: null, error: { message: 'Profile update failed' } };
  }
};

// File upload functions with enhanced error handling
export const uploadProfilePicture = async (userId: string, file: File) => {
  try {
    if (!userId || !file) {
      return { data: null, error: { message: 'User ID and file are required' } };
    }

    // Validate file type and size
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      return { data: null, error: { message: 'Invalid file type. Please upload a JPEG, PNG, or WebP image.' } };
    }

    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      return { data: null, error: { message: 'File size too large. Please upload an image smaller than 5MB.' } };
    }

    const fileExt = file.name.split('.').pop();
    const fileName = `${userId}/${Date.now()}.${fileExt}`;
    
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Upload timeout')), 30000)
    );

    const uploadPromise = supabase.storage
      .from('profile-pictures')
      .upload(fileName, file, {
        cacheControl: '3600',
        upsert: false
      });
    
    const { data, error } = await Promise.race([uploadPromise, timeoutPromise]) as any;
    
    if (error) {
      console.error('❌ Upload profile picture error:', error);
      return { data: null, error };
    }
    
    const { data: urlData } = supabase.storage
      .from('profile-pictures')
      .getPublicUrl(fileName);
    
    console.log('✅ Profile picture uploaded successfully for user:', userId);
    return { data: { ...data, publicUrl: urlData.publicUrl }, error: null };
  } catch (err: any) {
    console.error('❌ Upload profile picture exception:', err);
    if (err.message?.includes('timeout')) {
      return { data: null, error: { message: 'File upload timed out. Please try again.' } };
    }
    return { data: null, error: { message: 'File upload failed' } };
  }
};

export const deleteProfilePicture = async (filePath: string) => {
  try {
    if (!filePath) {
      return { data: null, error: { message: 'File path is required' } };
    }

    const { data, error } = await supabase.storage
      .from('profile-pictures')
      .remove([filePath]);

    if (error) {
      console.error('❌ Delete profile picture error:', error);
      return { data: null, error };
    }

    console.log('✅ Profile picture deleted successfully:', filePath);
    return { data, error: null };
  } catch (err: any) {
    console.error('❌ Delete profile picture exception:', err);
    return { data: null, error: { message: 'File deletion failed' } };
  }
};

// Dreams functions
export const createDream = async (dreamData: Omit<Dream, 'id' | 'created_at'>) => {
  try {
    const { data, error } = await supabase
      .from('dreams')
      .insert([dreamData])
      .select()
      .single();

    if (error) {
      console.error('❌ Create dream error:', error);
      return { data: null, error };
    }

    console.log('✅ Dream created successfully:', data.dream_name);
    return { data, error: null };
  } catch (err: any) {
    console.error('❌ Create dream exception:', err);
    return { data: null, error: { message: 'Dream creation failed' } };
  }
};

export const getUserDreams = async (userId: string) => {
  try {
    if (!userId) {
      return { data: null, error: { message: 'User ID is required' } };
    }

    const { data, error } = await supabase
      .from('dreams')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('❌ Get user dreams error:', error);
      return { data: null, error };
    }

    return { data, error: null };
  } catch (err: any) {
    console.error('❌ Get user dreams exception:', err);
    return { data: null, error: { message: 'Failed to fetch dreams' } };
  }
};

// Auth state change listener
export const onAuthStateChange = (callback: (event: string, session: any) => void) => {
  return supabase.auth.onAuthStateChange(callback);
};

// Initialize connection test on module load
testSupabaseConnection().then(result => {
  if (!result.success) {
    console.warn('⚠️ Supabase connection failed:', result.error);
    console.warn('Details:', result.details);
  }
});