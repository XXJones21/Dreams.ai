import React, { useState, useEffect } from 'react';
import { User, Mail, Calendar, MessageSquare, Edit, Camera, LogOut, Home, Library, Sparkles, Brain, AlertCircle, RefreshCw } from 'lucide-react';
import { useAuthContext } from '../auth/AuthProvider';
import { signOut } from '../../lib/supabase';
import CosmicBackground from '../CosmicBackground';

const ProfilePage: React.FC = () => {
  const { user, profile, loading, error, refreshProfile, isAuthenticated } = useAuthContext();
  const [retryCount, setRetryCount] = useState(0);

  // Redirect if not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      window.location.href = '/';
    }
  }, [loading, isAuthenticated]);

  const handleSignOut = async () => {
    try {
      const { error } = await signOut();
      if (!error) {
        window.location.href = '/';
      }
    } catch (err) {
      console.error('Sign out error:', err);
      // Force redirect anyway
      window.location.href = '/';
    }
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    refreshProfile();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const calculateAge = (dateOfBirth: string) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black-marble overflow-hidden">
        <CosmicBackground />
        <div className="relative z-10 min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin w-12 h-12 border-4 border-brass border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-stardust-silver">Loading profile...</p>
            {retryCount > 0 && (
              <p className="text-stardust-silver/60 text-sm mt-2">
                Attempt {retryCount + 1}
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-black-marble overflow-hidden">
        <CosmicBackground />
        <div className="relative z-10 min-h-screen flex items-center justify-center">
          <div className="glass-card p-8 text-center max-w-md">
            <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-2xl font-cinzel font-bold text-stardust-silver mb-4">
              Authentication Required
            </h2>
            <p className="text-stardust-silver/70 mb-6">
              Please sign in to access your profile.
            </p>
            <a href="/" className="marble-button block w-full">
              <span className="relative z-10 text-brass font-inter font-medium">
                Return Home
              </span>
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-black-marble overflow-hidden">
        <CosmicBackground />
        <div className="relative z-10 min-h-screen flex items-center justify-center">
          <div className="glass-card p-8 text-center max-w-md">
            <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-2xl font-cinzel font-bold text-stardust-silver mb-4">
              Profile Loading Issue
            </h2>
            <p className="text-stardust-silver/70 mb-6">
              {error || 'Unable to load your profile. This might be because your profile is still being created.'}
            </p>
            <div className="space-y-4">
              <button
                onClick={handleRetry}
                className="marble-button flex items-center space-x-2 w-full justify-center"
              >
                <RefreshCw className="w-4 h-4" />
                <span className="relative z-10 text-brass font-inter font-medium">
                  Try Again
                </span>
              </button>
              <a href="/" className="glass-button block w-full">
                <span className="relative z-10 text-stardust-silver font-inter font-medium">
                  Return Home
                </span>
              </a>
              <button
                onClick={handleSignOut}
                className="glass-button w-full"
              >
                <span className="relative z-10 text-stardust-silver font-inter font-medium">
                  Sign Out
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black-marble overflow-hidden">
      <CosmicBackground />
      
      {/* Header */}
      <header className="relative z-50 w-full border-b border-brass/20">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="logo-container flex items-center space-x-3">
              <div className="relative">
                <Brain className="text-brass w-8 h-8" />
                <Sparkles className="absolute -top-1 -right-1 text-brass w-4 h-4" />
              </div>
              <div>
                <a href="/" className="text-brass text-2xl font-cinzel font-bold tracking-wider">
                  DREAMS.AI
                </a>
                <div className="logo-underline"></div>
              </div>
            </div>

            {/* Navigation */}
            <div className="hidden md:flex items-center space-x-6">
              <a
                href="/"
                className="flex items-center space-x-2 text-stardust-silver hover:text-brass transition-colors font-inter font-medium"
              >
                <Home className="w-5 h-5" />
                <span>Home</span>
              </a>
              <div className="flex items-center space-x-2 text-brass font-inter font-medium">
                <Library className="w-5 h-5" />
                <span>Library</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-4">
              <button
                onClick={handleSignOut}
                className="glass-button flex items-center space-x-2"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden md:inline">Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Profile Content */}
      <div className="relative z-10 container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="glass-card p-8">
            {/* Profile Header */}
            <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8 mb-8">
              {/* Profile Picture */}
              <div className="relative">
                {profile.profile_picture_url ? (
                  <img
                    src={profile.profile_picture_url}
                    alt={profile.full_name}
                    className="w-32 h-32 rounded-full object-cover border-4 border-brass"
                  />
                ) : (
                  <div className="w-32 h-32 rounded-full bg-black-marble/50 border-4 border-brass/30 flex items-center justify-center">
                    <User className="w-16 h-16 text-brass/50" />
                  </div>
                )}
                <button className="absolute bottom-2 right-2 w-8 h-8 bg-brass rounded-full flex items-center justify-center text-black-marble hover:bg-stardust-silver transition-colors">
                  <Camera className="w-4 h-4" />
                </button>
              </div>

              {/* Profile Info */}
              <div className="flex-1 text-center md:text-left">
                <h2 className="text-3xl font-cinzel font-bold text-stardust-silver mb-2">
                  {profile.full_name}
                </h2>
                <p className="text-brass font-inter mb-4">
                  Member since {formatDate(profile.created_at)}
                </p>
                {profile.bio && (
                  <p className="text-stardust-silver/80 font-inter leading-relaxed">
                    {profile.bio}
                  </p>
                )}
              </div>

              {/* Edit Button */}
              <button className="marble-button flex items-center space-x-2">
                <Edit className="w-4 h-4" />
                <span className="relative z-10 text-brass font-inter font-medium">
                  Edit Profile
                </span>
              </button>
            </div>

            {/* Profile Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Email */}
              <div className="glass-card p-6">
                <div className="flex items-center space-x-3 mb-2">
                  <Mail className="w-5 h-5 text-brass" />
                  <h3 className="text-lg font-cinzel font-semibold text-stardust-silver">
                    Email
                  </h3>
                </div>
                <p className="text-stardust-silver/80 font-inter">
                  {profile.email}
                </p>
              </div>

              {/* Age */}
              <div className="glass-card p-6">
                <div className="flex items-center space-x-3 mb-2">
                  <Calendar className="w-5 h-5 text-brass" />
                  <h3 className="text-lg font-cinzel font-semibold text-stardust-silver">
                    Age
                  </h3>
                </div>
                <p className="text-stardust-silver/80 font-inter">
                  {calculateAge(profile.date_of_birth)} years old
                </p>
              </div>

              {/* Bio Section */}
              {profile.bio && (
                <div className="glass-card p-6 md:col-span-2">
                  <div className="flex items-center space-x-3 mb-2">
                    <MessageSquare className="w-5 h-5 text-brass" />
                    <h3 className="text-lg font-cinzel font-semibold text-stardust-silver">
                      About
                    </h3>
                  </div>
                  <p className="text-stardust-silver/80 font-inter leading-relaxed">
                    {profile.bio}
                  </p>
                </div>
              )}
            </div>

            {/* Dreams Library Section */}
            <div className="mt-8 pt-8 border-t border-brass/20">
              <h3 className="text-xl font-cinzel font-bold text-stardust-silver mb-4 flex items-center space-x-2">
                <Library className="w-6 h-6 text-brass" />
                <span>Your Dreams Library</span>
              </h3>
              <div className="glass-card p-6 text-center">
                <div className="text-stardust-silver/60 mb-4">
                  <Sparkles className="w-12 h-12 mx-auto mb-2" />
                  <p className="font-inter">No dreams created yet</p>
                </div>
                <a href="/" className="marble-button">
                  <span className="relative z-10 text-brass font-inter font-medium">
                    Create Your First Dream
                  </span>
                </a>
              </div>
            </div>

            {/* Account Actions */}
            <div className="mt-8 pt-8 border-t border-brass/20">
              <h3 className="text-xl font-cinzel font-bold text-stardust-silver mb-4">
                Account Settings
              </h3>
              <div className="flex flex-wrap gap-4">
                <button className="glass-button">
                  <span className="relative z-10 text-stardust-silver font-inter font-medium">
                    Change Password
                  </span>
                </button>
                <button className="glass-button">
                  <span className="relative z-10 text-stardust-silver font-inter font-medium">
                    Privacy Settings
                  </span>
                </button>
                <button className="glass-button text-red-400 border-red-400/30 hover:border-red-400">
                  <span className="relative z-10 font-inter font-medium">
                    Delete Account
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;