import React, { ReactNode } from 'react';
import { useAuthContext } from './AuthProvider';
import { Loader2, Lock } from 'lucide-react';

interface ProtectedRouteProps {
  children: ReactNode;
  requireProfile?: boolean;
  fallback?: ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requireProfile = false,
  fallback 
}) => {
  const { loading, isAuthenticated, isProfileComplete } = useAuthContext();

  if (loading) {
    return (
      <div className="min-h-screen bg-black-marble flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-brass mx-auto mb-4" />
          <p className="text-stardust-silver">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return fallback || (
      <div className="min-h-screen bg-black-marble flex items-center justify-center">
        <div className="glass-card p-8 text-center max-w-md">
          <Lock className="w-12 h-12 text-brass mx-auto mb-4" />
          <h2 className="text-2xl font-cinzel font-bold text-stardust-silver mb-4">
            Authentication Required
          </h2>
          <p className="text-stardust-silver/70 mb-6">
            Please sign in to access this page.
          </p>
          <a href="/" className="marble-button">
            <span className="relative z-10 text-brass font-inter font-medium">
              Go to Home
            </span>
          </a>
        </div>
      </div>
    );
  }

  if (requireProfile && !isProfileComplete) {
    return fallback || (
      <div className="min-h-screen bg-black-marble flex items-center justify-center">
        <div className="glass-card p-8 text-center max-w-md">
          <h2 className="text-2xl font-cinzel font-bold text-stardust-silver mb-4">
            Profile Setup Required
          </h2>
          <p className="text-stardust-silver/70 mb-6">
            Please complete your profile to continue.
          </p>
          <a href="/profile/setup" className="marble-button">
            <span className="relative z-10 text-brass font-inter font-medium">
              Complete Profile
            </span>
          </a>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;