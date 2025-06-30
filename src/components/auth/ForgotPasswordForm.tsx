import React, { useState } from 'react';
import { Mail, ArrowLeft } from 'lucide-react';
import { resetPassword } from '../../lib/supabase';

const ForgotPasswordForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const { error: resetError } = await resetPassword(email);
      
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

  if (isSuccess) {
    return (
      <div className="max-w-md mx-auto p-8">
        <div className="glass-card p-8 text-center">
          <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Mail className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-cinzel font-bold text-stardust-silver mb-4">
            Check Your Email
          </h2>
          <p className="text-stardust-silver/70 mb-6">
            We've sent a password reset link to <strong>{email}</strong>
          </p>
          <a
            href="/login"
            className="marble-button inline-block"
          >
            <span className="relative z-10 text-brass font-inter font-medium">
              Back to Login
            </span>
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto p-8">
      <div className="glass-card p-8">
        <div className="flex items-center mb-6">
          <a
            href="/login"
            className="text-brass hover:text-stardust-silver transition-colors mr-4"
          >
            <ArrowLeft className="w-5 h-5" />
          </a>
          <h2 className="text-2xl font-cinzel font-bold text-stardust-silver">
            Reset Password
          </h2>
        </div>

        <p className="text-stardust-silver/70 mb-6">
          Enter your email address and we'll send you a link to reset your password.
        </p>

        {error && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500/40 rounded-lg text-red-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-stardust-silver font-inter font-medium mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-brass w-5 h-5" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-black-marble/50 border-2 border-brass/30 rounded-lg text-stardust-silver placeholder-stardust-silver/50 font-inter focus:border-brass focus:outline-none transition-colors"
                placeholder="Enter your email"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full marble-button-large group disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="relative z-10 text-brass font-inter font-semibold tracking-wide group-hover:text-black-marble transition-colors duration-300">
              {isLoading ? 'Sending...' : 'Send Reset Link'}
            </span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default ForgotPasswordForm;