
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';

export default function PrescriptionHistoryScreen({ onBack }) {
  const [prescriptions, setPrescriptions] = useState([]);

  const deletePrescription = (id) => {
    Alert.alert(
      'Delete Prescription',
      'Are you sure you want to delete this prescription?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            setPrescriptions((previous) =>
              previous.filter((item) => item.id !== id)
            );
          },
        },
      ]
    );
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TouchableOpacity onPress={onBack}>
        <Text style={styles.backText}>‹ Back to Home</Text>
      </TouchableOpacity>

      <Text style={styles.title}>Prescription History</Text>

      <Text style={styles.description}>
        View your previously uploaded prescriptions.
      </Text>

      {prescriptions.length === 0 ? (
        <View style={styles.emptyCard}>
          <Text style={styles.emptyIcon}>📄</Text>
          <Text style={styles.emptyTitle}>No Prescriptions Found</Text>
          <Text style={styles.emptyMessage}>
            Your uploaded prescriptions will appear here.
          </Text>
        </View>
      ) : (
        prescriptions.map((item) => (
          <View key={item.id} style={styles.prescriptionCard}>
            <View style={styles.details}>
              <Text style={styles.fileName}>{item.name}</Text>
              <Text style={styles.date}>{item.date}</Text>
            </View>

            <TouchableOpacity
              style={styles.deleteButton}
              onPress={() => deletePrescription(item.id)}
            >
              <Text style={styles.deleteText}>Delete</Text>
            </TouchableOpacity>
          </View>
        ))
      )}
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
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1769AA',
    textAlign: 'center',
    marginTop: 25,
  },
  description: {
    color: '#666',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 10,
    marginBottom: 25,
  },
  emptyCard: {
    backgroundColor: '#FFFFFF',
    padding: 30,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
    elevation: 2,
  },
  emptyIcon: {
    fontSize: 45,
    marginBottom: 15,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  emptyMessage: {
    fontSize: 14,
    color: '#777',
    textAlign: 'center',
    lineHeight: 21,
  },
  prescriptionCard: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  details: {
    flex: 1,
  },
  fileName: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#1769AA',
  },
  date: {
    fontSize: 13,
    color: '#777',
    marginTop: 6,
  },
  deleteButton: {
    backgroundColor: '#FCE8E8',
    padding: 10,
    borderRadius: 8,
    marginLeft: 10,
  },
  deleteText: {
    color: '#C62828',
    fontWeight: 'bold',
  },
});
