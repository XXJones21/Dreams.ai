import { useState, useEffect } from 'react';
import { User, Session } from '@supabase/supabase-js';
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
    // Get initial session
    const getInitialSession = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('Error getting initial session:', error);
          setAuthState(prev => ({ ...prev, loading: false, error: error.message }));
          return;
        }

        if (session?.user) {
          // Load user profile
          const { data: profile, error: profileError } = await getProfile(session.user.id);
          
          if (profileError && profileError.message !== 'Profile not found') {
            console.error('Error loading profile:', profileError);
          }

          setAuthState({
            user: session.user,
            session,
            profile: profile || null,
            loading: false,
            error: null
          });
        } else {
          setAuthState(prev => ({ ...prev, loading: false }));
        }
      } catch (err) {
        console.error('Error in getInitialSession:', err);
        setAuthState(prev => ({ ...prev, loading: false, error: 'Failed to initialize auth' }));
      }
    };

    getInitialSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email);

        if (session?.user) {
          // Load user profile
          const { data: profile, error: profileError } = await getProfile(session.user.id);
          
          if (profileError && profileError.message !== 'Profile not found') {
            console.error('Error loading profile after auth change:', profileError);
          }

          setAuthState({
            user: session.user,
            session,
            profile: profile || null,
            loading: false,
            error: null
          });
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