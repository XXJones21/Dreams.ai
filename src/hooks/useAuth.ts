import { useState, useEffect } from 'react';
import { User, Session, AuthChangeEvent } from '@supabase/supabase-js';
import { supabase, Profile, getProfile } from '../lib/supabase';

interface AuthState {
  user: User | null;
  session: Session | null;
  profile: Profile | null;
  loading: boolean;
  error: string | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    session: null,
    profile: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    let mounted = true;
    let retryCount = 0;
    const maxRetries = 3;

    // REMOVED: All timeout logic that was causing authentication loops
    // Get initial session with retry logic but NO timeouts
    const getInitialSession = async () => {
      try {
        console.log('🔄 Initializing authentication...');
        
        // Let getSession complete naturally without timeout constraints
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (!mounted) return;
        
        if (error) {
          console.error('Error getting initial session:', error);
          
          // Retry logic for network issues, but no timeout loops
          if (retryCount < maxRetries && (error.message?.includes('fetch') || error.message?.includes('network'))) {
            retryCount++;
            console.log(`🔄 Retrying authentication (${retryCount}/${maxRetries})...`);
            setTimeout(() => getInitialSession(), 2000 * retryCount); // Exponential backoff
            return;
          }
          
          setAuthState(prev => ({ ...prev, loading: false, error: error.message }));
          return;
        }

        if (session?.user) {
          console.log('✅ Session found, loading profile...');
          
          // Load user profile with graceful error handling - NO TIMEOUTS
          try {
            const { data: profile, error: profileError } = await getProfile(session.user.id);
            
            if (!mounted) return;
            
            if (profileError) {
              console.error('Profile loading failed:', profileError);
              // Don't treat profile errors as fatal - user might not have a profile yet
              if (profileError.message !== 'Profile not found') {
                console.warn('Profile loading failed, but continuing with authentication:', profileError.message);
              }
            }

            setAuthState({
              user: session.user,
              session,
              profile: profile || null,
              loading: false,
              error: null
            });
          } catch (profileErr: any) {
            console.error('Profile loading exception:', profileErr);
            if (mounted) {
              // Don't fail authentication if profile loading fails
              setAuthState({
                user: session.user,
                session,
                profile: null,
                loading: false,
                error: null
              });
            }
          }
        } else {
          console.log('ℹ️ No active session found');
          setAuthState(prev => ({ ...prev, loading: false }));
        }
      } catch (err: any) {
        console.error('Error in getInitialSession:', err);
        if (mounted) {
          // Retry for network errors, but don't create timeout loops
          if (retryCount < maxRetries && (err.message?.includes('fetch') || err.message?.includes('network'))) {
            retryCount++;
            console.log(`🔄 Retrying authentication due to network error (${retryCount}/${maxRetries})...`);
            setTimeout(() => getInitialSession(), 2000 * retryCount);
            return;
          }
          
          let errorMessage = 'Failed to initialize authentication';
          
          if (err.message?.includes('fetch')) {
            errorMessage = 'Unable to connect to authentication service. Please check your connection.';
          }
          
          setAuthState(prev => ({ ...prev, loading: false, error: errorMessage }));
        }
      }
    };

    getInitialSession();

    // Listen for auth changes with improved error handling - NO TIMEOUTS
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, session: Session | null) => {
        if (!mounted) return;
        
        console.log('🔄 Auth state changed:', event, session?.user?.email);

        if (session?.user) {
          // Force a getUser call after auth state change for debugging
          try {
            const userResult = await supabase.auth.getUser();
            console.log('🔍 Forced getUser result after auth state change:', userResult);
          } catch (err) {
            console.error('❌ Error in forced getUser after auth state change:', err);
          }
          // Load user profile with graceful error handling - NO TIMEOUTS
          try {
            const { data: profile, error: profileError } = await getProfile(session.user.id);
            
            if (!mounted) return;
            
            if (profileError) {
              console.error('Error loading profile after auth change:', profileError);
              // Don't treat profile errors as fatal
              if (profileError.message !== 'Profile not found') {
                console.warn('Profile loading failed after auth change, but continuing:', profileError.message);
              }
            }

            setAuthState({
              user: session.user,
              session,
              profile: profile || null,
              loading: false,
              error: null
            });
          } catch (profileErr: any) {
            console.error('Profile loading exception after auth change:', profileErr);
            if (mounted) {
              // Don't fail authentication if profile loading fails
              setAuthState({
                user: session.user,
                session,
                profile: null,
                loading: false,
                error: null
              });
            }
          }
        } else {
          setAuthState({
            user: null,
            session: null,
            profile: null,
            loading: false,
            error: null
          });
        }
      }
    );

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const refreshProfile = async () => {
    if (!authState.user) return;

    try {
      // NO TIMEOUT - let profile refresh complete naturally
      const { data: profile, error } = await getProfile(authState.user.id);
      
      if (error) {
        console.error('Error refreshing profile:', error);
        // Don't throw error, just log it
        return;
      }

      setAuthState(prev => ({ ...prev, profile }));
    } catch (err) {
      console.error('Error in refreshProfile:', err);
      // Don't throw error, just log it
    }
  };

  return {
    ...authState,
    refreshProfile,
    isAuthenticated: !!authState.user,
    isProfileComplete: !!authState.profile
  };
};