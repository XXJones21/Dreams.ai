import React, { useState } from 'react';
import { X, Mail, Lock, Eye, EyeOff, User, Calendar, FileImage, MessageSquare, Upload, AlertTriangle } from 'lucide-react';
import { signIn, signUp, createProfile, uploadProfilePicture, resetPassword, testSupabaseConnection } from '../../lib/supabase';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

type AuthMode = 'login' | 'register' | 'forgot-password';

interface FormErrors {
  fullName?: string;
  email?: string;
  password?: string;
  dateOfBirth?: string;
  profilePicture?: string;
  bio?: string;
  general?: string;
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [mode, setMode] = useState<AuthMode>('login');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [connectionStatus, setConnectionStatus] = useState<'unknown' | 'testing' | 'connected' | 'failed'>('unknown');

  // Login form data
  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });

  // Registration form data
  const [registerData, setRegisterData] = useState({
    fullName: '',
    email: '',
    password: '',
    dateOfBirth: '',
    bio: ''
  });

  // Forgot password data
  const [forgotEmail, setForgotEmail] = useState('');

  // Profile picture
  const [profilePicture, setProfilePicture] = useState<File | null>(null);
  const [profilePicturePreview, setProfilePicturePreview] = useState<string>('');

  // Test connection when modal opens
  React.useEffect(() => {
    if (isOpen && connectionStatus === 'unknown') {
      testConnection();
    }
  }, [isOpen]);

  const testConnection = async () => {
    setConnectionStatus('testing');
    const result = await testSupabaseConnection();
    setConnectionStatus(result.success ? 'connected' : 'failed');
    
    if (!result.success) {
      setError(result.error || 'Connection failed');
    }
  };

  // Validation functions
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePassword = (password: string): boolean => {
    const hasMinLength = password.length >= 6;
    const hasNumber = /\d/.test(password);
    return hasMinLength && hasNumber;
  };

  const validateAge = (dateOfBirth: string): boolean => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    const age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      return age - 1 >= 13;
    }
    return age >= 13;
  };

  const validateFile = (file: File): string | null => {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (!allowedTypes.includes(file.type)) {
      return 'Please upload a valid image file (JPG, JPEG, or PNG)';
    }

    if (file.size > maxSize) {
      return 'File size must be less than 5MB';
    }

    return null;
  };

  const resetForm = () => {
    setLoginData({ email: '', password: '' });
    setRegisterData({ fullName: '', email: '', password: '', dateOfBirth: '', bio: '' });
    setForgotEmail('');
    setProfilePicture(null);
    setProfilePicturePreview('');
    setError('');
    setErrors({});
    setIsSuccess(false);
    setShowPassword(false);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleModeChange = (newMode: AuthMode) => {
    setMode(newMode);
    setError('');
    setErrors({});
    setIsSuccess(false);
  };

  // Login handlers
  const handleLoginChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setLoginData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginData.email.trim() || !loginData.password.trim()) return;
    
    setIsLoading(true);
    setError('');

    try {
      const { data, error: signInError } = await signIn(loginData.email, loginData.password);
      
      if (signInError) {
        setError(signInError.message);
        setIsLoading(false);
        return;
      }

      if (data.user) {
        setIsSuccess(true);
        onSuccess?.();
        setTimeout(() => {
          handleClose();
          // Redirect to main page after successful login
          window.location.href = '/';
        }, 1000);
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Registration handlers
  const handleRegisterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setRegisterData(prev => ({ ...prev, [name]: value }));
    
    // Real-time validation
    const newErrors = { ...errors };
    switch (name) {
      case 'fullName':
        if (!value || value.trim().length < 2) {
          newErrors.fullName = 'Full name must be at least 2 characters';
        } else {
          delete newErrors.fullName;
        }
        break;
      case 'email':
        if (!value) {
          newErrors.email = 'Email is required';
        } else if (!validateEmail(value)) {
          newErrors.email = 'Please enter a valid email address';
        } else {
          delete newErrors.email;
        }
        break;
      case 'password':
        if (!value) {
          newErrors.password = 'Password is required';
        } else if (!validatePassword(value)) {
          newErrors.password = 'Password must be at least 6 characters with numbers';
        } else {
          delete newErrors.password;
        }
        break;
      case 'dateOfBirth':
        if (!value) {
          newErrors.dateOfBirth = 'Date of birth is required';
        } else if (!validateAge(value)) {
          newErrors.dateOfBirth = 'You must be at least 13 years old to register';
        } else {
          delete newErrors.dateOfBirth;
        }
        break;
      case 'bio':
        if (value && value.length > 250) {
          newErrors.bio = 'Bio must be 250 characters or less';
        } else {
          delete newErrors.bio;
        }
        break;
    }
    setErrors(newErrors);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const fileError = validateFile(file);
      if (fileError) {
        setErrors(prev => ({ ...prev, profilePicture: fileError }));
      } else {
        setErrors(prev => ({ ...prev, profilePicture: undefined }));
        setProfilePicture(file);
        const reader = new FileReader();
        reader.onload = (e) => {
          setProfilePicturePreview(e.target?.result as string);
        };
        reader.readAsDataURL(file);
      }
    }
  };

  const removeProfilePicture = () => {
    setProfilePicture(null);
    setProfilePicturePreview('');
    setErrors(prev => ({ ...prev, profilePicture: undefined }));
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Final validation
      const validationErrors: FormErrors = {};
      
      if (!registerData.fullName.trim()) validationErrors.fullName = 'Full name is required';
      if (!validateEmail(registerData.email)) validationErrors.email = 'Valid email is required';
      if (!validatePassword(registerData.password)) validationErrors.password = 'Password requirements not met';
      if (!validateAge(registerData.dateOfBirth)) validationErrors.dateOfBirth = 'Must be 13+ years old';
      if (registerData.bio && registerData.bio.length > 250) validationErrors.bio = 'Bio too long';
      if (profilePicture && validateFile(profilePicture)) validationErrors.profilePicture = validateFile(profilePicture)!;

      if (Object.keys(validationErrors).length > 0) {
        setErrors(validationErrors);
        setIsLoading(false);
        return;
      }

      // Sign up user
      const { data: authData, error: authError } = await signUp(registerData.email, registerData.password);
      
      if (authError) {
        setError(authError.message);
        setIsLoading(false);
        return;
      }

      if (!authData.user) {
        setError('Registration failed. Please try again.');
        setIsLoading(false);
        return;
      }

      // Upload profile picture if provided
      let profilePictureUrl = '';
      if (profilePicture) {
        const { data: uploadData, error: uploadError } = await uploadProfilePicture(
          authData.user.id,
          profilePicture
        );
        
        if (uploadError) {
          console.error('Profile picture upload failed:', uploadError);
        } else if (uploadData) {
          profilePictureUrl = uploadData.publicUrl;
        }
      }

      // Create profile
      const { error: profileError } = await createProfile({
        user_id: authData.user.id,
        full_name: registerData.fullName.trim(),
        email: registerData.email,
        profile_picture_url: profilePictureUrl,
        bio: registerData.bio?.trim() || null,
        date_of_birth: registerData.dateOfBirth
      });

      if (profileError) {
        setError('Profile creation failed. Please try again.');
        setIsLoading(false);
        return;
      }

      setIsSuccess(true);
      onSuccess?.();
      
      setTimeout(() => {
        handleClose();
        // Redirect to main page after successful registration
        window.location.href = '/';
      }, 2000);

    } catch (error) {
      console.error('Registration error:', error);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Forgot password handlers
  const handleForgotPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const { error: resetError } = await resetPassword(forgotEmail);
      
      if (resetError) {
        setError(resetError.message);
      } else {
        setIsSuccess(true);
      }
    } catch (error) {
      console.error('Password reset error:', error);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={handleClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="glass-card p-8">
          {/* Close Button */}
          <button
            onClick={handleClose}
            className="absolute top-4 right-4 text-stardust-silver hover:text-brass transition-colors"
          >
            <X className="w-6 h-6" />
          </button>

          {/* Connection Status */}
          {connectionStatus !== 'connected' && (
            <div className="mb-6 p-4 bg-red-500/20 border border-red-500/40 rounded-lg">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <div>
                  <div className="text-red-300 font-medium">
                    {connectionStatus === 'testing' ? 'Testing connection...' : 'Connection Failed'}
                  </div>
                  {connectionStatus === 'failed' && (
                    <div className="text-red-400 text-sm mt-1">
                      Unable to connect to Supabase. Please check your configuration.
                      <button
                        onClick={testConnection}
                        className="ml-2 text-brass hover:text-stardust-silver underline"
                      >
                        Retry
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Success State */}
          {isSuccess && (
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <User className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-cinzel font-bold text-stardust-silver mb-4">
                {mode === 'register' ? 'Registration Successful!' : 
                 mode === 'login' ? 'Welcome Back!' : 
                 'Check Your Email'}
              </h2>
              <p className="text-stardust-silver/70">
                {mode === 'register' ? 'Please check your email to verify your account. Redirecting to home...' :
                 mode === 'login' ? 'Redirecting to home page...' :
                 `We've sent a password reset link to ${forgotEmail}`}
              </p>
            </div>
          )}

          {/* Login Form */}
          {!isSuccess && mode === 'login' && (
            <>
              <h2 className="text-3xl font-cinzel font-bold text-center text-stardust-silver mb-8">
                <span className="text-brass">
                  Welcome Back
                </span>
              </h2>

              {error && (
                <div className="mb-6 p-4 bg-red-500/20 border border-red-500/40 rounded-lg text-red-300">
                  {error}
                </div>
              )}

              <form onSubmit={handleLoginSubmit} className="space-y-6">
                <div>
                  <label className="block text-stardust-silver font-inter font-medium mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
                    <input
                      type="email"
                      name="email"
                      value={loginData.email}
                      onChange={handleLoginChange}
                      className="w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 border-brass/30 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:border-brass focus:outline-none transition-colors"
                      placeholder="Enter your email"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-stardust-silver font-inter font-medium mb-2">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      name="password"
                      value={loginData.password}
                      onChange={handleLoginChange}
                      className="w-full pl-12 pr-12 py-3 bg-black-marble/50 border-2 border-brass/30 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:border-brass focus:outline-none transition-colors"
                      placeholder="Enter your password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-brass hover:text-stardust-silver transition-colors"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div className="text-right">
                  <button
                    type="button"
                    onClick={() => handleModeChange('forgot-password')}
                    className="text-brass hover:text-stardust-silver transition-colors text-sm"
                  >
                    Forgot your password?
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={isLoading || connectionStatus !== 'connected'}
                  className="w-full marble-button-large group disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="relative z-10 text-brass font-inter font-semibold tracking-wide group-hover:text-black-marble transition-colors duration-300">
                    {isLoading ? 'Signing In...' : 'Sign In'}
                  </span>
                </button>

                <p className="text-center text-stardust-silver/60 text-sm">
                  Don't have an account?{' '}
                  <button
                    type="button"
                    onClick={() => handleModeChange('register')}
                    className="text-brass hover:text-stardust-silver transition-colors"
                  >
                    Create one here
                  </button>
                </p>
              </form>
            </>
          )}

          {/* Registration Form */}
          {!isSuccess && mode === 'register' && (
            <>
              <h2 className="text-3xl font-cinzel font-bold text-center text-stardust-silver mb-8">
                <span className="text-brass">
                  Create Your Account
                </span>
              </h2>

              {error && (
                <div className="mb-6 p-4 bg-red-500/20 border border-red-500/40 rounded-lg text-red-300">
                  {error}
                </div>
              )}

              <form onSubmit={handleRegisterSubmit} className="space-y-6">
                {/* Profile Picture Upload */}
                <div className="text-center">
                  <div className="relative inline-block">
                    {profilePicturePreview ? (
                      <div className="relative">
                        <img
                          src={profilePicturePreview}
                          alt="Profile preview"
                          className="w-20 h-20 rounded-full object-cover border-2 border-brass"
                        />
                        <button
                          type="button"
                          onClick={removeProfilePicture}
                          className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white hover:bg-red-600 transition-colors"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ) : (
                      <div className="w-20 h-20 rounded-full bg-black-marble/50 border-2 border-brass/30 flex items-center justify-center">
                        <FileImage className="w-6 h-6 text-brass/50" />
                      </div>
                    )}
                  </div>
                  <div className="mt-2">
                    <label className="marble-button cursor-pointer text-sm">
                      <input
                        type="file"
                        accept=".jpg,.jpeg,.png"
                        onChange={handleFileChange}
                        className="hidden"
                      />
                      <span className="relative z-10 text-brass font-inter font-medium flex items-center space-x-1">
                        <Upload className="w-3 h-3" />
                        <span>Photo</span>
                      </span>
                    </label>
                    {errors.profilePicture && (
                      <p className="text-red-400 text-xs mt-1">{errors.profilePicture}</p>
                    )}
                  </div>
                </div>

                {/* Full Name */}
                <div>
                  <label className="block text-stardust-silver font-inter font-medium mb-2">
                    Full Name *
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
                    <input
                      type="text"
                      name="fullName"
                      value={registerData.fullName}
                      onChange={handleRegisterChange}
                      className={`w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:outline-none transition-colors ${
                        errors.fullName ? 'border-red-500' : 'border-brass/30 focus:border-brass'
                      }`}
                      placeholder="Enter your full name"
                      required
                    />
                  </div>
                  {errors.fullName && (
                    <p className="text-red-400 text-xs mt-1">{errors.fullName}</p>
                  )}
                </div>

                {/* Email */}
                <div>
                  <label className="block text-stardust-silver font-inter font-medium mb-2">
                    Email Address *
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
                    <input
                      type="email"
                      name="email"
                      value={registerData.email}
                      onChange={handleRegisterChange}
                      className={`w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:outline-none transition-colors ${
                        errors.email ? 'border-red-500' : 'border-brass/30 focus:border-brass'
                      }`}
                      placeholder="Enter your email"
                      required
                    />
                  </div>
                  {errors.email && (
                    <p className="text-red-400 text-xs mt-1">{errors.email}</p>
                  )}
                </div>

                {/* Password */}
                <div>
                  <label className="block text-stardust-silver font-inter font-medium mb-2">
                    Password *
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      name="password"
                      value={registerData.password}
                      onChange={handleRegisterChange}
                      className={`w-full pl-12 pr-12 py-3 bg-black-marble/50 border-2 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:outline-none transition-colors ${
                        errors.password ? 'border-red-500' : 'border-brass/30 focus:border-brass'
                      }`}
                      placeholder="Create a secure password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-brass hover:text-stardust-silver transition-colors"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                  <p className="text-xs text-stardust-silver/60 mt-1">
                    Min 6 chars with numbers
                  </p>
                  {errors.password && (
                    <p className="text-red-400 text-xs mt-1">{errors.password}</p>
                  )}
                </div>

                {/* Date of Birth */}
                <div>
                  <label className="block text-stardust-silver font-inter font-medium mb-2">
                    Date of Birth *
                  </label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
                    <input
                      type="date"
                      name="dateOfBirth"
                      value={registerData.dateOfBirth}
                      onChange={handleRegisterChange}
                      className={`w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 rounded-lg text-stardust-silver font-inter focus:outline-none transition-colors ${
                        errors.dateOfBirth ? 'border-red-500' : 'border-brass/30 focus:border-brass'
                      }`}
                      required
                    />
                  </div>
                  {errors.dateOfBirth && (
                    <p className="text-red-400 text-xs mt-1">{errors.dateOfBirth}</p>
                  )}
                </div>

                {/* Bio */}
                <div>
                  <label className="block text-stardust-silver font-inter font-medium mb-2">
                    Bio (Optional)
                  </label>
                  <div className="relative">
                    <MessageSquare className="absolute left-3 top-3 text-brass w-5 h-5" />
                    <textarea
                      name="bio"
                      value={registerData.bio}
                      onChange={handleRegisterChange}
                      rows={2}
                      maxLength={250}
                      className={`w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:outline-none transition-colors resize-none ${
                        errors.bio ? 'border-red-500' : 'border-brass/30 focus:border-brass'
                      }`}
                      placeholder="Tell us about yourself..."
                    />
                  </div>
                  <div className="flex justify-between items-center mt-1">
                    <span className="text-xs text-stardust-silver/60">
                      {registerData.bio?.length || 0}/250
                    </span>
                    {errors.bio && (
                      <p className="text-red-400 text-xs">{errors.bio}</p>
                    )}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading || Object.keys(errors).length > 0 || connectionStatus !== 'connected'}
                  className="w-full marble-button-large group disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="relative z-10 text-brass font-inter font-semibold tracking-wide group-hover:text-black-marble transition-colors duration-300">
                    {isLoading ? 'Creating Account...' : 'Create Account'}
                  </span>
                </button>

                <p className="text-center text-stardust-silver/60 text-sm">
                  Already have an account?{' '}
                  <button
                    type="button"
                    onClick={() => handleModeChange('login')}
                    className="text-brass hover:text-stardust-silver transition-colors"
                  >
                    Sign in here
                  </button>
                </p>
              </form>
            </>
          )}

          {/* Forgot Password Form */}
          {!isSuccess && mode === 'forgot-password' && (
            <>
              <h2 className="text-2xl font-cinzel font-bold text-center text-stardust-silver mb-6">
                Reset Password
              </h2>

              <p className="text-stardust-silver/70 mb-6 text-center text-sm">
                Enter your email address and we'll send you a link to reset your password.
              </p>

              {error && (
                <div className="mb-6 p-4 bg-red-500/20 border border-red-500/40 rounded-lg text-red-300">
                  {error}
                </div>
              )}

              <form onSubmit={handleForgotPasswordSubmit} className="space-y-6">
                <div>
                  <label className="block text-stardust-silver font-inter font-medium mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
                    <input
                      type="email"
                      value={forgotEmail}
                      onChange={(e) => setForgotEmail(e.target.value)}
                      className="w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 border-brass/30 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:border-brass focus:outline-none transition-colors"
                      placeholder="Enter your email"
                      required
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading || connectionStatus !== 'connected'}
                  className="w-full marble-button-large group disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="relative z-10 text-brass font-inter font-semibold tracking-wide group-hover:text-black-marble transition-colors duration-300">
                    {isLoading ? 'Sending...' : 'Send Reset Link'}
                  </span>
                </button>

                <p className="text-center text-stardust-silver/60 text-sm">
                  Remember your password?{' '}
                  <button
                    type="button"
                    onClick={() => handleModeChange('login')}
                    className="text-brass hover:text-stardust-silver transition-colors"
                  >
                    Sign in here
                  </button>
                </p>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthModal;