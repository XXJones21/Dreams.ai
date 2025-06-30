import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Provide fallback values for development/demo
const defaultUrl = 'https://demo.supabase.co';
const defaultKey = 'demo-key';

export const supabase = createClient(
  supabaseUrl || defaultUrl, 
  supabaseAnonKey || defaultKey
);

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

export interface UserRegistrationData {
  fullName: string;
  email: string;
  password: string;
  dateOfBirth: string;
  bio?: string;
  profilePicture?: File;
}

// Auth functions with error handling
export const signUp = async (email: string, password: string) => {
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`
      }
    });
    return { data, error };
  } catch (err) {
    console.error('SignUp error:', err);
    return { data: null, error: { message: 'Authentication service unavailable' } };
  }
};

export const signIn = async (email: string, password: string) => {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });
    return { data, error };
  } catch (err) {
    console.error('SignIn error:', err);
    return { data: null, error: { message: 'Authentication service unavailable' } };
  }
};

export const signOut = async () => {
  try {
    const { error } = await supabase.auth.signOut();
    return { error };
  } catch (err) {
    console.error('SignOut error:', err);
    return { error: { message: 'Sign out failed' } };
  }
};

export const resetPassword = async (email: string) => {
  try {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`
    });
    return { data, error };
  } catch (err) {
    console.error('Reset password error:', err);
    return { data: null, error: { message: 'Password reset service unavailable' } };
  }
};

// Profile functions with error handling
export const createProfile = async (profileData: Omit<Profile, 'id' | 'created_at' | 'updated_at'>) => {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .insert([profileData])
      .select()
      .single();
    return { data, error };
  } catch (err) {
    console.error('Create profile error:', err);
    return { data: null, error: { message: 'Profile creation failed' } };
  }
};

export const getProfile = async (userId: string) => {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('user_id', userId)
      .single();
    return { data, error };
  } catch (err) {
    console.error('Get profile error:', err);
    return { data: null, error: { message: 'Profile fetch failed' } };
  }
};

export const updateProfile = async (userId: string, updates: Partial<Profile>) => {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .update(updates)
      .eq('user_id', userId)
      .select()
      .single();
    return { data, error };
  } catch (err) {
    console.error('Update profile error:', err);
    return { data: null, error: { message: 'Profile update failed' } };
  }
};

// File upload functions with error handling
export const uploadProfilePicture = async (userId: string, file: File) => {
  try {
    const fileExt = file.name.split('.').pop();
    const fileName = `${userId}/${Date.now()}.${fileExt}`;
    
    const { data, error } = await supabase.storage
      .from('profile-pictures')
      .upload(fileName, file, {
        cacheControl: '3600',
        upsert: false
      });
    
    if (error) return { data: null, error };
    
    const { data: urlData } = supabase.storage
      .from('profile-pictures')
      .getPublicUrl(fileName);
    
    return { data: { ...data, publicUrl: urlData.publicUrl }, error: null };
  } catch (err) {
    console.error('Upload profile picture error:', err);
    return { data: null, error: { message: 'File upload failed' } };
  }
};

export const deleteProfilePicture = async (filePath: string) => {
  try {
    const { data, error } = await supabase.storage
      .from('profile-pictures')
      .remove([filePath]);
    return { data, error };
  } catch (err) {
    console.error('Delete profile picture error:', err);
    return { data: null, error: { message: 'File deletion failed' } };
  }
};