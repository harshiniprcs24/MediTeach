import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
} from 'react-native';

import { login } from '../services/authService';

export default function LoginScreen({
  onLogin,
  onRegister,
  onForgotPassword,
}) {
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading]   = useState(false);

  const handleLogin = async () => {
    // ── Client-side validation ──────────────────────────────────────────────
    if (!email.trim() || !password) {
      Alert.alert('Missing Details', 'Please enter your email and password.');
      return;
    }

    if (!email.includes('@') || !email.includes('.')) {
      Alert.alert('Invalid Email', 'Please enter a valid email address.');
      return;
    }

    // ── Call backend ────────────────────────────────────────────────────────
    setLoading(true);
    const result = await login(email, password);
    setLoading(false);

    if (result.error) {
      // Map common HTTP status codes to user-friendly messages
      if (result.status === 401) {
        Alert.alert('Login Failed', 'Incorrect email or password. Please try again.');
      } else if (result.status === 403) {
        Alert.alert('Account Disabled', 'Your account has been deactivated. Contact support.');
      } else if (result.status === 0) {
        Alert.alert('Connection Error', result.message);
      } else {
        Alert.alert('Login Failed', result.message || 'An unexpected error occurred.');
      }
      return;
    }

    // Success — navigate to home
    onLogin();
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.logo}>💊</Text>

      <Text style={styles.title}>MediTeach</Text>
      <Text style={styles.subtitle}>Your Smart Medication Assistant</Text>

      <Text style={styles.heading}>Login</Text>

      <Text style={styles.label}>Email Address</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter your email address"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        autoCorrect={false}
        editable={!loading}
      />

      <Text style={styles.label}>Password</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter your password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        editable={!loading}
      />

      <TouchableOpacity
        style={[styles.loginButton, loading && styles.loginButtonDisabled]}
        onPress={handleLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#FFFFFF" />
        ) : (
          <Text style={styles.loginButtonText}>Login</Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity
        onPress={onForgotPassword}
        style={styles.linkButton}
        disabled={loading}
      >
        <Text style={styles.linkText}>Forgot Password?</Text>
      </TouchableOpacity>

      <TouchableOpacity
        onPress={onRegister}
        style={styles.registerButton}
        disabled={loading}
      >
        <Text style={styles.registerText}>
          Don't have an account? Register
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: '#F4F8FF',
    justifyContent: 'center',
    padding: 25,
  },
  logo: {
    fontSize: 55,
    textAlign: 'center',
    marginBottom: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1769AA',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 15,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 35,
  },
  heading: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1769AA',
    textAlign: 'center',
    marginBottom: 22,
  },
  label: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 7,
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#DCE5EF',
    borderRadius: 9,
    padding: 14,
    fontSize: 15,
    marginBottom: 18,
  },
  loginButton: {
    backgroundColor: '#1769AA',
    padding: 16,
    borderRadius: 9,
    alignItems: 'center',
    marginTop: 5,
    minHeight: 52,
    justifyContent: 'center',
  },
  loginButtonDisabled: {
    backgroundColor: '#9CB8D2',
  },
  loginButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  linkButton: {
    alignItems: 'center',
    marginTop: 18,
  },
  linkText: {
    color: '#1769AA',
    fontWeight: 'bold',
  },
  registerButton: {
    alignItems: 'center',
    marginTop: 20,
  },
  registerText: {
    color: '#1769AA',
    fontSize: 15,
    fontWeight: 'bold',
  },
});
