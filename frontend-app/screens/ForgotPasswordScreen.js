
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
} from 'react-native';

export default function ForgotPasswordScreen({ onBack }) {
  const [email, setEmail] = useState('');

  const handleReset = () => {
    if (!email.trim()) {
      Alert.alert('Missing Details', 'Please enter your email address.');
      return;
    }

    if (!email.includes('@') || !email.includes('.')) {
      Alert.alert('Invalid Email', 'Please enter a valid email address.');
      return;
    }

    Alert.alert(
      'Request Submitted',
      'Password reset functionality will be connected to the backend later.'
    );
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.logo}>💊</Text>

      <Text style={styles.title}>MediTeach</Text>
      <Text style={styles.heading}>Forgot Password?</Text>

      <Text style={styles.description}>
        Enter your registered email address to reset your password.
      </Text>

      <Text style={styles.label}>Email Address</Text>

      <TextInput
        style={styles.input}
        placeholder="Enter your registered email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />

      <TouchableOpacity
        style={styles.resetButton}
        onPress={handleReset}
      >
        <Text style={styles.buttonText}>Reset Password</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.backButton} onPress={onBack}>
        <Text style={styles.backText}>Back to Login</Text>
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
    fontSize: 50,
    textAlign: 'center',
    marginBottom: 10,
  },
  title: {
    fontSize: 30,
    fontWeight: 'bold',
    color: '#1769AA',
    textAlign: 'center',
  },
  heading: {
    fontSize: 23,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginTop: 30,
  },
  description: {
    fontSize: 15,
    color: '#666',
    textAlign: 'center',
    marginTop: 12,
    marginBottom: 25,
    lineHeight: 22,
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
  resetButton: {
    backgroundColor: '#1769AA',
    padding: 16,
    borderRadius: 9,
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  backButton: {
    alignItems: 'center',
    marginTop: 22,
  },
  backText: {
    color: '#1769AA',
    fontSize: 15,
    fontWeight: 'bold',
  },
});
