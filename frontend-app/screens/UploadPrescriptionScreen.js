import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Image,
  ActivityIndicator,
} from 'react-native';

import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import api from '../services/api';

export default function UploadPrescriptionScreen({ onBack, onContinue }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading]       = useState(false);

  // ── File selection helpers ──────────────────────────────────────────────────

  const selectImage = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission Required', 'Please allow gallery access to select a prescription.');
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
        uri:  file.uri,
        name: file.fileName || 'prescription.jpg',
        mimeType: file.mimeType || 'image/jpeg',
        type: 'image',
      });
    }
  };

  const takePhoto = async () => {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission Required', 'Please allow camera access to take a prescription photo.');
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
        uri:  file.uri,
        name: file.fileName || 'prescription.jpg',
        mimeType: file.mimeType || 'image/jpeg',
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
        uri:  file.uri,
        name: file.name,
        mimeType: 'application/pdf',
        type: 'pdf',
      });
    }
  };

  const removeFile = () => setSelectedFile(null);

  // ── Upload and navigate ─────────────────────────────────────────────────────

  const uploadAndContinue = async () => {
    if (!selectedFile) {
      Alert.alert('No Prescription Selected', 'Please select or capture a prescription first.');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();

      // FormData file construction differs between environments:
      //
      // • Expo Go (native iOS / Android): React Native's custom fetch understands
      //   a plain object { uri, name, type } appended to FormData. This is the
      //   standard RN pattern and works without fetching the blob first.
      //
      // • Expo web (browser): The browser's native fetch requires a real Blob or
      //   File object. Appending { uri, name, type } sends "[object Object]" as
      //   text, which FastAPI rejects with 422. We must fetch the blob from the
      //   local URI first.
      //
      // We detect the environment by checking for the web platform.

      const isWeb = typeof document !== 'undefined';

      if (isWeb) {
        // Browser: fetch the local file URI as a Blob, then wrap it in a File
        // so that the filename and MIME type are preserved in the multipart body.
        let blob;
        try {
          const localResponse = await fetch(selectedFile.uri);
          blob = await localResponse.blob();
        } catch (blobErr) {
          Alert.alert('Upload Failed', 'Could not read the selected file. Please try again.');
          return;
        }
        // Use the File constructor (available in all modern browsers) so that
        // the filename appears in the Content-Disposition header.
        const file = new File(
          [blob],
          selectedFile.name,
          { type: selectedFile.mimeType || blob.type || 'image/jpeg' }
        );
        formData.append('file', file);
      } else {
        // Native (Expo Go): React Native's fetch handles the plain-object form.
        formData.append('file', {
          uri:  selectedFile.uri,
          name: selectedFile.name,
          type: selectedFile.mimeType || 'image/jpeg',
        });
      }

      const result = await api.uploadFile('/prescriptions/upload?language=en', formData);

      if (result.error) {
        if (result.sessionExpired) {
          Alert.alert('Session Expired', 'Please log in again.');
          return;
        }
        if (result.status === 413) {
          Alert.alert('File Too Large', 'The prescription file exceeds the maximum allowed size.');
          return;
        }
        if (result.status === 400) {
          Alert.alert(
            'Unsupported File Type',
            'Please upload a JPEG, PNG, or WEBP image. PDF uploads require a compatible image converter.'
          );
          return;
        }
        Alert.alert('Upload Failed', result.message || 'Could not upload the prescription. Please try again.');
        return;
      }

      // result is a PrescriptionOut object — pass it to the explanation screen
      onContinue(result);
    } finally {
      setUploading(false);
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TouchableOpacity onPress={onBack} disabled={uploading}>
        <Text style={styles.backText}>‹ Back to Home</Text>
      </TouchableOpacity>

      <Text style={styles.title}>Upload Prescription</Text>
      <Text style={styles.description}>
        Upload your prescription image so we can extract medicine details.
      </Text>

      <View style={styles.uploadCard}>
        <Text style={styles.uploadIcon}>📄</Text>
        <Text style={styles.uploadHeading}>Select Your Prescription</Text>
        <Text style={styles.uploadDescription}>
          Choose an image from your gallery, take a photo, or upload a PDF.
        </Text>

        <TouchableOpacity style={styles.optionButton} onPress={selectImage} disabled={uploading}>
          <Text style={styles.optionButtonText}>🖼️ Choose from Gallery</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.optionButton} onPress={takePhoto} disabled={uploading}>
          <Text style={styles.optionButtonText}>📷 Take a Photo</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.optionButton} onPress={selectPDF} disabled={uploading}>
          <Text style={styles.optionButtonText}>📑 Upload PDF</Text>
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

          {!uploading && (
            <TouchableOpacity style={styles.removeButton} onPress={removeFile}>
              <Text style={styles.removeButtonText}>Remove File</Text>
            </TouchableOpacity>
          )}
        </View>
      )}

      <TouchableOpacity
        style={[
          styles.continueButton,
          (!selectedFile || uploading) && styles.disabledButton,
        ]}
        onPress={uploadAndContinue}
        disabled={!selectedFile || uploading}
      >
        {uploading ? (
          <View style={styles.loadingRow}>
            <ActivityIndicator color="#FFFFFF" style={{ marginRight: 10 }} />
            <Text style={styles.continueButtonText}>Uploading & Processing…</Text>
          </View>
        ) : (
          <Text style={styles.continueButtonText}>Upload & Continue</Text>
        )}
      </TouchableOpacity>

      <Text style={styles.note}>
        Text is extracted using OCR and analysed by AI. All results must be
        verified by a qualified healthcare professional before acting on them.
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
    minHeight: 52,
    justifyContent: 'center',
  },
  disabledButton: {
    backgroundColor: '#9CB8D2',
  },
  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
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
