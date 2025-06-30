import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle, Loader2, RefreshCw } from 'lucide-react';
import { 
  testSupabaseConnection, 
  signUp, 
  signIn, 
  signOut, 
  getCurrentUser,
  getCurrentSession,
  createProfile,
  getProfile
} from '../../lib/supabase';

interface TestResult {
  name: string;
  status: 'pending' | 'success' | 'error';
  message: string;
  duration?: number;
}

const AuthTest: React.FC = () => {
  const [tests, setTests] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [testEmail] = useState(`test-${Date.now()}@example.com`);
  const [testPassword] = useState('TestPassword123!');

  const updateTest = (name: string, status: TestResult['status'], message: string, duration?: number) => {
    setTests(prev => {
      const existing = prev.find(t => t.name === name);
      if (existing) {
        return prev.map(t => t.name === name ? { ...t, status, message, duration } : t);
      }
      return [...prev, { name, status, message, duration }];
    });
  };

  const runTest = async (name: string, testFn: () => Promise<void>) => {
    const startTime = Date.now();
    updateTest(name, 'pending', 'Running...');
    
    try {
      await testFn();
      const duration = Date.now() - startTime;
      updateTest(name, 'success', 'Passed', duration);
    } catch (error: any) {
      const duration = Date.now() - startTime;
      updateTest(name, 'error', error.message || 'Failed', duration);
    }
  };

  const runAllTests = async () => {
    setIsRunning(true);
    setTests([]);

    // Test 1: Connection
    await runTest('Connection Test', async () => {
      const result = await testSupabaseConnection();
      if (!result.success) {
        throw new Error(result.error || 'Connection failed');
      }
    });

    // Test 2: User Registration
    await runTest('User Registration', async () => {
      const { data, error } = await signUp(testEmail, testPassword);
      if (error) {
        throw new Error(error.message);
      }
      if (!data.user) {
        throw new Error('No user returned from registration');
      }
    });

    // Test 3: User Login
    await runTest('User Login', async () => {
      const { data, error } = await signIn(testEmail, testPassword);
      if (error) {
        throw new Error(error.message);
      }
      if (!data.user) {
        throw new Error('No user returned from login');
      }
    });

    // Test 4: Session Management
    await runTest('Session Management', async () => {
      const { session, error } = await getCurrentSession();
      if (error) {
        throw new Error(error.message);
      }
      if (!session) {
        throw new Error('No active session found');
      }
    });

    // Test 5: Profile Creation
    await runTest('Profile Creation', async () => {
      const { user } = await getCurrentUser();
      if (!user) {
        throw new Error('No authenticated user');
      }

      const profileData = {
        user_id: user.id,
        full_name: 'Test User',
        email: testEmail,
        date_of_birth: '1990-01-01',
        bio: 'Test profile for authentication testing'
      };

      const { data, error } = await createProfile(profileData);
      if (error) {
        throw new Error(error.message);
      }
      if (!data) {
        throw new Error('No profile data returned');
      }
    });

    // Test 6: Profile Retrieval
    await runTest('Profile Retrieval', async () => {
      const { user } = await getCurrentUser();
      if (!user) {
        throw new Error('No authenticated user');
      }

      const { data, error } = await getProfile(user.id);
      if (error) {
        throw new Error(error.message);
      }
      if (!data) {
        throw new Error('No profile found');
      }
    });

    // Test 7: User Logout
    await runTest('User Logout', async () => {
      const { error } = await signOut();
      if (error) {
        throw new Error(error.message);
      }

      // Verify session is cleared
      const { session } = await getCurrentSession();
      if (session) {
        throw new Error('Session still active after logout');
      }
    });

    setIsRunning(false);
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'pending':
        return <Loader2 className="w-5 h-5 animate-spin text-brass" />;
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return <AlertCircle className="w-5 h-5 text-stardust-silver/50" />;
    }
  };

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'success':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      case 'pending':
        return 'text-brass';
      default:
        return 'text-stardust-silver/50';
    }
  };

  const successCount = tests.filter(t => t.status === 'success').length;
  const errorCount = tests.filter(t => t.status === 'error').length;
  const totalTests = tests.length;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="glass-card p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-cinzel font-bold text-stardust-silver mb-2">
              Authentication Test Suite
            </h2>
            <p className="text-stardust-silver/70">
              Comprehensive testing of Supabase authentication integration
            </p>
          </div>
          <button
            onClick={runAllTests}
            disabled={isRunning}
            className="marble-button flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${isRunning ? 'animate-spin' : ''}`} />
            <span className="relative z-10 text-brass font-inter font-medium">
              {isRunning ? 'Running Tests...' : 'Run Tests'}
            </span>
          </button>
        </div>

        {/* Test Summary */}
        {tests.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="glass-card p-4 text-center">
              <div className="text-2xl font-bold text-green-400">{successCount}</div>
              <div className="text-sm text-stardust-silver/60">Passed</div>
            </div>
            <div className="glass-card p-4 text-center">
              <div className="text-2xl font-bold text-red-400">{errorCount}</div>
              <div className="text-sm text-stardust-silver/60">Failed</div>
            </div>
            <div className="glass-card p-4 text-center">
              <div className="text-2xl font-bold text-brass">{totalTests}</div>
              <div className="text-sm text-stardust-silver/60">Total</div>
            </div>
          </div>
        )}

        {/* Test Results */}
        <div className="space-y-4">
          {tests.map((test, index) => (
            <div key={test.name} className="glass-card p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(test.status)}
                  <div>
                    <h3 className="font-inter font-semibold text-stardust-silver">
                      {index + 1}. {test.name}
                    </h3>
                    <p className={`text-sm ${getStatusColor(test.status)}`}>
                      {test.message}
                    </p>
                  </div>
                </div>
                {test.duration && (
                  <div className="text-sm text-stardust-silver/60">
                    {test.duration}ms
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Test Configuration */}
        <div className="mt-8 pt-8 border-t border-brass/20">
          <h3 className="text-lg font-cinzel font-semibold text-stardust-silver mb-4">
            Test Configuration
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-stardust-silver/60">Test Email:</span>
              <span className="ml-2 text-stardust-silver font-mono">{testEmail}</span>
            </div>
            <div>
              <span className="text-stardust-silver/60">Test Password:</span>
              <span className="ml-2 text-stardust-silver font-mono">TestPassword123!</span>
            </div>
            <div>
              <span className="text-stardust-silver/60">Supabase URL:</span>
              <span className="ml-2 text-stardust-silver font-mono">
                {import.meta.env.VITE_SUPABASE_URL || 'Not configured'}
              </span>
            </div>
            <div>
              <span className="text-stardust-silver/60">Environment:</span>
              <span className="ml-2 text-stardust-silver font-mono">
                {import.meta.env.MODE}
              </span>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-8 pt-8 border-t border-brass/20">
          <h3 className="text-lg font-cinzel font-semibold text-stardust-silver mb-4">
            Setup Instructions
          </h3>
          <div className="space-y-2 text-sm text-stardust-silver/70">
            <p>1. Ensure your <code className="bg-black-marble/50 px-2 py-1 rounded">.env</code> file contains valid Supabase credentials</p>
            <p>2. Run the database migrations to create the required tables</p>
            <p>3. Configure RLS policies in your Supabase dashboard</p>
            <p>4. Set up the profile-pictures storage bucket</p>
            <p>5. Click "Run Tests" to verify your authentication setup</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthTest;