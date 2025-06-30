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

    // Simple initialization
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
          
          // Set authenticated state immediately, then load profile
          setAuthState({
            user: session.user,
            session,
            profile: null,
            loading: false, // Set loading to false immediately
            error: null
          });

          // Load profile in background
          try {
            const { data: profile, error: profileError } = await getProfile(session.user.id);
            
            if (mounted && !profileError) {
              setAuthState(prev => ({
                ...prev,
                profile
              }));
            }
          } catch (profileErr) {
            console.warn('⚠️ Profile loading failed, but user is authenticated:', profileErr);
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

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, session: Session | null) => {
        if (!mounted) return;
        
        console.log('🔄 Auth state changed:', event, session?.user?.email);

        if (session?.user) {
          console.log('✅ User authenticated via state change:', session.user.email);
          
          // Set authenticated state immediately
          setAuthState({
            user: session.user,
            session,
            profile: null,
            loading: false, // Always set loading to false when we have a user
            error: null
          });

          // Load profile in background
          try {
            const { data: profile, error: profileError } = await getProfile(session.user.id);
            
            if (mounted && !profileError) {
              setAuthState(prev => ({
                ...prev,
                profile
              }));
            }
          } catch (profileErr) {
            console.warn('⚠️ Profile loading failed after auth change:', profileErr);
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