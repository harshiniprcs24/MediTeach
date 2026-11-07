
import React, { useState } from 'react';

import LoginScreen from './screens/LoginScreen';
import RegisterScreen from './screens/RegisterScreen';
import ForgotPasswordScreen from './screens/ForgotPasswordScreen';
import HomeScreen from './screens/HomeScreen';
import UploadPrescriptionScreen from './screens/UploadPrescriptionScreen';
import PrescriptionExplanationScreen from './screens/PrescriptionExplanationScreen';
import ScanMedicineScreen from './screens/ScanMedicineScreen';
import KnowledgeTestScreen from './screens/KnowledgeTestScreen';
import AIAssistantScreen from './screens/AIAssistantScreen';
import RemindersScreen from './screens/RemindersScreen';
import PrescriptionHistoryScreen from './screens/PrescriptionHistoryScreen';
import ProfileScreen from './screens/ProfileScreen';

export default function App() {
  const [screen, setScreen] = useState('login');

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
        onContinue={() => setScreen('explanation')}
      />
    );
  }

  if (screen === 'explanation') {
    return (
      <PrescriptionExplanationScreen
        onBack={() => setScreen('upload')}
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
        onLogout={() => setScreen('login')}
      />
    );
  }

  return null;
}
