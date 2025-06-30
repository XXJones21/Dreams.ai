import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle, Loader2, RefreshCw, Copy, ExternalLink } from 'lucide-react';
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
  details?: any;
}

const AuthTest: React.FC = () => {
  const [tests, setTests] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [testEmail] = useState(`test-${Date.now()}@example.com`);
  const [testPassword] = useState('TestPassword123!');
  const [connectionDetails, setConnectionDetails] = useState<any>(null);

  const updateTest = (name: string, status: TestResult['status'], message: string, duration?: number, details?: any) => {
    setTests(prev => {
      const existing = prev.find(t => t.name === name);
      if (existing) {
        return prev.map(t => t.name === name ? { ...t, status, message, duration, details } : t);
      }
      return [...prev, { name, status, message, duration, details }];
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
      updateTest(name, 'error', error.message || 'Failed', duration, error.details);
    }
  };

  const runConnectionTest = async () => {
    setIsRunning(true);
    setTests([]);
    setConnectionDetails(null);

    // Test 1: Connection Test with detailed diagnostics
    await runTest('Connection Test', async () => {
      const result = await testSupabaseConnection();
      setConnectionDetails(result.details);
      
      if (!result.success) {
        throw new Error(result.error || 'Connection failed');
      }
    });

    setIsRunning(false);
  };

  const runAllTests = async () => {
    setIsRunning(true);
    setTests([]);
    setConnectionDetails(null);

    // Test 1: Connection
    await runTest('Connection Test', async () => {
      const result = await testSupabaseConnection();
      setConnectionDetails(result.details);
      
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

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const successCount = tests.filter(t => t.status === 'success').length;
  const errorCount = tests.filter(t => t.status === 'error').length;
  const totalTests = tests.length;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="glass-card p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-cinzel font-bold text-stardust-silver mb-2">
              Supabase Connection Diagnostics
            </h2>
            <p className="text-stardust-silver/70">
              Comprehensive testing of Supabase authentication integration
            </p>
          </div>
          <div className="flex space-x-4">
            <button
              onClick={runConnectionTest}
              disabled={isRunning}
              className="glass-button flex items-center space-x-2"
            >
              <AlertCircle className={`w-4 h-4 ${isRunning ? 'animate-spin' : ''}`} />
              <span className="relative z-10 text-stardust-silver font-inter font-medium">
                Test Connection
              </span>
            </button>
            <button
              onClick={runAllTests}
              disabled={isRunning}
              className="marble-button flex items-center space-x-2"
            >
              <RefreshCw className={`w-4 h-4 ${isRunning ? 'animate-spin' : ''}`} />
              <span className="relative z-10 text-brass font-inter font-medium">
                {isRunning ? 'Running Tests...' : 'Run All Tests'}
              </span>
            </button>
          </div>
        </div>

        {/* Environment Variables Check */}
        <div className="mb-8 glass-card p-6">
          <h3 className="text-xl font-cinzel font-semibold text-stardust-silver mb-4">
            Environment Configuration
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-stardust-silver/60">VITE_SUPABASE_URL:</span>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-mono ${
                    import.meta.env.VITE_SUPABASE_URL ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {import.meta.env.VITE_SUPABASE_URL ? 
                      `${import.meta.env.VITE_SUPABASE_URL.substring(0, 30)}...` : 
                      'Not configured'
                    }
                  </span>
                  {import.meta.env.VITE_SUPABASE_URL && (
                    <button
                      onClick={() => copyToClipboard(import.meta.env.VITE_SUPABASE_URL)}
                      className="text-brass hover:text-stardust-silver"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-stardust-silver/60">VITE_SUPABASE_ANON_KEY:</span>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-mono ${
                    import.meta.env.VITE_SUPABASE_ANON_KEY ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {import.meta.env.VITE_SUPABASE_ANON_KEY ? 
                      `${import.meta.env.VITE_SUPABASE_ANON_KEY.substring(0, 20)}...` : 
                      'Not configured'
                    }
                  </span>
                  {import.meta.env.VITE_SUPABASE_ANON_KEY && (
                    <button
                      onClick={() => copyToClipboard(import.meta.env.VITE_SUPABASE_ANON_KEY)}
                      className="text-brass hover:text-stardust-silver"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-stardust-silver/60">Environment:</span>
                <span className="text-sm text-stardust-silver font-mono">
                  {import.meta.env.MODE}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-stardust-silver/60">Base URL:</span>
                <span className="text-sm text-stardust-silver font-mono">
                  {window.location.origin}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Connection Details */}
        {connectionDetails && (
          <div className="mb-8 glass-card p-6">
            <h3 className="text-xl font-cinzel font-semibold text-stardust-silver mb-4">
              Connection Details
            </h3>
            <div className="bg-black-marble/50 p-4 rounded-lg">
              <pre className="text-sm text-stardust-silver/80 overflow-x-auto">
                {JSON.stringify(connectionDetails, null, 2)}
              </pre>
            </div>
          </div>
        )}

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
                    {test.details && (
                      <details className="mt-2">
                        <summary className="text-xs text-stardust-silver/60 cursor-pointer">
                          Show details
                        </summary>
                        <div className="mt-2 bg-black-marble/50 p-2 rounded text-xs">
                          <pre className="text-stardust-silver/70 overflow-x-auto">
                            {JSON.stringify(test.details, null, 2)}
                          </pre>
                        </div>
                      </details>
                    )}
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

        {/* Troubleshooting Guide */}
        <div className="mt-8 pt-8 border-t border-brass/20">
          <h3 className="text-lg font-cinzel font-semibold text-stardust-silver mb-4">
            Troubleshooting Guide
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-inter font-semibold text-brass">Common Issues:</h4>
              <ul className="space-y-2 text-sm text-stardust-silver/70">
                <li>• <strong>Missing .env file:</strong> Create .env file in project root</li>
                <li>• <strong>Invalid URL format:</strong> Should be https://your-project.supabase.co</li>
                <li>• <strong>Wrong API key:</strong> Use anon/public key, not service role key</li>
                <li>• <strong>CORS errors:</strong> Check Supabase project settings</li>
                <li>• <strong>Network timeout:</strong> Check internet connection</li>
              </ul>
            </div>
            <div className="space-y-4">
              <h4 className="font-inter font-semibold text-brass">Quick Fixes:</h4>
              <ul className="space-y-2 text-sm text-stardust-silver/70">
                <li>• Restart development server after .env changes</li>
                <li>• Verify Supabase project is not paused</li>
                <li>• Check browser console for detailed errors</li>
                <li>• Ensure database tables exist and RLS is configured</li>
                <li>• Test connection from Supabase dashboard</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-brass/10 border border-brass/30 rounded-lg">
            <div className="flex items-start space-x-3">
              <ExternalLink className="w-5 h-5 text-brass mt-0.5" />
              <div>
                <h4 className="font-inter font-semibold text-brass mb-2">Need Help?</h4>
                <p className="text-sm text-stardust-silver/70 mb-2">
                  If you're still experiencing issues, check these resources:
                </p>
                <ul className="text-sm text-stardust-silver/70 space-y-1">
                  <li>• <a href="https://supabase.com/docs" target="_blank" rel="noopener noreferrer" className="text-brass hover:underline">Supabase Documentation</a></li>
                  <li>• <a href="https://supabase.com/dashboard" target="_blank" rel="noopener noreferrer" className="text-brass hover:underline">Supabase Dashboard</a></li>
                  <li>• Check your project's API settings and RLS policies</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthTest;