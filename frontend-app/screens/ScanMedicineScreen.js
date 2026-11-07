
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
  Alert,
} from 'react-native';

import * as ImagePicker from 'expo-image-picker';

const translations = {
  English: {
    title: 'Medicine Scanner',
    description: 'Scan a tablet or medicine package.',
    language: 'Choose Language',
    gallery: 'Choose from Gallery',
    camera: 'Capture with Camera',
    selected: 'Selected Medicine Image',
    remove: 'Remove Image',
    scan: 'Identify Medicine',
    result: 'Identification Result',
    resultMessage: 'Medicine identification will appear here after AI model integration.',
    pending: 'Waiting for medicine image identification.',
    warning: 'Important Safety Notice',
    warningText: 'Do not take a medicine based only on image identification. Verify its identity with a qualified healthcare professional or pharmacist.',
    back: '‹ Back to Home',
    permission: 'Camera or gallery permission is required.',
    noImage: 'Please select or capture a medicine image first.',
    unavailable: 'Medicine identification will be connected through the backend later.',
  },
  Tamil: {
    title: 'மருந்து ஸ்கேனர்',
    description: 'மாத்திரை அல்லது மருந்துப் பெட்டியை ஸ்கேன் செய்யவும்.',
    language: 'மொழியைத் தேர்ந்தெடுக்கவும்',
    gallery: 'புகைப்படத் தொகுப்பிலிருந்து தேர்ந்தெடுக்கவும்',
    camera: 'கேமரா மூலம் படம் எடுக்கவும்',
    selected: 'தேர்ந்தெடுக்கப்பட்ட மருந்துப் படம்',
    remove: 'படத்தை நீக்கவும்',
    scan: 'மருந்தை அடையாளம் காணவும்',
    result: 'அடையாளம் காணப்பட்ட விவரம்',
    resultMessage: 'AI மாடல் இணைக்கப்பட்ட பிறகு மருந்து விவரங்கள் இங்கே தோன்றும்.',
    pending: 'மருந்துப் படம் அடையாளம் காணப்படுவதற்காக காத்திருக்கிறது.',
    warning: 'முக்கியமான பாதுகாப்பு அறிவிப்பு',
    warningText: 'படத்தை மட்டும் வைத்து மருந்தை எடுத்துக்கொள்ள வேண்டாம். தகுதியான சுகாதார நிபுணர் அல்லது மருந்தாளரிடம் சரிபார்க்கவும்.',
    back: '‹ முகப்புக்குத் திரும்பு',
    permission: 'கேமரா அல்லது புகைப்படத் தொகுப்பு அனுமதி தேவை.',
    noImage: 'முதலில் மருந்துப் படத்தைத் தேர்ந்தெடுக்கவும் அல்லது எடுக்கவும்.',
    unavailable: 'மருந்து அடையாளம் காணும் வசதி பின்னர் backend உடன் இணைக்கப்படும்.',
  },
  Hindi: {
    title: 'दवा स्कैनर',
    description: 'गोली या दवा के पैकेट को स्कैन करें।',
    language: 'भाषा चुनें',
    gallery: 'गैलरी से चुनें',
    camera: 'कैमरे से फोटो लें',
    selected: 'चुनी गई दवा की तस्वीर',
    remove: 'तस्वीर हटाएँ',
    scan: 'दवा की पहचान करें',
    result: 'पहचान का परिणाम',
    resultMessage: 'AI मॉडल जुड़ने के बाद दवा की पहचान यहाँ दिखाई देगी।',
    pending: 'दवा की तस्वीर की पहचान की प्रतीक्षा है।',
    warning: 'महत्वपूर्ण सुरक्षा सूचना',
    warningText: 'केवल तस्वीर के आधार पर दवा न लें। योग्य स्वास्थ्य विशेषज्ञ या फार्मासिस्ट से उसकी पहचान की पुष्टि करें।',
    back: '‹ होम पर वापस जाएँ',
    permission: 'कैमरा या गैलरी की अनुमति आवश्यक है।',
    noImage: 'कृपया पहले दवा की तस्वीर चुनें या लें।',
    unavailable: 'दवा पहचानने की सुविधा बाद में backend से जोड़ी जाएगी।',
  },
};

