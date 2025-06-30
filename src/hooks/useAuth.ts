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

    // Simple initialization without timeouts or retries
    const initializeAuth = async () => {
      try {
        console.log('🔄 Initializing authentication...');
        
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (!mounted) return;
        
        if (error) {
          console.error('❌ Session error:', error);
          setAuthState(prev => ({ ...prev, loading: false, error: error.message }));
          return;
        }

        if (session?.user) {
          console.log('✅ Session found, loading profile...');
          
          // Load profile without timeout
          try {
            const { data: profile, error: profileError } = await getProfile(session.user.id);
            
            if (!mounted) return;
            
            if (profileError && profileError.message !== 'Profile not found') {
              console.warn('⚠️ Profile loading failed, but continuing with authentication:', profileError.message);
            }

            setAuthState({
              user: session.user,
              session,
              profile: profile || null,
              loading: false,
              error: null
            });
          } catch (profileErr: any) {
            console.warn('⚠️ Profile loading exception, but continuing with authentication:', profileErr);
            if (mounted) {
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
        console.error('❌ Auth initialization error:', err);
        if (mounted) {
          setAuthState(prev => ({ 
            ...prev, 
            loading: false, 
            error: 'Failed to initialize authentication' 
          }));
        }
      }
    };

    initializeAuth();

    // Listen for auth changes - simplified
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, session: Session | null) => {
        if (!mounted) return;
        
        console.log('🔄 Auth state changed:', event, session?.user?.email);

        if (session?.user) {
          // Load profile for authenticated user
          try {
            const { data: profile, error: profileError } = await getProfile(session.user.id);
            
            if (!mounted) return;
            
            if (profileError && profileError.message !== 'Profile not found') {
              console.warn('⚠️ Profile loading failed after auth change:', profileError.message);
            }

            setAuthState({
              user: session.user,
              session,
              profile: profile || null,
              loading: false,
              error: null
            });
          } catch (profileErr: any) {
            console.warn('⚠️ Profile loading exception after auth change:', profileErr);
            if (mounted) {
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
          // User signed out
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
      const { data: profile, error } = await getProfile(authState.user.id);
      
      if (error) {
        console.error('Error refreshing profile:', error);
        return;
      }

      setAuthState(prev => ({ ...prev, profile }));
    } catch (err) {
      console.error('Error in refreshProfile:', err);
    }
  };

  return {
    ...authState,
    refreshProfile,
    isAuthenticated: !!authState.user,
    isProfileComplete: !!authState.profile
  };
};