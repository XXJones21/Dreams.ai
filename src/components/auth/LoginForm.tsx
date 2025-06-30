import React, { useState } from 'react';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { signIn } from '../../lib/supabase';

interface LoginFormProps {
  onSuccess?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const { data, error: signInError } = await signIn(formData.email, formData.password);
      
      if (signInError) {
        setError(signInError.message);
        setIsLoading(false);
        return;
      }

      if (data.user) {
        onSuccess?.();
        window.location.href = '/profile';
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-8">
      <div className="glass-card p-8">
        <h2 className="text-3xl font-cinzel font-bold text-center text-stardust-silver mb-8">
          <span className="bg-gradient-to-r from-brass to-electric-blue bg-clip-text text-transparent">
            Welcome Back
          </span>
        </h2>

        {error && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500/40 rounded-lg text-red-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email */}
          <div>
            <label className="block text-stardust-silver font-inter font-medium mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 border-brass/30 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:border-brass focus:outline-none transition-colors"
                placeholder="Enter your email"
                required
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-stardust-silver font-inter font-medium mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
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

          {/* Forgot Password */}
          <div className="text-right">
            <a
              href="/auth/forgot-password"
              className="text-brass hover:text-stardust-silver transition-colors text-sm"
            >
              Forgot your password?
            </a>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full marble-button-large group disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="relative z-10 text-brass font-inter font-semibold tracking-wide group-hover:text-black-marble transition-colors duration-300">
              {isLoading ? 'Signing In...' : 'Sign In'}
            </span>
          </button>

          <p className="text-center text-stardust-silver/60 text-sm">
            Don't have an account?{' '}
            <a href="/register" className="text-brass hover:text-stardust-silver transition-colors">
              Create one here
            </a>
          </p>
        </form>
      </div>
    </div>
  );
};

export default LoginForm;