export default function ScanMedicineScreen({ onBack }) {
  const [language, setLanguage] = useState('English');
  const [selectedImage, setSelectedImage] = useState(null);
  const [scanStarted, setScanStarted] = useState(false);

  const t = translations[language];

  const chooseFromGallery = async () => {
    const permission =
      await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permission.granted) {
      Alert.alert(t.title, t.permission);
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: false,
      quality: 1,
    });

    if (!result.canceled && result.assets.length > 0) {
      setSelectedImage(result.assets[0].uri);
      setScanStarted(false);
    }
  };

  const captureImage = async () => {
    const permission =
      await ImagePicker.requestCameraPermissionsAsync();

    if (!permission.granted) {
      Alert.alert(t.title, t.permission);
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ['images'],
      allowsEditing: false,
      quality: 1,
    });

    if (!result.canceled && result.assets.length > 0) {
      setSelectedImage(result.assets[0].uri);
      setScanStarted(false);
    }
  };

  const identifyMedicine = () => {
    if (!selectedImage) {
      Alert.alert(t.title, t.noImage);
      return;
    }

    setScanStarted(true);
    Alert.alert(t.title, t.unavailable);
  };

  const removeImage = () => {
    setSelectedImage(null);
    setScanStarted(false);
  };

  const changeLanguage = (newLanguage) => {
    setLanguage(newLanguage);
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
              onPress={() => changeLanguage(item)}
            >
              <Text
                style={[
                  styles.languageText,
                  language === item && styles.selectedLanguageText,
                ]}
              >
                {item === 'Tamil'
                  ? 'தமிழ்'
                  : item === 'Hindi'
                    ? 'हिन्दी'
                    : 'English'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.card}>
        <TouchableOpacity
          style={styles.optionButton}
          onPress={chooseFromGallery}
        >
          <Text style={styles.optionText}>🖼️ {t.gallery}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.optionButton}
          onPress={captureImage}
        >
          <Text style={styles.optionText}>📷 {t.camera}</Text>
        </TouchableOpacity>
      </View>

      {selectedImage && (
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t.selected}</Text>

          <Image
            source={{ uri: selectedImage }}
            style={styles.preview}
            resizeMode="contain"
          />

          <TouchableOpacity
            style={styles.removeButton}
            onPress={removeImage}
          >
            <Text style={styles.removeText}>{t.remove}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.scanButton}
            onPress={identifyMedicine}
          >
            <Text style={styles.scanButtonText}>{t.scan}</Text>
          </TouchableOpacity>
        </View>
      )}

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>{t.result}</Text>

        <Text style={styles.resultText}>
          {scanStarted ? t.resultMessage : t.pending}
        </Text>
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
    marginBottom: 14,
  },
  languageRow: {
    flexDirection: 'row',
    gap: 8,
  },
  languageButton: {
    flex: 1,
    padding: 11,
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
  optionButton: {
    backgroundColor: '#E4F1FF',
    padding: 16,
    borderRadius: 9,
    alignItems: 'center',
    marginBottom: 12,
  },
  optionText: {
    color: '#1769AA',
    fontWeight: 'bold',
    fontSize: 15,
  },
  preview: {
    width: '100%',
    height: 230,
    backgroundColor: '#F8FAFC',
    borderRadius: 9,
  },
  removeButton: {
    backgroundColor: '#FCE8E8',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 12,
  },
  removeText: {
    color: '#C62828',
    fontWeight: 'bold',
  },
  scanButton: {
    backgroundColor: '#1769AA',
    padding: 15,
    borderRadius: 9,
    alignItems: 'center',
    marginTop: 12,
  },
  scanButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: 'bold',
  },
  resultText: {
    color: '#666',
    fontSize: 14,
    lineHeight: 22,
  },
  warningCard: {
    backgroundColor: '#FFF4E5',
    padding: 17,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#F1D4A8',
    marginBottom: 20,
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
