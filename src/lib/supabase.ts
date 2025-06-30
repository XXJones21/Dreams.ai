import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

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

// Auth functions
export const signUp = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: `${window.location.origin}/auth/callback`
    }
  });
  return { data, error };
};

export const signIn = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  });
  return { data, error };
};

export const signOut = async () => {
  const { error } = await supabase.auth.signOut();
  return { error };
};

export const resetPassword = async (email: string) => {
  const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${window.location.origin}/auth/reset-password`
  });
  return { data, error };
};

// Profile functions
export const createProfile = async (profileData: Omit<Profile, 'id' | 'created_at' | 'updated_at'>) => {
  const { data, error } = await supabase
    .from('profiles')
    .insert([profileData])
    .select()
    .single();
  return { data, error };
};

export const getProfile = async (userId: string) => {
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('user_id', userId)
    .single();
  return { data, error };
};

export const updateProfile = async (userId: string, updates: Partial<Profile>) => {
  const { data, error } = await supabase
    .from('profiles')
    .update(updates)
    .eq('user_id', userId)
    .select()
    .single();
  return { data, error };
};

// File upload functions
export const uploadProfilePicture = async (userId: string, file: File) => {
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
};

export const deleteProfilePicture = async (filePath: string) => {
  const { data, error } = await supabase.storage
    .from('profile-pictures')
    .remove([filePath]);
  return { data, error };
};