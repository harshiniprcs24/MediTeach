
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

const translations = {
  English: {
    title: 'Medicine Reminders',
    description: 'Manage your medicine schedule.',
    language: 'Choose Language',
    medicine: 'Medicine Name',
    dosage: 'Dosage',
    time: 'Reminder Time',
    medicinePlaceholder: 'Enter medicine name',
    dosagePlaceholder: 'Example: 1 tablet',
    timePlaceholder: 'Example: 8:00 AM',
    add: 'Add Reminder',
    empty: 'No reminders added yet.',
    delete: 'Delete',
    back: '‹ Back to Home',
    fillFields: 'Please fill in all fields.',
    success: 'Reminder added successfully.',
    deleteTitle: 'Delete Reminder',
    deleteMessage: 'Are you sure you want to delete this reminder?',
    cancel: 'Cancel',
    reminderNote: 'Scheduled notifications will be connected later.',
  },
  Tamil: {
    title: 'மருந்து நினைவூட்டல்கள்',
    description: 'உங்கள் மருந்து அட்டவணையை நிர்வகிக்கவும்.',
    language: 'மொழியைத் தேர்ந்தெடுக்கவும்',
    medicine: 'மருந்தின் பெயர்',
    dosage: 'மருந்தின் அளவு',
    time: 'நினைவூட்டும் நேரம்',
    medicinePlaceholder: 'மருந்தின் பெயரை உள்ளிடவும்',
    dosagePlaceholder: 'உதாரணம்: 1 மாத்திரை',
    timePlaceholder: 'உதாரணம்: காலை 8:00',
    add: 'நினைவூட்டலைச் சேர்க்கவும்',
    empty: 'இதுவரை நினைவூட்டல்கள் சேர்க்கப்படவில்லை.',
    delete: 'நீக்கு',
    back: '‹ முகப்புக்குத் திரும்பு',
    fillFields: 'அனைத்து விவரங்களையும் உள்ளிடவும்.',
    success: 'நினைவூட்டல் வெற்றிகரமாகச் சேர்க்கப்பட்டது.',
    deleteTitle: 'நினைவூட்டலை நீக்கவும்',
    deleteMessage: 'இந்த நினைவூட்டலை நீக்க விரும்புகிறீர்களா?',
    cancel: 'ரத்து செய்',
    reminderNote: 'அறிவிப்புகள் பின்னர் இணைக்கப்படும்.',
  },
  Hindi: {
    title: 'दवा रिमाइंडर',
    description: 'अपनी दवा समय-सारणी प्रबंधित करें।',
    language: 'भाषा चुनें',
    medicine: 'दवा का नाम',
    dosage: 'दवा की मात्रा',
    time: 'रिमाइंडर का समय',
    medicinePlaceholder: 'दवा का नाम लिखें',
    dosagePlaceholder: 'उदाहरण: 1 गोली',
    timePlaceholder: 'उदाहरण: सुबह 8:00',
    add: 'रिमाइंडर जोड़ें',
    empty: 'अभी तक कोई रिमाइंडर नहीं जोड़ा गया है।',
    delete: 'हटाएँ',
    back: '‹ होम पर वापस जाएँ',
    fillFields: 'कृपया सभी जानकारी भरें।',
    success: 'रिमाइंडर सफलतापूर्वक जोड़ा गया।',
    deleteTitle: 'रिमाइंडर हटाएँ',
    deleteMessage: 'क्या आप इस रिमाइंडर को हटाना चाहते हैं?',
    cancel: 'रद्द करें',
    reminderNote: 'सूचनाएँ बाद में जोड़ी जाएँगी।',
  },
};

