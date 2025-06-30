import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase environment variables not found. Using demo mode.');
}

// Provide fallback values for development/demo
const defaultUrl = 'https://demo.supabase.co';
const defaultKey = 'demo-key';

export const supabase = createClient(
  supabaseUrl || defaultUrl, 
  supabaseAnonKey || defaultKey
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

// Connection Test Function
export const testSupabaseConnection = async (): Promise<{ success: boolean; error?: string }> => {
  try {
    const { data, error } = await supabase.from('profiles').select('count').limit(1);
    
    if (error) {
      console.error('Supabase connection test failed:', error);
      return { success: false, error: error.message };
    }
    
    console.log('✅ Supabase connection successful');
    return { success: true };
  } catch (err) {
    console.error('Supabase connection test error:', err);
    return { success: false, error: 'Failed to connect to Supabase' };
  }
};

// Auth functions with comprehensive error handling
export const signUp = async (email: string, password: string) => {
  try {
    // Validate inputs
    if (!email || !password) {
      return { data: null, error: { message: 'Email and password are required' } };
    }

    if (password.length < 8) {
      return { data: null, error: { message: 'Password must be at least 8 characters long' } };
    }

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`,
        data: {
          email_confirm: false // Disable email confirmation for faster onboarding
        }
      }
    });

    if (error) {
      console.error('SignUp error:', error);
      return { data: null, error };
    }

    console.log('✅ User signed up successfully:', data.user?.email);
    return { data, error: null };
  } catch (err) {
    console.error('SignUp exception:', err);
    return { data: null, error: { message: 'Authentication service unavailable' } };
  }
};

export const signIn = async (email: string, password: string) => {
  try {
    if (!email || !password) {
      return { data: null, error: { message: 'Email and password are required' } };
    }

    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) {
      console.error('SignIn error:', error);
      
      // Provide user-friendly error messages
      if (error.message.includes('Invalid login credentials')) {
        return { data: null, error: { message: 'Invalid email or password' } };
      }
      
      return { data: null, error };
    }

    console.log('✅ User signed in successfully:', data.user?.email);
    return { data, error: null };
  } catch (err) {
    console.error('SignIn exception:', err);
    return { data: null, error: { message: 'Authentication service unavailable' } };
  }
};

export const signOut = async () => {
  try {
    const { error } = await supabase.auth.signOut();
    
    if (error) {
      console.error('SignOut error:', error);
      return { error };
    }

    console.log('✅ User signed out successfully');
    return { error: null };
  } catch (err) {
    console.error('SignOut exception:', err);
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
      console.error('Reset password error:', error);
      return { data: null, error };
    }

    console.log('✅ Password reset email sent to:', email);
    return { data, error: null };
  } catch (err) {
    console.error('Reset password exception:', err);
    return { data: null, error: { message: 'Password reset service unavailable' } };
  }
};

// Session Management
export const getCurrentUser = async () => {
  try {
    const { data: { user }, error } = await supabase.auth.getUser();
    
    if (error) {
      console.error('Get current user error:', error);
      return { user: null, error };
    }

    return { user, error: null };
  } catch (err) {
    console.error('Get current user exception:', err);
    return { user: null, error: { message: 'Failed to get current user' } };
  }
};

export const getCurrentSession = async () => {
  try {
    const { data: { session }, error } = await supabase.auth.getSession();
    
    if (error) {
      console.error('Get current session error:', error);
      return { session: null, error };
    }

    return { session, error: null };
  } catch (err) {
    console.error('Get current session exception:', err);
    return { session: null, error: { message: 'Failed to get current session' } };
  }
};

// Profile functions with enhanced error handling
export const createProfile = async (profileData: Omit<Profile, 'id' | 'created_at' | 'updated_at'>) => {
  try {
    // Validate required fields
    if (!profileData.user_id || !profileData.full_name || !profileData.email || !profileData.date_of_birth) {
      return { data: null, error: { message: 'Missing required profile fields' } };
    }

    const { data, error } = await supabase
      .from('profiles')
      .insert([profileData])
      .select()
      .single();

    if (error) {
      console.error('Create profile error:', error);
      
      if (error.code === '23505') { // Unique constraint violation
        return { data: null, error: { message: 'Profile already exists for this user' } };
      }
      
      return { data: null, error };
    }

    console.log('✅ Profile created successfully for user:', profileData.user_id);
    return { data, error: null };
  } catch (err) {
    console.error('Create profile exception:', err);
    return { data: null, error: { message: 'Profile creation failed' } };
  }
};

export const getProfile = async (userId: string) => {
  try {
    if (!userId) {
      return { data: null, error: { message: 'User ID is required' } };
    }

    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('user_id', userId)
      .single();

    if (error) {
      console.error('Get profile error:', error);
      
      if (error.code === 'PGRST116') { // No rows returned
        return { data: null, error: { message: 'Profile not found' } };
      }
      
      return { data: null, error };
    }

    return { data, error: null };
  } catch (err) {
    console.error('Get profile exception:', err);
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

    const { data, error } = await supabase
      .from('profiles')
      .update({ ...allowedUpdates, updated_at: new Date().toISOString() })
      .eq('user_id', userId)
      .select()
      .single();

    if (error) {
      console.error('Update profile error:', error);
      return { data: null, error };
    }

    console.log('✅ Profile updated successfully for user:', userId);
    return { data, error: null };
  } catch (err) {
    console.error('Update profile exception:', err);
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
    
    const { data, error } = await supabase.storage
      .from('profile-pictures')
      .upload(fileName, file, {
        cacheControl: '3600',
        upsert: false
      });
    
    if (error) {
      console.error('Upload profile picture error:', error);
      return { data: null, error };
    }
    
    const { data: urlData } = supabase.storage
      .from('profile-pictures')
      .getPublicUrl(fileName);
    
    console.log('✅ Profile picture uploaded successfully for user:', userId);
    return { data: { ...data, publicUrl: urlData.publicUrl }, error: null };
  } catch (err) {
    console.error('Upload profile picture exception:', err);
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
      console.error('Delete profile picture error:', error);
      return { data: null, error };
    }

    console.log('✅ Profile picture deleted successfully:', filePath);
    return { data, error: null };
  } catch (err) {
    console.error('Delete profile picture exception:', err);
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
      console.error('Create dream error:', error);
      return { data: null, error };
    }

    console.log('✅ Dream created successfully:', data.dream_name);
    return { data, error: null };
  } catch (err) {
    console.error('Create dream exception:', err);
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
      console.error('Get user dreams error:', error);
      return { data: null, error };
    }

    return { data, error: null };
  } catch (err) {
    console.error('Get user dreams exception:', err);
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
  }
});