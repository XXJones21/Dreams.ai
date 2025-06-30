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

    // Simplified initialization - no race conditions
    const initializeAuth = async () => {
      try {
        console.log('🔄 Initializing authentication...');
        
        const { data: { session }, error } = await supabase.auth.getSession();
        
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
          
          // Handle profile loading - keep loading true until complete
          try {
            const { data: profile, error: profileError } = await ensureProfile(session.user);
            
            if (mounted) {
              setAuthState({
                user: session.user,
                session,
                profile: profile || null,
                loading: false,
                error: profileError ? `Profile issue: ${profileError.message}` : null
              });
            }
          } catch (profileErr: any) {
            console.warn('⚠️ Profile handling failed:', profileErr);
            if (mounted) {
              // User is authenticated even if profile has issues
              setAuthState({
                user: session.user,
                session,
                profile: null,
                loading: false,
                error: `Profile loading failed: ${profileErr.message}`
              });
            }
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

    // Listen for auth changes with proper state management
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, session: Session | null) => {
        if (!mounted) return;
        
        console.log('🔄 Auth state changed:', event, session?.user?.email);

        if (session?.user) {
          console.log('✅ User authenticated via state change:', session.user.email);
          
          // Set loading state while handling profile
          setAuthState(prev => ({
            ...prev,
            user: session.user,
            session,
            loading: true,
            error: null
          }));

          // Handle profile loading
          try {
            const { data: profile, error: profileError } = await ensureProfile(session.user);
            
            if (mounted) {
              setAuthState({
                user: session.user,
                session,
                profile: profile || null,
                loading: false,
                error: profileError ? `Profile issue: ${profileError.message}` : null
              });
            }
          } catch (profileErr: any) {
            console.warn('⚠️ Profile handling failed after auth change:', profileErr);
            if (mounted) {
              setAuthState({
                user: session.user,
                session,
                profile: null,
                loading: false,
                error: `Profile loading failed: ${profileErr.message}`
              });
            }
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
      
      // Set loading state for profile refresh
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      const { data: profile, error } = await getProfile(authState.user.id);
      
      if (error) {
        console.error('❌ Error refreshing profile:', error);
        setAuthState(prev => ({ 
          ...prev, 
          loading: false, 
          error: `Profile refresh failed: ${error.message}` 
        }));
        return;
      }

      console.log('✅ Profile refreshed successfully');
      setAuthState(prev => ({ 
        ...prev, 
        profile, 
        loading: false, 
        error: null 
      }));
    } catch (err: any) {
      console.error('❌ Error in refreshProfile:', err);
      setAuthState(prev => ({ 
        ...prev, 
        loading: false, 
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