export default function RemindersScreen({ onBack }) {
  const [language, setLanguage] = useState('English');
  const [medicineName, setMedicineName] = useState('');
  const [dosage, setDosage] = useState('');
  const [time, setTime] = useState('');
  const [reminders, setReminders] = useState([]);

  const t = translations[language];

  const addReminder = () => {
    if (!medicineName.trim() || !dosage.trim() || !time.trim()) {
      Alert.alert(t.title, t.fillFields);
      return;
    }

    const newReminder = {
      id: Date.now().toString(),
      medicineName: medicineName.trim(),
      dosage: dosage.trim(),
      time: time.trim(),
    };

    setReminders((previous) => [...previous, newReminder]);

    setMedicineName('');
    setDosage('');
    setTime('');

    Alert.alert(t.title, t.success);
  };

  const deleteReminder = (id) => {
    Alert.alert(t.deleteTitle, t.deleteMessage, [
      {
        text: t.cancel,
        style: 'cancel',
      },
      {
        text: t.delete,
        style: 'destructive',
        onPress: () => {
          setReminders((previous) =>
            previous.filter((item) => item.id !== id)
          );
        },
      },
    ]);
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TouchableOpacity onPress={onBack}>
        <Text style={styles.backText}>{t.back}</Text>
      </TouchableOpacity>

      <Text style={styles.title}>{t.title}</Text>
      <Text style={styles.description}>{t.description}</Text>

      <View style={styles.languageCard}>
        <Text style={styles.label}>{t.language}</Text>

        <View style={styles.languageRow}>
          {['English', 'Tamil', 'Hindi'].map((item) => (
            <TouchableOpacity
              key={item}
              style={[
                styles.languageButton,
                language === item && styles.selectedLanguage,
              ]}
              onPress={() => setLanguage(item)}
            >
              <Text
                style={[
                  styles.languageText,
                  language === item && styles.selectedLanguageText,
                ]}
              >
                {item === 'Tamil' ? 'தமிழ்' : item === 'Hindi' ? 'हिन्दी' : 'English'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.formCard}>
        <Text style={styles.label}>{t.medicine}</Text>
        <TextInput
          style={styles.input}
          placeholder={t.medicinePlaceholder}
          value={medicineName}
          onChangeText={setMedicineName}
        />

        <Text style={styles.label}>{t.dosage}</Text>
        <TextInput
          style={styles.input}
          placeholder={t.dosagePlaceholder}
          value={dosage}
          onChangeText={setDosage}
        />

        <Text style={styles.label}>{t.time}</Text>
        <TextInput
          style={styles.input}
          placeholder={t.timePlaceholder}
          value={time}
          onChangeText={setTime}
        />

        <TouchableOpacity
          style={styles.addButton}
          onPress={addReminder}
        >
          <Text style={styles.addButtonText}>{t.add}</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionTitle}>{t.title}</Text>

      {reminders.length === 0 ? (
        <Text style={styles.emptyText}>{t.empty}</Text>
      ) : (
        reminders.map((item) => (
          <View key={item.id} style={styles.reminderCard}>
            <View style={styles.reminderDetails}>
              <Text style={styles.medicineName}>
                {item.medicineName}
              </Text>
              <Text style={styles.reminderInfo}>{item.dosage}</Text>
              <Text style={styles.reminderTime}>{item.time}</Text>
            </View>

            <TouchableOpacity
              style={styles.deleteButton}
              onPress={() => deleteReminder(item.id)}
            >
              <Text style={styles.deleteButtonText}>{t.delete}</Text>
            </TouchableOpacity>
          </View>
        ))
      )}

      <Text style={styles.note}>{t.reminderNote}</Text>
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
    marginTop: 22,
  },
  description: {
    color: '#666',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 20,
  },
  languageCard: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 12,
    marginBottom: 18,
  },
  languageRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 10,
  },
  languageButton: {
    flex: 1,
    padding: 10,
    borderWidth: 1,
    borderColor: '#DCE5EF',
    borderRadius: 8,
    alignItems: 'center',
  },
  selectedLanguage: {
    backgroundColor: '#1769AA',
    borderColor: '#1769AA',
  },
  languageText: {
    color: '#333',
    fontWeight: 'bold',
  },
  selectedLanguageText: {
    color: '#FFFFFF',
  },
  formCard: {
    backgroundColor: '#FFFFFF',
    padding: 18,
    borderRadius: 12,
    elevation: 2,
  },
  label: {
    color: '#333',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#DCE5EF',
    borderRadius: 8,
    padding: 13,
    marginBottom: 15,
    color: '#333',
  },
  addButton: {
    backgroundColor: '#1769AA',
    padding: 15,
    borderRadius: 9,
    alignItems: 'center',
  },
  addButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 15,
  },
  sectionTitle: {
    color: '#1769AA',
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 25,
    marginBottom: 12,
  },
  emptyText: {
    color: '#777',
    textAlign: 'center',
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
  },
  reminderCard: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
    marginBottom: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  reminderDetails: {
    flex: 1,
  },
  medicineName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1769AA',
  },
  reminderInfo: {
    color: '#555',
    marginTop: 5,
  },
  reminderTime: {
    color: '#333',
    fontWeight: 'bold',
    marginTop: 5,
  },
  deleteButton: {
    backgroundColor: '#FCE8E8',
    padding: 10,
    borderRadius: 8,
    marginLeft: 10,
  },
  deleteButtonText: {
    color: '#C62828',
    fontWeight: 'bold',
  },
  note: {
    color: '#777',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 18,
    marginBottom: 15,
  },
});
