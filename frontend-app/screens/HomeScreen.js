
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';

export default function HomeScreen({ onNavigate }) {
  const features = [
    {
      title: 'Upload Prescription',
      description: 'Upload a prescription image or PDF.',
      icon: '📄',
      action: 'upload',
    },
    {
      title: 'Scan Medicine',
      description: 'Scan your medicine package or tablet.',
      icon: '📷',
      action: 'scan',
    },
    {
      title: 'AI Medicine Assistant',
      description: 'Ask questions about your medicines.',
      icon: '🤖',
      action: 'assistant',
    },
    {
      title: 'Medicine Reminders',
      description: 'Manage your medicine timings.',
      icon: '⏰',
      action: 'reminders',
    },
    {
      title: 'My Profile',
      description: 'View and manage your profile.',
      icon: '👤',
      action: 'profile',
    },
  ];

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>MediTeach</Text>

      <Text style={styles.subtitle}>
        Medicine Made Simple.
      </Text>

      <Text style={styles.heading}>Welcome!</Text>

      <Text style={styles.description}>
        What would you like to do today?
      </Text>

      {features.map((feature) => (
        <TouchableOpacity
          key={feature.action}
          style={styles.card}
          onPress={() => onNavigate(feature.action)}
        >
          <Text style={styles.icon}>{feature.icon}</Text>

          <View style={styles.cardContent}>
            <Text style={styles.cardTitle}>
              {feature.title}
            </Text>

            <Text style={styles.cardDescription}>
              {feature.description}
            </Text>
          </View>

          <Text style={styles.arrow}>›</Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: '#F4F8FF',
    padding: 20,
  },
  title: {
    fontSize: 30,
    fontWeight: 'bold',
    color: '#1769AA',
    textAlign: 'center',
    marginTop: 25,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 5,
  },
  heading: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 35,
  },
  description: {
    fontSize: 15,
    color: '#666',
    marginTop: 8,
    marginBottom: 20,
  },
  card: {
    backgroundColor: '#FFFFFF',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 17,
    borderRadius: 13,
    marginBottom: 14,
    elevation: 2,
  },
  icon: {
    fontSize: 30,
    marginRight: 15,
  },
  cardContent: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1769AA',
  },
  cardDescription: {
    fontSize: 12,
    color: '#777',
    marginTop: 5,
  },
  arrow: {
    fontSize: 28,
    color: '#1769AA',
  },
});
