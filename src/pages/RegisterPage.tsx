import React from 'react';
import CosmicBackground from '../components/CosmicBackground';
import RegistrationForm from '../components/auth/RegistrationForm';

const RegisterPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-black-marble overflow-hidden">
      <CosmicBackground />
      <div className="relative z-10 min-h-screen flex items-center justify-center py-12">
        <RegistrationForm />
      </div>
    </div>
  );
};

export default RegisterPage;