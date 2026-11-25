import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';

import api from '../services/api';

// ── UI text translations ──────────────────────────────────────────────────────
const translations = {
  English: {
    title:           'Prescription Explanation',
    description:     'Medicines extracted from your prescription.',
    language:        'Choose Language',
    prescriptionInfo:'Prescription Information',
    doctorLabel:     'Doctor',
    titleLabel:      'Clinic / Title',
    instructionsLabel:'General Instructions',
    medicinesTitle:  'Medicines',
    nameLabel:       'Medicine Name',
    dosageLabel:     'Dosage',
    frequencyLabel:  'Frequency',
    durationLabel:   'Duration',
    instrLabel:      'Instructions',
    noMedicines:     'No medicines were extracted from this prescription.',
    noMedicinesHint: 'OCR may not have recognised the text clearly. Please consult your doctor or pharmacist for accurate medicine details.',
    notAvailable:    'Not available',
    audio:           '🔊 Listen to Explanation',
    audioNotice:     'Audio playback is not yet connected. A text-to-speech endpoint is not available for prescriptions at this time.',
    warning:         'Important Safety Notice',
    warningText:     'All extracted details must be verified by a qualified healthcare professional before acting on them. Do not use this information as a substitute for medical advice.',
    back:            '‹ Back',
    loading:         'Loading prescription…',
    errorTitle:      'Could Not Load Prescription',
    rawTextTitle:    'Raw OCR Text',
    rawTextHint:     'Medicine details could not be extracted automatically. The raw text from your prescription is shown below for reference.',
    medicine:        'Medicine',
  },
  Tamil: {
    title:           'மருந்துச் சீட்டு விளக்கம்',
    description:     'உங்கள் மருந்துச் சீட்டிலிருந்து பிரித்தெடுக்கப்பட்ட மருந்துகள்.',
    language:        'மொழியைத் தேர்ந்தெடுக்கவும்',
    prescriptionInfo:'மருந்துச் சீட்டு தகவல்',
    doctorLabel:     'மருத்துவர்',
    titleLabel:      'மருத்துவமனை / தலைப்பு',
    instructionsLabel:'பொதுவான அறிவுரைகள்',
    medicinesTitle:  'மருந்துகள்',
    nameLabel:       'மருந்தின் பெயர்',
    dosageLabel:     'மருந்தின் அளவு',
    frequencyLabel:  'எத்தனை முறை',
    durationLabel:   'கால அளவு',
    instrLabel:      'அறிவுரைகள்',
    noMedicines:     'இந்த மருந்துச் சீட்டிலிருந்து மருந்துகள் எடுக்கப்படவில்லை.',
    noMedicinesHint: 'OCR உரையை தெளிவாக அடையாளம் காணவில்லை. சரியான மருந்து விவரங்களுக்கு உங்கள் மருத்துவர் அல்லது மருந்தாளரிடம் ஆலோசிக்கவும்.',
    notAvailable:    'கிடைக்கவில்லை',
    audio:           '🔊 விளக்கத்தைக் கேளுங்கள்',
    audioNotice:     'ஒலி இயக்கம் இன்னும் இணைக்கப்படவில்லை.',
    warning:         'முக்கியமான பாதுகாப்பு அறிவிப்பு',
    warningText:     'பிரித்தெடுக்கப்பட்ட அனைத்து விவரங்களும் தகுதியான சுகாதார நிபுணரால் சரிபார்க்கப்பட வேண்டும். இதை மருத்துவ ஆலோசனைக்கு மாற்றாகப் பயன்படுத்த வேண்டாம்.',
    back:            '‹ பின்செல்',
    loading:         'மருந்துச் சீட்டு ஏற்றுகிறது…',
    errorTitle:      'மருந்துச் சீட்டை ஏற்ற முடியவில்லை',
    rawTextTitle:    'OCR மூல உரை',
    rawTextHint:     'மருந்து விவரங்களை தானாகவே பிரிக்க முடியவில்லை.',
    medicine:        'மருந்து',
  },
  Hindi: {
    title:           'प्रिस्क्रिप्शन की व्याख्या',
    description:     'आपके प्रिस्क्रिप्शन से निकाली गई दवाएँ।',
    language:        'भाषा चुनें',
    prescriptionInfo:'प्रिस्क्रिप्शन जानकारी',
    doctorLabel:     'डॉक्टर',
    titleLabel:      'क्लिनिक / शीर्षक',
    instructionsLabel:'सामान्य निर्देश',
    medicinesTitle:  'दवाएँ',
    nameLabel:       'दवा का नाम',
    dosageLabel:     'मात्रा',
    frequencyLabel:  'कितनी बार',
    durationLabel:   'अवधि',
    instrLabel:      'निर्देश',
    noMedicines:     'इस प्रिस्क्रिप्शन से कोई दवा नहीं निकाली गई।',
    noMedicinesHint: 'OCR ने टेक्स्ट को स्पष्ट रूप से पहचान नहीं पाया। सटीक दवा विवरण के लिए अपने डॉक्टर या फार्मासिस्ट से परामर्श लें।',
    notAvailable:    'उपलब्ध नहीं',
    audio:           '🔊 व्याख्या सुनें',
    audioNotice:     'ऑडियो प्लेबैक अभी तक जुड़ा नहीं है।',
    warning:         'महत्वपूर्ण सुरक्षा सूचना',
    warningText:     'सभी निकाली गई जानकारी को एक योग्य स्वास्थ्य पेशेवर द्वारा सत्यापित किया जाना चाहिए। इसे चिकित्सा सलाह के विकल्प के रूप में उपयोग न करें।',
    back:            '‹ वापस',
    loading:         'प्रिस्क्रिप्शन लोड हो रहा है…',
    errorTitle:      'प्रिस्क्रिप्शन लोड नहीं हो सका',
    rawTextTitle:    'OCR मूल पाठ',
    rawTextHint:     'दवा विवरण स्वचालित रूप से निकालना संभव नहीं था।',
    medicine:        'दवा',
  },
};

