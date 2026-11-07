
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
    title: 'AI Medicine Assistant',
    description: 'Ask questions about understanding your medicines.',
    placeholder: 'Type your question here...',
    send: 'Send',
    microphone: '🎤 Voice',
    speaker: '🔊 Speaker',
    welcome: 'Hello! How can I help you understand your medicines?',
    notice: 'AI responses and voice features will be connected to the backend later.',
    back: '‹ Back to Home',
    language: 'Choose Language',
    empty: 'Please enter a message.',
    user: 'You',
    assistant: 'Assistant',
  },
  Tamil: {
    title: 'AI மருந்து உதவியாளர்',
    description: 'உங்கள் மருந்துகளைப் புரிந்துகொள்ள கேள்விகள் கேளுங்கள்.',
    placeholder: 'உங்கள் கேள்வியை இங்கே எழுதுங்கள்...',
    send: 'அனுப்பு',
    microphone: '🎤 குரல்',
    speaker: '🔊 ஒலி',
    welcome: 'வணக்கம்! உங்கள் மருந்துகளைப் புரிந்துகொள்ள நான் எவ்வாறு உதவலாம்?',
    notice: 'AI பதில்கள் மற்றும் குரல் வசதிகள் பின்னர் backend உடன் இணைக்கப்படும்.',
    back: '‹ முகப்புக்குத் திரும்பு',
    language: 'மொழியைத் தேர்ந்தெடுக்கவும்',
    empty: 'தயவுசெய்து ஒரு செய்தியை உள்ளிடவும்.',
    user: 'நீங்கள்',
    assistant: 'உதவியாளர்',
  },
  Hindi: {
    title: 'AI दवा सहायक',
    description: 'अपनी दवाओं को समझने के लिए प्रश्न पूछें।',
    placeholder: 'अपना प्रश्न यहाँ लिखें...',
    send: 'भेजें',
    microphone: '🎤 आवाज़',
    speaker: '🔊 स्पीकर',
    welcome: 'नमस्ते! मैं आपकी दवाओं को समझने में कैसे मदद कर सकता हूँ?',
    notice: 'AI जवाब और आवाज़ की सुविधाएँ बाद में backend से जोड़ी जाएँगी।',
    back: '‹ होम पर वापस जाएँ',
    language: 'भाषा चुनें',
    empty: 'कृपया एक संदेश लिखें।',
    user: 'आप',
    assistant: 'सहायक',
  },
};

export default function AIAssistantScreen({ onBack }) {
  const [language, setLanguage] = useState('English');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);

  const t = translations[language];

  const sendMessage = () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage) {
      Alert.alert(t.title, t.empty);
      return;
    }

    setMessages((previous) => [
      ...previous,
      {
        id: Date.now().toString(),
        text: trimmedMessage,
      },
    ]);

    setMessage('');

    Alert.alert(t.title, t.notice);
  };

  const changeLanguage = (newLanguage) => {
    setLanguage(newLanguage);
  };

  const showVoiceNotice = () => {
    Alert.alert(t.title, t.notice);
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity onPress={onBack}>
        <Text style={styles.backText}>{t.back}</Text>
      </TouchableOpacity>

      <Text style={styles.title}>{t.title}</Text>
      <Text style={styles.description}>{t.description}</Text>

      <View style={styles.languageContainer}>
        <Text style={styles.languageLabel}>{t.language}</Text>

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
                {item === 'Tamil' ? 'தமிழ்' : item === 'Hindi' ? 'हिन्दी' : 'English'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <ScrollView
        style={styles.chatArea}
        contentContainerStyle={styles.chatContent}
      >
        {messages.length === 0 && (
          <View style={styles.welcomeCard}>
            <Text style={styles.welcomeText}>{t.welcome}</Text>
          </View>
        )}

        {messages.map((item) => (
          <View key={item.id} style={styles.messageCard}>
            <Text style={styles.sender}>{t.user}</Text>
            <Text style={styles.messageText}>{item.text}</Text>
          </View>
        ))}
      </ScrollView>

      <View style={styles.voiceRow}>
        <TouchableOpacity
          style={styles.voiceButton}
          onPress={showVoiceNotice}
        >
          <Text style={styles.voiceButtonText}>{t.microphone}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.voiceButton}
          onPress={showVoiceNotice}
        >
          <Text style={styles.voiceButtonText}>{t.speaker}</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          placeholder={t.placeholder}
          placeholderTextColor="#888"
          value={message}
          onChangeText={setMessage}
          multiline
        />

        <TouchableOpacity
          style={styles.sendButton}
          onPress={sendMessage}
        >
          <Text style={styles.sendButtonText}>{t.send}</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.notice}>{t.notice}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F4F8FF',
    padding: 18,
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
    marginTop: 20,
  },
  description: {
    color: '#666',
    fontSize: 13,
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 15,
  },
  languageContainer: {
    backgroundColor: '#FFFFFF',
    padding: 12,
    borderRadius: 10,
    marginBottom: 12,
  },
  languageLabel: {
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  languageRow: {
    flexDirection: 'row',
    gap: 8,
  },
  languageButton: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#DCE5EF',
    borderRadius: 8,
    padding: 10,
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
  chatArea: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
  },
  chatContent: {
    padding: 14,
    flexGrow: 1,
  },
  welcomeCard: {
    backgroundColor: '#E4F1FF',
    padding: 16,
    borderRadius: 12,
    alignSelf: 'flex-start',
    maxWidth: '90%',
    marginTop: 10,
  },
  welcomeText: {
    color: '#245477',
    fontSize: 15,
    lineHeight: 22,
  },
  messageCard: {
    backgroundColor: '#DDEEFF',
    padding: 13,
    borderRadius: 12,
    alignSelf: 'flex-end',
    maxWidth: '90%',
    marginBottom: 12,
  },
  sender: {
    fontWeight: 'bold',
    color: '#1769AA',
    marginBottom: 5,
  },
  messageText: {
    color: '#333',
    fontSize: 15,
    lineHeight: 21,
  },
  voiceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
    gap: 10,
  },
  voiceButton: {
    flex: 1,
    backgroundColor: '#E4F1FF',
    padding: 12,
    borderRadius: 9,
    alignItems: 'center',
  },
  voiceButtonText: {
    color: '#1769AA',
    fontWeight: 'bold',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
    gap: 8,
  },
  input: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#DCE5EF',
    borderRadius: 10,
    padding: 12,
    maxHeight: 100,
    color: '#333',
  },
  sendButton: {
    backgroundColor: '#1769AA',
    paddingVertical: 14,
    paddingHorizontal: 15,
    borderRadius: 9,
  },
  sendButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  notice: {
    fontSize: 11,
    color: '#777',
    textAlign: 'center',
    marginTop: 9,
    marginBottom: 5,
  },
});
