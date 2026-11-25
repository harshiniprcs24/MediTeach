import React, { useState, useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';

import { getStoredSession } from './services/authService';
import { clearSession }     from './services/api';

import LoginScreen              from './screens/LoginScreen';
import RegisterScreen           from './screens/RegisterScreen';
import ForgotPasswordScreen     from './screens/ForgotPasswordScreen';
import HomeScreen               from './screens/HomeScreen';
import UploadPrescriptionScreen from './screens/UploadPrescriptionScreen';
import PrescriptionExplanationScreen from './screens/PrescriptionExplanationScreen';
import ScanMedicineScreen       from './screens/ScanMedicineScreen';
import KnowledgeTestScreen      from './screens/KnowledgeTestScreen';
import AIAssistantScreen        from './screens/AIAssistantScreen';
import RemindersScreen          from './screens/RemindersScreen';
import PrescriptionHistoryScreen from './screens/PrescriptionHistoryScreen';
import ProfileScreen            from './screens/ProfileScreen';

export default function App() {
  // 'loading' while we check AsyncStorage on first render.
  // 'login' | 'register' | 'forgot' | 'home' | ... after that.
  const [screen, setScreen]             = useState('loading');
  // Holds the full PrescriptionOut object returned by the upload endpoint,
  // so PrescriptionExplanationScreen receives real data without a second fetch.
  const [currentPrescription, setCurrentPrescription] = useState(null);

  // ── Session restore ─────────────────────────────────────────────────────────
  // On app start, check whether a stored token exists.
  // If yes, go directly to 'home'. If no, show 'login'.
  // The token is NOT validated against the server here — that happens lazily
  // on the first authenticated API call. If it has expired, api.js will try
  // to refresh it automatically; if refresh fails, sessionExpired is set and
  // the screen navigates back to 'login'.
  useEffect(() => {
    (async () => {
      const session = await getStoredSession();
      setScreen(session ? 'home' : 'login');
    })();
  }, []);

  // ── Logout helper ────────────────────────────────────────────────────────────
  // Called by ProfileScreen's logout button AND by any screen that receives
  // a sessionExpired error from api.js in future wiring.
  const handleLogout = async () => {
    await clearSession();
    setScreen('login');
  };

  // ── Loading spinner ──────────────────────────────────────────────────────────
  if (screen === 'loading') {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1769AA" />
      </View>
    );
  }

  // ── Auth screens ─────────────────────────────────────────────────────────────
  if (screen === 'login') {
    return (
      <LoginScreen
        onLogin={() => setScreen('home')}
        onRegister={() => setScreen('register')}
        onForgotPassword={() => setScreen('forgot')}
      />
    );
  }

  if (screen === 'register') {
    return (
      <RegisterScreen
        onBack={() => setScreen('login')}
        onRegister={() => setScreen('login')}
      />
    );
  }

  if (screen === 'forgot') {
    return <ForgotPasswordScreen onBack={() => setScreen('login')} />;
  }

  // ── Main app screens ──────────────────────────────────────────────────────────
  if (screen === 'home') {
    return (
      <HomeScreen
        onNavigate={(destination) => setScreen(destination)}
      />
    );
  }

  if (screen === 'upload') {
    return (
      <UploadPrescriptionScreen
        onBack={() => setScreen('home')}
        onContinue={(prescription) => {
          // prescription is the full PrescriptionOut object from the backend
          setCurrentPrescription(prescription);
          setScreen('explanation');
        }}
      />
    );
  }

  if (screen === 'explanation') {
    return (
      <PrescriptionExplanationScreen
        onBack={() => {
          setCurrentPrescription(null);
          setScreen('upload');
        }}
        prescription={currentPrescription}
      />
    );
  }

  if (screen === 'scan') {
    return <ScanMedicineScreen onBack={() => setScreen('home')} />;
  }

  if (screen === 'test') {
    return <KnowledgeTestScreen onBack={() => setScreen('home')} />;
  }

  if (screen === 'assistant') {
    return <AIAssistantScreen onBack={() => setScreen('home')} />;
  }

  if (screen === 'reminders') {
    return <RemindersScreen onBack={() => setScreen('home')} />;
  }

  if (screen === 'history') {
    return <PrescriptionHistoryScreen onBack={() => setScreen('home')} />;
  }

  if (screen === 'profile') {
    return (
      <ProfileScreen
        onBack={() => setScreen('home')}
        onLogout={handleLogout}
      />
    );
  }

  return null;
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    backgroundColor: '#F4F8FF',
    justifyContent: 'center',
    alignItems: 'center',
  },
});
