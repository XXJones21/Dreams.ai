import { supabase } from '../lib/supabase';

// Email validation
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Password validation
export const validatePassword = (password: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }
  
  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

// Age validation
export const validateAge = (dateOfBirth: string): { isValid: boolean; age: number } => {
  const today = new Date();
  const birthDate = new Date(dateOfBirth);
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  
  return {
    isValid: age >= 13,
    age
  };
};

// File validation
export const validateProfilePicture = (file: File): { isValid: boolean; error?: string } => {
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  const maxSize = 5 * 1024 * 1024; // 5MB
  
  if (!allowedTypes.includes(file.type)) {
    return {
      isValid: false,
      error: 'Please upload a valid image file (JPEG, PNG, or WebP)'
    };
  }
  
  if (file.size > maxSize) {
    return {
      isValid: false,
      error: 'File size must be less than 5MB'
    };
  }
  
  return { isValid: true };
};

// Session persistence helpers
export const clearAuthData = () => {
  // Clear any cached auth data
  localStorage.removeItem('supabase.auth.token');
  sessionStorage.clear();
};

export const getStoredSession = async () => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    return session;
  } catch (error) {
    console.error('Error getting stored session:', error);
    return null;
  }
};

// Error message helpers
export const getAuthErrorMessage = (error: any): string => {
  if (!error) return 'An unknown error occurred';
  
  const message = error.message || error.error_description || error.toString();
  
  // Map common Supabase errors to user-friendly messages
  const errorMap: Record<string, string> = {
    'Invalid login credentials': 'Invalid email or password',
    'Email not confirmed': 'Please check your email and click the confirmation link',
    'User already registered': 'An account with this email already exists',
    'Password should be at least 6 characters': 'Password must be at least 6 characters long',
    'Unable to validate email address: invalid format': 'Please enter a valid email address',
    'Database error saving new user': 'Registration failed. Please try again.',
    'User not found': 'No account found with this email address'
  };
  
  return errorMap[message] || message;
};

// Cross-device session sync
export const syncSessionAcrossDevices = async () => {
  try {
    // Refresh the session to ensure it's valid across devices
    const { data: { session }, error } = await supabase.auth.refreshSession();
    
    if (error) {
      console.error('Error syncing session:', error);
      return false;
    }
    
    return !!session;
  } catch (error) {
    console.error('Error in syncSessionAcrossDevices:', error);
    return false;
  }
};

// Network status detection
export const isOnline = (): boolean => {
  return navigator.onLine;
};

// Retry mechanism for failed requests
export const retryAuthOperation = async <T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: any;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
  }
  
  throw lastError;
};