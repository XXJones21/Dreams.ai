import React, { useState } from 'react';
import { User, Mail, Lock, Calendar, FileImage, MessageSquare, Eye, EyeOff, Upload, X } from 'lucide-react';
import { supabase, signUp, createProfile, uploadProfilePicture, UserRegistrationData } from '../../lib/supabase';

interface FormErrors {
  fullName?: string;
  email?: string;
  password?: string;
  dateOfBirth?: string;
  profilePicture?: string;
  bio?: string;
  general?: string;
}

const RegistrationForm: React.FC = () => {
  const [formData, setFormData] = useState<UserRegistrationData>({
    fullName: '',
    email: '',
    password: '',
    dateOfBirth: '',
    bio: ''
  });
  
  const [profilePicture, setProfilePicture] = useState<File | null>(null);
  const [profilePicturePreview, setProfilePicturePreview] = useState<string>('');
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  // Validation functions
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePassword = (password: string): boolean => {
    const hasMinLength = password.length >= 8;
    const hasNumber = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    return hasMinLength && hasNumber && hasSpecialChar;
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

  // Real-time validation
  const validateField = (name: string, value: string | File) => {
    const newErrors = { ...errors };

    switch (name) {
      case 'fullName':
        if (!value || (value as string).trim().length < 2) {
          newErrors.fullName = 'Full name must be at least 2 characters';
        } else {
          delete newErrors.fullName;
        }
        break;

      case 'email':
        if (!value) {
          newErrors.email = 'Email is required';
        } else if (!validateEmail(value as string)) {
          newErrors.email = 'Please enter a valid email address';
        } else {
          delete newErrors.email;
        }
        break;

      case 'password':
        if (!value) {
          newErrors.password = 'Password is required';
        } else if (!validatePassword(value as string)) {
          newErrors.password = 'Password must be at least 8 characters with numbers and special characters';
        } else {
          delete newErrors.password;
        }
        break;

      case 'dateOfBirth':
        if (!value) {
          newErrors.dateOfBirth = 'Date of birth is required';
        } else if (!validateAge(value as string)) {
          newErrors.dateOfBirth = 'You must be at least 13 years old to register';
        } else {
          delete newErrors.dateOfBirth;
        }
        break;

      case 'bio':
        if (value && (value as string).length > 250) {
          newErrors.bio = 'Bio must be 250 characters or less';
        } else {
          delete newErrors.bio;
        }
        break;

      case 'profilePicture':
        if (value) {
          const fileError = validateFile(value as File);
          if (fileError) {
            newErrors.profilePicture = fileError;
          } else {
            delete newErrors.profilePicture;
          }
        }
        break;
    }

    setErrors(newErrors);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    validateField(name, value);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      validateField('profilePicture', file);
      if (!errors.profilePicture) {
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
    delete errors.profilePicture;
    setErrors({ ...errors });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      // Final validation
      const validationErrors: FormErrors = {};
      
      if (!formData.fullName.trim()) validationErrors.fullName = 'Full name is required';
      if (!validateEmail(formData.email)) validationErrors.email = 'Valid email is required';
      if (!validatePassword(formData.password)) validationErrors.password = 'Password requirements not met';
      if (!validateAge(formData.dateOfBirth)) validationErrors.dateOfBirth = 'Must be 13+ years old';
      if (formData.bio && formData.bio.length > 250) validationErrors.bio = 'Bio too long';
      if (profilePicture && validateFile(profilePicture)) validationErrors.profilePicture = validateFile(profilePicture)!;

      if (Object.keys(validationErrors).length > 0) {
        setErrors(validationErrors);
        setIsLoading(false);
        return;
      }

      // Sign up user
      const { data: authData, error: authError } = await signUp(formData.email, formData.password);
      
      if (authError) {
        setErrors({ general: authError.message });
        setIsLoading(false);
        return;
      }

      if (!authData.user) {
        setErrors({ general: 'Registration failed. Please try again.' });
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
          // Continue without profile picture
        } else if (uploadData) {
          profilePictureUrl = uploadData.publicUrl;
        }
      }

      // Create profile
      const { error: profileError } = await createProfile({
        user_id: authData.user.id,
        full_name: formData.fullName.trim(),
        email: formData.email,
        profile_picture_url: profilePictureUrl,
        bio: formData.bio?.trim() || null,
        date_of_birth: formData.dateOfBirth
      });

      if (profileError) {
        setErrors({ general: 'Profile creation failed. Please try again.' });
        setIsLoading(false);
        return;
      }

      setIsSuccess(true);
      
      // Redirect after success
      setTimeout(() => {
        window.location.href = '/profile';
      }, 2000);

    } catch (error) {
      console.error('Registration error:', error);
      setErrors({ general: 'An unexpected error occurred. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="max-w-md mx-auto p-8 glass-card text-center">
        <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <User className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-2xl font-cinzel font-bold text-stardust-silver mb-4">
          Registration Successful!
        </h2>
        <p className="text-stardust-silver/70 mb-4">
          Please check your email to verify your account.
        </p>
        <p className="text-brass text-sm">
          Redirecting to your profile...
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-8">
      <div className="glass-card p-8">
        <h2 className="text-3xl font-cinzel font-bold text-center text-stardust-silver mb-8">
          <span className="bg-gradient-to-r from-brass to-nebula-pink bg-clip-text text-transparent">
            Create Your Account
          </span>
        </h2>

        {errors.general && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500/40 rounded-lg text-red-300">
            {errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Profile Picture Upload */}
          <div className="text-center">
            <div className="relative inline-block">
              {profilePicturePreview ? (
                <div className="relative">
                  <img
                    src={profilePicturePreview}
                    alt="Profile preview"
                    className="w-24 h-24 rounded-full object-cover border-2 border-brass"
                  />
                  <button
                    type="button"
                    onClick={removeProfilePicture}
                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-white hover:bg-red-600 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <div className="w-24 h-24 rounded-full bg-black-marble/50 border-2 border-brass/30 flex items-center justify-center">
                  <FileImage className="w-8 h-8 text-brass/50" />
                </div>
              )}
            </div>
            <div className="mt-4">
              <label className="marble-button cursor-pointer">
                <input
                  type="file"
                  accept=".jpg,.jpeg,.png"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <span className="relative z-10 text-brass font-inter font-medium flex items-center space-x-2">
                  <Upload className="w-4 h-4" />
                  <span>Upload Photo</span>
                </span>
              </label>
              <p className="text-xs text-stardust-silver/50 mt-2">
                Optional • JPG, PNG up to 5MB
              </p>
              {errors.profilePicture && (
                <p className="text-red-400 text-sm mt-1">{errors.profilePicture}</p>
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
                value={formData.fullName}
                onChange={handleInputChange}
                className={`w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:outline-none transition-colors ${
                  errors.fullName ? 'border-red-500' : 'border-brass/30 focus:border-brass'
                }`}
                placeholder="Enter your full name"
                required
              />
            </div>
            {errors.fullName && (
              <p className="text-red-400 text-sm mt-1">{errors.fullName}</p>
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
                value={formData.email}
                onChange={handleInputChange}
                className={`w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:outline-none transition-colors ${
                  errors.email ? 'border-red-500' : 'border-brass/30 focus:border-brass'
                }`}
                placeholder="Enter your email"
                required
              />
            </div>
            {errors.email && (
              <p className="text-red-400 text-sm mt-1">{errors.email}</p>
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
                value={formData.password}
                onChange={handleInputChange}
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
              Minimum 8 characters with numbers and special characters
            </p>
            {errors.password && (
              <p className="text-red-400 text-sm mt-1">{errors.password}</p>
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
                value={formData.dateOfBirth}
                onChange={handleInputChange}
                className={`w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 rounded-lg text-stardust-silver font-inter focus:outline-none transition-colors ${
                  errors.dateOfBirth ? 'border-red-500' : 'border-brass/30 focus:border-brass'
                }`}
                required
              />
            </div>
            <p className="text-xs text-stardust-silver/60 mt-1">
              You must be at least 13 years old
            </p>
            {errors.dateOfBirth && (
              <p className="text-red-400 text-sm mt-1">{errors.dateOfBirth}</p>
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
                value={formData.bio}
                onChange={handleInputChange}
                rows={3}
                maxLength={250}
                className={`w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:outline-none transition-colors resize-none ${
                  errors.bio ? 'border-red-500' : 'border-brass/30 focus:border-brass'
                }`}
                placeholder="Tell us a bit about yourself..."
              />
            </div>
            <div className="flex justify-between items-center mt-1">
              <span className="text-xs text-stardust-silver/60">
                {formData.bio?.length || 0}/250 characters
              </span>
              {errors.bio && (
                <p className="text-red-400 text-sm">{errors.bio}</p>
              )}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading || Object.keys(errors).length > 0}
            className="w-full marble-button-large group disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="relative z-10 text-brass font-inter font-semibold tracking-wide group-hover:text-black-marble transition-colors duration-300">
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </span>
          </button>

          <p className="text-center text-stardust-silver/60 text-sm">
            Already have an account?{' '}
            <a href="/login" className="text-brass hover:text-stardust-silver transition-colors">
              Sign in here
            </a>
          </p>
        </form>
      </div>
    </div>
  );
};

export default RegistrationForm;