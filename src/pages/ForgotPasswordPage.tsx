import React from 'react';
import CosmicBackground from '../components/CosmicBackground';
import ForgotPasswordForm from '../components/auth/ForgotPasswordForm';

const ForgotPasswordPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-black-marble overflow-hidden">
      <CosmicBackground />
      <div className="relative z-10 min-h-screen flex items-center justify-center py-12">
        <ForgotPasswordForm />
      </div>
    </div>
  );
};

export default ForgotPasswordPage;