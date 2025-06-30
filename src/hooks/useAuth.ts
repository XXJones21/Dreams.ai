import { useState, useEffect } from 'react';
import { User, Session, AuthChangeEvent } from '@supabase/supabase-js';
import { supabase, Profile, getProfile, ensureProfile } from '../lib/supabase';

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
    let timeoutId: NodeJS.Timeout;

    // CRITICAL FIX: Set a maximum loading time to prevent infinite loading
    const setLoadingTimeout = () => {
      timeoutId = setTimeout(() => {
        if (mounted) {
          console.warn('⚠️ Auth loading timed out, setting loading to false');
          setAuthState(prev => ({ ...prev, loading: false }));
        }
      }, 5000); // 5 second maximum loading time
    };

    const clearLoadingTimeout = () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };

    const initializeAuth = async () => {
      try {
        console.log('🔄 Initializing authentication...');
        setLoadingTimeout(); // Start timeout
        
        const { data: { session }, error } = await supabase.auth.getSession();
        
        clearLoadingTimeout(); // Clear timeout since we got a response
        
        if (!mounted) return;
        
        if (error) {
          console.error('❌ Session error:', error);
          setAuthState({
            user: null,
            session: null,
            profile: null,
            loading: false,
            error: error.message
          });
          return;
        }

        if (session?.user) {
          console.log('✅ Session found for user:', session.user.email);
          
          // Set user immediately, then handle profile separately
          setAuthState({
            user: session.user,
            session,
            profile: null,
            loading: false, // CRITICAL: Set loading to false immediately when we have a user
            error: null
          });

          // Handle profile loading in background
          try {
            const { data: profile, error: profileError } = await ensureProfile(session.user);
            
            if (mounted) {
              setAuthState(prev => ({
                ...prev,
                profile: profile || null,
                error: profileError ? `Profile issue: ${profileError.message}` : null
              }));
            }
          } catch (profileErr: any) {
            console.warn('⚠️ Profile handling failed:', profileErr);
            // Don't update loading state here since user is already authenticated
          }
        } else {
          console.log('ℹ️ No active session found');
          setAuthState({
            user: null,
            session: null,
            profile: null,
            loading: false,
            error: null
          });
        }
      } catch (err: any) {
        console.error('❌ Auth initialization error:', err);
        clearLoadingTimeout();
        if (mounted) {
          setAuthState({
            user: null,
            session: null,
            profile: null,
            loading: false,
            error: 'Failed to initialize authentication'
          });
        }
      }
    };

    initializeAuth();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, session: Session | null) => {
        if (!mounted) return;
        
        console.log('🔄 Auth state changed:', event, session?.user?.email);

        if (session?.user) {
          console.log('✅ User authenticated via state change:', session.user.email);
          
          // CRITICAL: Set user and loading false immediately
          setAuthState({
            user: session.user,
            session,
            profile: null,
            loading: false, // Don't keep loading true
            error: null
          });

          // Handle profile in background
          try {
            const { data: profile, error: profileError } = await ensureProfile(session.user);
            
            if (mounted) {
              setAuthState(prev => ({
                ...prev,
                profile: profile || null,
                error: profileError ? `Profile issue: ${profileError.message}` : null
              }));
            }
          } catch (profileErr: any) {
            console.warn('⚠️ Profile handling failed after auth change:', profileErr);
          }
        } else {
          console.log('ℹ️ User signed out');
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
      clearLoadingTimeout();
      subscription.unsubscribe();
    };
  }, []);

  const refreshProfile = async () => {
    if (!authState.user) {
      console.warn('Cannot refresh profile: no authenticated user');
      return;
    }

    try {
      console.log('🔄 Refreshing profile for user:', authState.user.email);
      
      const { data: profile, error } = await getProfile(authState.user.id);
      
      if (error) {
        console.error('❌ Error refreshing profile:', error);
        setAuthState(prev => ({ 
          ...prev, 
          error: `Profile refresh failed: ${error.message}` 
        }));
        return;
      }

      console.log('✅ Profile refreshed successfully');
      setAuthState(prev => ({ 
        ...prev, 
        profile, 
        error: null 
      }));
    } catch (err: any) {
      console.error('❌ Error in refreshProfile:', err);
      setAuthState(prev => ({ 
        ...prev, 
        error: `Profile refresh failed: ${err.message}` 
      }));
    }
  };

  return {
    ...authState,
    refreshProfile,
    isAuthenticated: !!authState.user,
    isProfileComplete: !!authState.profile
  };
};