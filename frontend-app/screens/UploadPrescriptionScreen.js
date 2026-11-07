
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Image,
} from 'react-native';

import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';

export default function UploadPrescriptionScreen({ onBack, onContinue }) {
  const [selectedFile, setSelectedFile] = useState(null);

  const selectImage = async () => {
    const permission =
      await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permission.granted) {
      Alert.alert(
        'Permission Required',
        'Please allow gallery access to select a prescription.'
      );
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: false,
      quality: 1,
    });

    if (!result.canceled && result.assets.length > 0) {
      const file = result.assets[0];

      setSelectedFile({
        uri: file.uri,
        name: file.fileName || 'Prescription Image',
        type: 'image',
      });
    }
  };

  const takePhoto = async () => {
    const permission =
      await ImagePicker.requestCameraPermissionsAsync();

    if (!permission.granted) {
      Alert.alert(
        'Permission Required',
        'Please allow camera access to take a prescription photo.'
      );
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ['images'],
      allowsEditing: false,
      quality: 1,
    });

    if (!result.canceled && result.assets.length > 0) {
      const file = result.assets[0];

      setSelectedFile({
        uri: file.uri,
        name: file.fileName || 'Prescription Photo',
        type: 'image',
      });
    }
  };

  const selectPDF = async () => {
    const result = await DocumentPicker.getDocumentAsync({
      type: 'application/pdf',
      copyToCacheDirectory: true,
    });

    if (!result.canceled && result.assets.length > 0) {
      const file = result.assets[0];

      setSelectedFile({
        uri: file.uri,
        name: file.name,
        type: 'pdf',
      });
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
  };

  const continueToExplanation = () => {
    if (!selectedFile) {
      Alert.alert(
        'No Prescription Selected',
        'Please select or capture a prescription first.'
      );
      return;
    }

    if (onContinue) {
      onContinue();
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TouchableOpacity onPress={onBack}>
        <Text style={styles.backText}>‹ Back to Home</Text>
      </TouchableOpacity>

      <Text style={styles.title}>Upload Prescription</Text>

      <Text style={styles.description}>
        Upload your prescription as an image or PDF file.
      </Text>

      <View style={styles.uploadCard}>
        <Text style={styles.uploadIcon}>📄</Text>

        <Text style={styles.uploadHeading}>
          Select Your Prescription
        </Text>

        <Text style={styles.uploadDescription}>
          Choose an image from your gallery, take a photo, or upload a PDF.
        </Text>

        <TouchableOpacity
          style={styles.optionButton}
          onPress={selectImage}
        >
          <Text style={styles.optionButtonText}>
            🖼️ Choose from Gallery
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.optionButton}
          onPress={takePhoto}
        >
          <Text style={styles.optionButtonText}>
            📷 Take a Photo
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.optionButton}
          onPress={selectPDF}
        >
          <Text style={styles.optionButtonText}>
            📑 Upload PDF
          </Text>
        </TouchableOpacity>
      </View>

      {selectedFile && (
        <View style={styles.fileCard}>
          <Text style={styles.fileHeading}>Selected Prescription</Text>

          {selectedFile.type === 'image' && (
            <Image
              source={{ uri: selectedFile.uri }}
              style={styles.preview}
              resizeMode="contain"
            />
          )}

          <Text style={styles.fileName}>{selectedFile.name}</Text>

          <TouchableOpacity
            style={styles.removeButton}
            onPress={removeFile}
          >
            <Text style={styles.removeButtonText}>Remove File</Text>
          </TouchableOpacity>
        </View>
      )}

      <TouchableOpacity
        style={[
          styles.continueButton,
          !selectedFile && styles.disabledButton,
        ]}
        onPress={continueToExplanation}
      >
        <Text style={styles.continueButtonText}>Continue</Text>
      </TouchableOpacity>

      <Text style={styles.note}>
        Prescription extraction and medicine explanation will be connected
        through the backend later. Unclear details must be verified by a
        qualified healthcare professional.
      </Text>
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
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 10,
    marginBottom: 25,
  },
  uploadCard: {
    backgroundColor: '#FFFFFF',
    padding: 22,
    borderRadius: 12,
    alignItems: 'center',
    elevation: 2,
  },
  uploadIcon: {
    fontSize: 45,
    marginBottom: 12,
  },
  uploadHeading: {
    fontSize: 19,
    fontWeight: 'bold',
    color: '#333',
  },
  uploadDescription: {
    fontSize: 13,
    color: '#777',
    textAlign: 'center',
    lineHeight: 20,
    marginTop: 10,
    marginBottom: 20,
  },
  optionButton: {
    width: '100%',
    backgroundColor: '#E4F1FF',
    padding: 15,
    borderRadius: 9,
    alignItems: 'center',
    marginBottom: 12,
  },
  optionButtonText: {
    color: '#1769AA',
    fontSize: 15,
    fontWeight: 'bold',
  },
  fileCard: {
    backgroundColor: '#FFFFFF',
    padding: 17,
    borderRadius: 12,
    marginTop: 20,
    alignItems: 'center',
  },
  fileHeading: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1769AA',
    marginBottom: 12,
  },
  preview: {
    width: '100%',
    height: 180,
    marginBottom: 12,
  },
  fileName: {
    color: '#333',
    fontSize: 14,
    textAlign: 'center',
  },
  removeButton: {
    backgroundColor: '#FCE8E8',
    padding: 10,
    borderRadius: 8,
    marginTop: 12,
  },
  removeButtonText: {
    color: '#C62828',
    fontWeight: 'bold',
  },
  continueButton: {
    backgroundColor: '#1769AA',
    padding: 16,
    borderRadius: 9,
    alignItems: 'center',
    marginTop: 22,
  },
  disabledButton: {
    backgroundColor: '#9CB8D2',
  },
  continueButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  note: {
    color: '#777',
    fontSize: 12,
    textAlign: 'center',
    lineHeight: 19,
    marginTop: 18,
    marginBottom: 20,
  },
});
