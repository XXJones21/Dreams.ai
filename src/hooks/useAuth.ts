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
    let mounted = true;
    let timeoutId: NodeJS.Timeout;

    // Get initial session with longer timeout
    const getInitialSession = async () => {
      try {
        // Set a longer timeout to prevent premature failures
        timeoutId = setTimeout(() => {
          if (mounted) {
            console.warn('⚠️ Auth initialization timed out after 30 seconds');
            setAuthState(prev => ({ 
              ...prev, 
              loading: false, 
              error: 'Authentication service is taking too long to respond. Please check your connection and refresh the page.' 
            }));
          }
        }, 30000); // Increased from 15 seconds to 30 seconds

        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (!mounted) return;
        
        clearTimeout(timeoutId);
        
        if (error) {
          console.error('Error getting initial session:', error);
          setAuthState(prev => ({ ...prev, loading: false, error: error.message }));
          return;
        }

        if (session?.user) {
          // Load user profile with longer timeout and better error handling
          try {
            const { data: profile, error: profileError } = await getProfile(session.user.id);
            
            if (!mounted) return;
            
            if (profileError) {
              console.error('Error loading profile:', profileError);
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
          setAuthState(prev => ({ ...prev, loading: false }));
        }
      } catch (err: any) {
        console.error('Error in getInitialSession:', err);
        if (mounted) {
          clearTimeout(timeoutId);
          let errorMessage = 'Failed to initialize authentication';
          
          if (err.message?.includes('timeout')) {
            errorMessage = 'Connection timed out. Please check your internet connection and refresh the page.';
          } else if (err.message?.includes('fetch')) {
            errorMessage = 'Unable to connect to authentication service. Please check your connection.';
          }
          
          setAuthState(prev => ({ ...prev, loading: false, error: errorMessage }));
        }
      }
    };

    getInitialSession();

    // Listen for auth changes with better error handling
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (!mounted) return;
        
        console.log('Auth state changed:', event, session?.user?.email);

        if (session?.user) {
          // Load user profile with better error handling
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
      clearTimeout(timeoutId);
      subscription.unsubscribe();
    };
  }, []);

  const refreshProfile = async () => {
    if (!authState.user) return;

    try {
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