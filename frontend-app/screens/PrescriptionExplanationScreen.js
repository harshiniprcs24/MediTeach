
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';

const translations = {
  English: {
    title: 'Prescription Explanation',
    description: 'Understand your prescription in your preferred language.',
    language: 'Choose Language',
    medicineDetails: 'Prescription Details',
    medicineName: 'Medicine Name',
    dosage: 'Dosage',
    frequency: 'Frequency',
    duration: 'Duration',
    pending: 'Details will appear after prescription processing.',
    explanation: 'Medicine Explanation',
    explanationText: 'Your prescription will be explained here in simple language after the details have been extracted and verified.',
    audio: '🔊 Listen to Explanation',
    audioNotice: 'Audio explanation will be available after text-to-speech integration.',
    warning: 'Important Safety Notice',
    warningText: 'If any prescription detail is unclear, consult a qualified healthcare professional. Do not guess medicine names or dosages.',
    back: '‹ Back',
  },

  Tamil: {
    title: 'மருந்துச் சீட்டு விளக்கம்',
    description: 'உங்களுக்கு விருப்பமான மொழியில் மருந்துச் சீட்டைப் புரிந்துகொள்ளுங்கள்.',
    language: 'மொழியைத் தேர்ந்தெடுக்கவும்',
    medicineDetails: 'மருந்துச் சீட்டு விவரங்கள்',
    medicineName: 'மருந்தின் பெயர்',
    dosage: 'மருந்தின் அளவு',
    frequency: 'எத்தனை முறை',
    duration: 'கால அளவு',
    pending: 'மருந்துச் சீட்டு செயலாக்கப்பட்ட பிறகு விவரங்கள் தோன்றும்.',
    explanation: 'மருந்து விளக்கம்',
    explanationText: 'விவரங்கள் பிரித்தெடுக்கப்பட்டு சரிபார்க்கப்பட்ட பிறகு, மருந்துச் சீட்டு எளிய மொழியில் இங்கே விளக்கப்படும்.',
    audio: '🔊 விளக்கத்தைக் கேளுங்கள்',
    audioNotice: 'உரை-முதல்-குரல் வசதி இணைக்கப்பட்ட பிறகு ஒலி விளக்கம் கிடைக்கும்.',
    warning: 'முக்கியமான பாதுகாப்பு அறிவிப்பு',
    warningText: 'மருந்துச் சீட்டில் ஏதேனும் விவரம் தெளிவாக இல்லாவிட்டால் தகுதியான சுகாதார நிபுணரை அணுகவும். மருந்தின் பெயர் அல்லது அளவை ஊகிக்க வேண்டாம்.',
    back: '‹ பின்செல்',
  },

  Hindi: {
    title: 'प्रिस्क्रिप्शन की व्याख्या',
    description: 'अपनी पसंदीदा भाषा में प्रिस्क्रिप्शन समझें।',
    language: 'भाषा चुनें',
    medicineDetails: 'प्रिस्क्रिप्शन का विवरण',
    medicineName: 'दवा का नाम',
    dosage: 'दवा की मात्रा',
    frequency: 'कितनी बार',
    duration: 'अवधि',
    pending: 'प्रिस्क्रिप्शन प्रोसेस होने के बाद विवरण दिखाई देंगे।',
    explanation: 'दवा की व्याख्या',
    explanationText: 'विवरण निकालने और सत्यापित करने के बाद प्रिस्क्रिप्शन को यहाँ सरल भाषा में समझाया जाएगा।',
    audio: '🔊 व्याख्या सुनें',
    audioNotice: 'टेक्स्ट-टू-स्पीच सुविधा जुड़ने के बाद ऑडियो व्याख्या उपलब्ध होगी।',
    warning: 'महत्वपूर्ण सुरक्षा सूचना',
    warningText: 'यदि प्रिस्क्रिप्शन का कोई विवरण स्पष्ट नहीं है, तो योग्य स्वास्थ्य विशेषज्ञ से सलाह लें। दवा के नाम या मात्रा का अनुमान न लगाएँ।',
    back: '‹ वापस जाएँ',
  },
};

export default function PrescriptionExplanationScreen({ onBack }) {
  const [language, setLanguage] = useState('English');

  const t = translations[language];

  const showAudioNotice = () => {
    Alert.alert(t.title, t.audioNotice);
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TouchableOpacity onPress={onBack}>
        <Text style={styles.backText}>{t.back}</Text>
      </TouchableOpacity>

      <Text style={styles.title}>{t.title}</Text>
      <Text style={styles.description}>{t.description}</Text>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>{t.language}</Text>

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

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>{t.medicineDetails}</Text>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>{t.medicineName}</Text>
          <Text style={styles.detailValue}>--</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>{t.dosage}</Text>
          <Text style={styles.detailValue}>--</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>{t.frequency}</Text>
          <Text style={styles.detailValue}>--</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>{t.duration}</Text>
          <Text style={styles.detailValue}>--</Text>
        </View>

        <Text style={styles.pendingText}>{t.pending}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>{t.explanation}</Text>

        <Text style={styles.explanationText}>
          {t.explanationText}
        </Text>

        <TouchableOpacity
          style={styles.audioButton}
          onPress={showAudioNotice}
        >
          <Text style={styles.audioButtonText}>{t.audio}</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.warningCard}>
        <Text style={styles.warningTitle}>{t.warning}</Text>
        <Text style={styles.warningText}>{t.warningText}</Text>
      </View>
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
    fontSize: 23,
    fontWeight: 'bold',
    color: '#1769AA',
    textAlign: 'center',
    marginTop: 22,
  },
  description: {
    fontSize: 13,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 20,
  },
  card: {
    backgroundColor: '#FFFFFF',
    padding: 17,
    borderRadius: 12,
    marginBottom: 16,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: 'bold',
    color: '#1769AA',
    marginBottom: 15,
  },
  languageRow: {
    flexDirection: 'row',
    gap: 8,
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
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#EDF1F5',
  },
  detailLabel: {
    color: '#555',
    fontWeight: 'bold',
    flex: 1,
  },
  detailValue: {
    color: '#777',
  },
  pendingText: {
    color: '#777',
    fontSize: 12,
    marginTop: 14,
    lineHeight: 19,
  },
  explanationText: {
    color: '#444',
    fontSize: 14,
    lineHeight: 23,
  },
  audioButton: {
    backgroundColor: '#1769AA',
    padding: 14,
    borderRadius: 9,
    alignItems: 'center',
    marginTop: 18,
  },
  audioButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  warningCard: {
    backgroundColor: '#FFF4E5',
    borderRadius: 12,
    padding: 17,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#F1D4A8',
  },
  warningTitle: {
    color: '#9A5B00',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  warningText: {
    color: '#76511E',
    fontSize: 13,
    lineHeight: 21,
  },
});