// ── Helper: safe field display ────────────────────────────────────────────────
function fieldValue(val, fallback) {
  if (val === null || val === undefined || String(val).trim() === '') {
    return fallback;
  }
  return String(val).trim();
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function PrescriptionExplanationScreen({ onBack, prescription: initialPrescription }) {
  const [language, setLanguage]         = useState('English');
  const [prescription, setPrescription] = useState(initialPrescription || null);
  const [loading, setLoading]           = useState(!initialPrescription);
  const [loadError, setLoadError]       = useState(null);

  const t = translations[language];

  // If we were passed a full prescription object directly from upload, use it.
  // If we were passed only an id (legacy path), fetch it.
  useEffect(() => {
    if (initialPrescription && typeof initialPrescription === 'object' && initialPrescription.id) {
      // Already have the full object from the upload response
      setPrescription(initialPrescription);
      setLoading(false);
      return;
    }

    if (initialPrescription && typeof initialPrescription === 'string') {
      // Passed as an ID string — fetch the full object
      fetchPrescription(initialPrescription);
      return;
    }

    // Nothing passed — nothing to show
    setLoading(false);
    setLoadError('No prescription data was provided.');
  }, []);

  const fetchPrescription = async (id) => {
    setLoading(true);
    setLoadError(null);
    const result = await api.get(`/prescriptions/${id}`);
    setLoading(false);
    if (result.error) {
      setLoadError(result.message);
    } else {
      setPrescription(result);
    }
  };

  const showAudioNotice = () => {
    Alert.alert(t.title, t.audioNotice);
  };

  // ── Loading state ──────────────────────────────────────────────────────────
  if (loading) {
    return (
      <View style={styles.centeredContainer}>
        <ActivityIndicator size="large" color="#1769AA" />
        <Text style={styles.loadingText}>{t.loading}</Text>
      </View>
    );
  }

  // ── Error state ────────────────────────────────────────────────────────────
  if (loadError) {
    return (
      <View style={styles.centeredContainer}>
        <Text style={styles.errorIcon}>⚠️</Text>
        <Text style={styles.errorTitle}>{t.errorTitle}</Text>
        <Text style={styles.errorMessage}>{loadError}</Text>
        <TouchableOpacity style={styles.backButtonLarge} onPress={onBack}>
          <Text style={styles.backButtonLargeText}>{t.back}</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // ── Data ───────────────────────────────────────────────────────────────────
  const medicines        = prescription?.medicines || [];
  const hasNoMedicines   = medicines.length === 0;
  const hasRawText       = !!(prescription?.raw_text && prescription.raw_text.trim());
  // OCR ran but LLM extraction returned nothing useful
  const ocrOnlyMode      = hasNoMedicines && hasRawText;

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {/* Back */}
      <TouchableOpacity onPress={onBack}>
        <Text style={styles.backText}>{t.back}</Text>
      </TouchableOpacity>

      <Text style={styles.title}>{t.title}</Text>
      <Text style={styles.description}>{t.description}</Text>

      {/* Language selector */}
      <View style={styles.card}>
        <Text style={styles.sectionTitle}>{t.language}</Text>
        <View style={styles.languageRow}>
          {['English', 'Tamil', 'Hindi'].map((lang) => (
            <TouchableOpacity
              key={lang}
              style={[styles.languageButton, language === lang && styles.selectedLanguage]}
              onPress={() => setLanguage(lang)}
            >
              <Text style={[styles.languageText, language === lang && styles.selectedLanguageText]}>
                {lang === 'Tamil' ? 'தமிழ்' : lang === 'Hindi' ? 'हिन्दी' : 'English'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Prescription meta info */}
      {(prescription?.doctor || prescription?.title || prescription?.instructions) && (
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t.prescriptionInfo}</Text>

          {prescription?.doctor && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>{t.doctorLabel}</Text>
              <Text style={styles.detailValue}>{prescription.doctor}</Text>
            </View>
          )}
          {prescription?.title && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>{t.titleLabel}</Text>
              <Text style={styles.detailValue}>{prescription.title}</Text>
            </View>
          )}
          {prescription?.instructions && (
            <View style={[styles.detailRow, { flexDirection: 'column', alignItems: 'flex-start' }]}>
              <Text style={styles.detailLabel}>{t.instructionsLabel}</Text>
              <Text style={[styles.detailValue, { marginTop: 4 }]}>{prescription.instructions}</Text>
            </View>
          )}
        </View>
      )}

      {/* OCR-only warning: text extracted but no medicines parsed */}
      {ocrOnlyMode && (
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>⚠️ {t.noMedicines}</Text>
          <Text style={styles.infoText}>{t.noMedicinesHint}</Text>
          <Text style={styles.sectionTitle2}>{t.rawTextTitle}</Text>
          <Text style={styles.infoHint}>{t.rawTextHint}</Text>
          <Text style={styles.rawText}>{prescription.raw_text}</Text>
        </View>
      )}

      {/* No text at all */}
      {hasNoMedicines && !hasRawText && (
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>⚠️ {t.noMedicines}</Text>
          <Text style={styles.infoText}>{t.noMedicinesHint}</Text>
        </View>
      )}

      {/* Medicine cards — one per extracted medicine */}
      {medicines.map((med, idx) => (
        <View key={idx} style={styles.card}>
          <Text style={styles.sectionTitle}>
            {t.medicine} {medicines.length > 1 ? idx + 1 : ''}
          </Text>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>{t.nameLabel}</Text>
            <Text style={[styles.detailValue, styles.medicineName]}>
              {fieldValue(med.name, t.notAvailable)}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>{t.dosageLabel}</Text>
            <Text style={styles.detailValue}>
              {fieldValue(med.dosage, t.notAvailable)}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>{t.frequencyLabel}</Text>
            <Text style={styles.detailValue}>
              {fieldValue(med.frequency, t.notAvailable)}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>{t.durationLabel}</Text>
            <Text style={styles.detailValue}>
              {fieldValue(med.duration, t.notAvailable)}
            </Text>
          </View>

          {med.instructions && (
            <View style={[styles.detailRow, { flexDirection: 'column', alignItems: 'flex-start' }]}>
              <Text style={styles.detailLabel}>{t.instrLabel}</Text>
              <Text style={[styles.detailValue, { marginTop: 4 }]}>{med.instructions}</Text>
            </View>
          )}
        </View>
      ))}

      {/* Audio — not connected */}
      <View style={styles.card}>
        <TouchableOpacity style={styles.audioButton} onPress={showAudioNotice}>
          <Text style={styles.audioButtonText}>{t.audio}</Text>
        </TouchableOpacity>
        <Text style={styles.audioNoticeText}>{t.audioNotice}</Text>
      </View>

      {/* Safety warning — always shown */}
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
  centeredContainer: {
    flex: 1,
    backgroundColor: '#F4F8FF',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 30,
  },
  loadingText: {
    marginTop: 14,
    color: '#1769AA',
    fontSize: 15,
  },
  errorIcon: {
    fontSize: 40,
    marginBottom: 12,
  },
  errorTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#C62828',
    textAlign: 'center',
    marginBottom: 10,
  },
  errorMessage: {
    fontSize: 14,
    color: '#555',
    textAlign: 'center',
    lineHeight: 21,
    marginBottom: 24,
  },
  backButtonLarge: {
    backgroundColor: '#1769AA',
    paddingVertical: 13,
    paddingHorizontal: 30,
    borderRadius: 9,
  },
  backButtonLargeText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 15,
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
    marginBottom: 12,
  },
  sectionTitle2: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#555',
    marginTop: 14,
    marginBottom: 6,
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
    paddingVertical: 11,
    borderBottomWidth: 1,
    borderBottomColor: '#EDF1F5',
    flexWrap: 'wrap',
  },
  detailLabel: {
    color: '#555',
    fontWeight: 'bold',
    flex: 1,
    marginRight: 8,
  },
  detailValue: {
    color: '#333',
    flex: 2,
    textAlign: 'right',
  },
  medicineName: {
    fontWeight: 'bold',
    color: '#1769AA',
  },
  infoCard: {
    backgroundColor: '#FFF4E5',
    padding: 17,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#F1D4A8',
  },
  infoTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#9A5B00',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 13,
    color: '#76511E',
    lineHeight: 20,
  },
  infoHint: {
    fontSize: 12,
    color: '#9A5B00',
    marginBottom: 8,
  },
  rawText: {
    fontSize: 12,
    color: '#555',
    fontFamily: 'monospace',
    lineHeight: 18,
    backgroundColor: '#FAFAFA',
    padding: 10,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  audioButton: {
    backgroundColor: '#1769AA',
    padding: 14,
    borderRadius: 9,
    alignItems: 'center',
  },
  audioButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  audioNoticeText: {
    color: '#888',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 17,
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
