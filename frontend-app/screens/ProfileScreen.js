
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';

export default function ProfileScreen({ onBack, onLogout, onNavigate }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const saveProfile = () => {
    if (!name.trim() || !email.trim()) {
      Alert.alert('Profile', 'Please enter your name and email address.');
      return;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email.trim())) {
      Alert.alert('Invalid Email', 'Please enter a valid email address.');
      return;
    }

    Alert.alert(
      'Profile',
      'Profile details are ready. Saving to the database will be connected later.'
    );
  };

  const confirmLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: onLogout,
        },
      ]
    );
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TouchableOpacity onPress={onBack}>
        <Text style={styles.backText}>‹ Back to Home</Text>
      </TouchableOpacity>

      <Text style={styles.title}>My Profile</Text>

      <View style={styles.profileIcon}>
        <Text style={styles.profileIconText}>👤</Text>
      </View>

      <View style={styles.formCard}>
        <Text style={styles.label}>Full Name</Text>

        <TextInput
          style={styles.input}
          placeholder="Enter your full name"
          value={name}
          onChangeText={setName}
        />

        <Text style={styles.label}>Email Address</Text>

        <TextInput
          style={styles.input}
          placeholder="Enter your email address"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
        />

        <TouchableOpacity
          style={styles.saveButton}
          onPress={saveProfile}
        >
          <Text style={styles.buttonText}>Save Profile</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={styles.historyButton}
        onPress={() => onNavigate('history')}
      >
        <Text style={styles.historyIcon}>📂</Text>
        <Text style={styles.historyText}>Prescription History</Text>
        <Text style={styles.arrow}>›</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.logoutButton}
        onPress={confirmLogout}
      >
        <Text style={styles.logoutText}>Logout</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: '#F4F8FF',
    padding: 20,
  },
  backText: {
    color: '#1769AA',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 10,
  },
  title: {
    fontSize: 25,
    fontWeight: 'bold',
    color: '#1769AA',
    textAlign: 'center',
    marginTop: 25,
    marginBottom: 20,
  },
  profileIcon: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#DCEEFF',
    alignSelf: 'center',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 25,
  },
  profileIconText: {
    fontSize: 45,
  },
  formCard: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 12,
    elevation: 2,
  },
  label: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#DCE5EF',
    borderRadius: 8,
    padding: 13,
    marginBottom: 18,
    color: '#333',
  },
  saveButton: {
    backgroundColor: '#1769AA',
    padding: 15,
    borderRadius: 9,
    alignItems: 'center',
    marginTop: 5,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  historyButton: {
    backgroundColor: '#FFFFFF',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 17,
    borderRadius: 12,
    marginTop: 20,
    elevation: 2,
  },
  historyIcon: {
    fontSize: 24,
    marginRight: 15,
  },
  historyText: {
    flex: 1,
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1769AA',
  },
  arrow: {
    fontSize: 28,
    color: '#1769AA',
  },
  logoutButton: {
    backgroundColor: '#FCE8E8',
    padding: 15,
    borderRadius: 9,
    alignItems: 'center',
    marginTop: 25,
  },
  logoutText: {
    color: '#C62828',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
