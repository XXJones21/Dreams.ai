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
          console.warn('[useAuth] ⚠️ Auth loading timed out, setting loading to false');
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
        console.log('[useAuth] 🔄 Initializing authentication...');
        setLoadingTimeout(); // Start timeout
        
        const { data: { session }, error } = await supabase.auth.getSession();
        console.log('[useAuth] 📡 getSession result:', { session, error });
        
        clearLoadingTimeout(); // Clear timeout since we got a response
        
        if (!mounted) {
          console.log('[useAuth] ⛔ Not mounted, aborting initializeAuth');
          return;
        }
        
        if (error) {
          console.error('[useAuth] ❌ Session error:', error);
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
          console.log('[useAuth] ✅ Session found for user:', session.user.email);
          
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
            console.log('[useAuth] 🔍 Calling ensureProfile for user:', session.user.email);
            const { data: profile, error: profileError } = await ensureProfile(session.user);
            console.log('[useAuth] 📝 ensureProfile result:', { profile, profileError });
            
            if (mounted) {
              setAuthState(prev => ({
                ...prev,
                profile: profile || null,
                error: profileError ? `[useAuth] Profile issue: ${profileError.message}` : null
              }));
              if (profileError) {
                console.warn('[useAuth] ⚠️ Profile error after ensureProfile:', profileError);
              }
            }
          } catch (profileErr: any) {
            console.warn('[useAuth] ⚠️ Profile handling failed:', profileErr);
            // Don't update loading state here since user is already authenticated
          }
        } else {
          console.log('[useAuth] ℹ️ No active session found');
          setAuthState({
            user: null,
            session: null,
            profile: null,
            loading: false,
            error: null
          });
        }
      } catch (err: any) {
        console.error('[useAuth] ❌ Auth initialization error:', err);
        clearLoadingTimeout();
        if (mounted) {
          setAuthState({
            user: null,
            session: null,
            profile: null,
            loading: false,
            error: '[useAuth] Failed to initialize authentication'
          });
        }
      }
    };

    initializeAuth();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, session: Session | null) => {
        if (!mounted) return;
        
        console.log('[useAuth] 🔄 Auth state changed:', event, session?.user?.email);

        if (session?.user) {
          console.log('[useAuth] ✅ User authenticated via state change:', session.user.email);
          
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
            console.log('[useAuth] 🔍 Calling ensureProfile after auth state change for user:', session.user.email);
            const { data: profile, error: profileError } = await ensureProfile(session.user);
            console.log('[useAuth] 📝 ensureProfile result after state change:', { profile, profileError });
            
            if (mounted) {
              setAuthState(prev => ({
                ...prev,
                profile: profile || null,
                error: profileError ? `[useAuth] Profile issue: ${profileError.message}` : null
              }));
              if (profileError) {
                console.warn('[useAuth] ⚠️ Profile error after ensureProfile (state change):', profileError);
              }
            }
          } catch (profileErr: any) {
            console.warn('[useAuth] ⚠️ Profile handling failed after auth change:', profileErr);
          }
        } else {
          console.log('[useAuth] ℹ️ User signed out');
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
      console.log('[useAuth] 🧹 Cleanup: unsubscribed and cleared timeout');
    };
  }, []);

  const refreshProfile = async () => {
    if (!authState.user) {
      console.warn('[useAuth] Cannot refresh profile: no authenticated user');
      return;
    }

    try {
      console.log('[useAuth] 🔄 Refreshing profile for user:', authState.user.email);
      
      const { data: profile, error } = await getProfile(authState.user.id);
      console.log('[useAuth] 📝 getProfile result:', { profile, error });
      
      if (error) {
        console.error('[useAuth] ❌ Error refreshing profile:', error);
        setAuthState(prev => ({ 
          ...prev, 
          error: `[useAuth] Profile refresh failed: ${error.message}` 
        }));
        return;
      }

      console.log('[useAuth] ✅ Profile refreshed successfully');
      setAuthState(prev => ({ 
        ...prev, 
        profile, 
        error: null 
      }));
    } catch (err: any) {
      console.error('[useAuth] ❌ Error in refreshProfile:', err);
      setAuthState(prev => ({ 
        ...prev, 
        error: `[useAuth] Profile refresh failed: ${err.message}` 
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