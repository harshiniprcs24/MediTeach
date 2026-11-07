
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';

const quizData = {
  English: {
    title: 'Test Your Knowledge',
    description: 'Answer these sample medicine safety questions.',
    next: 'Next Question',
    finish: 'Finish Test',
    tryAgain: 'Try Again',
    question: 'Question',
    score: 'Your Score',
    result: 'Test Completed!',
    questions: [
      {
        question: 'Who should you consult if you are unsure about your prescribed medicine?',
        options: [
          'A qualified healthcare professional',
          'A friend',
          'A social media user',
          'No one',
        ],
        answer: 0,
      },
      {
        question: 'What should you do if the dosage on your prescription is unclear?',
        options: [
          'Guess the dosage',
          'Ask a qualified healthcare professional',
          'Double the dosage',
          'Stop all medicines permanently',
        ],
        answer: 1,
      },
      {
        question: 'Why is it important to follow the prescribed medicine schedule?',
        options: [
          'To avoid checking the prescription',
          'To take medicines randomly',
          'To follow the treatment instructions correctly',
          'To change the dosage yourself',
        ],
        answer: 2,
      },
    ],
  },

  Tamil: {
    title: 'உங்கள் அறிவைச் சோதிக்கவும்',
    description: 'இந்த மாதிரி மருந்து பாதுகாப்புக் கேள்விகளுக்கு பதிலளிக்கவும்.',
    next: 'அடுத்த கேள்வி',
    finish: 'சோதனையை முடிக்கவும்',
    tryAgain: 'மீண்டும் முயற்சிக்கவும்',
    question: 'கேள்வி',
    score: 'உங்கள் மதிப்பெண்',
    result: 'சோதனை முடிந்தது!',
    questions: [
      {
        question: 'பரிந்துரைக்கப்பட்ட மருந்தைப் பற்றி சந்தேகம் இருந்தால் யாரிடம் ஆலோசனை பெற வேண்டும்?',
        options: [
          'தகுதியான சுகாதார நிபுணர்',
          'நண்பர்',
          'சமூக ஊடகப் பயனர்',
          'யாரிடமும் வேண்டாம்',
        ],
        answer: 0,
      },
      {
        question: 'மருந்துச் சீட்டில் அளவு தெளிவாக இல்லாவிட்டால் என்ன செய்ய வேண்டும்?',
        options: [
          'அளவை ஊகிக்க வேண்டும்',
          'தகுதியான சுகாதார நிபுணரிடம் கேட்க வேண்டும்',
          'இரட்டிப்பு அளவு எடுக்க வேண்டும்',
          'அனைத்து மருந்துகளையும் நிரந்தரமாக நிறுத்த வேண்டும்',
        ],
        answer: 1,
      },
      {
        question: 'பரிந்துரைக்கப்பட்ட மருந்து அட்டவணையைப் பின்பற்றுவது ஏன் முக்கியம்?',
        options: [
          'மருந்துச் சீட்டைப் பார்க்காமல் இருக்க',
          'விருப்பப்படி மருந்து எடுக்க',
          'சிகிச்சை வழிமுறைகளைச் சரியாகப் பின்பற்ற',
          'அளவை நீங்களே மாற்ற',
        ],
        answer: 2,
      },
    ],
  },

  Hindi: {
    title: 'अपनी जानकारी जाँचें',
    description: 'दवा सुरक्षा से जुड़े इन नमूना प्रश्नों के उत्तर दें।',
    next: 'अगला प्रश्न',
    finish: 'टेस्ट समाप्त करें',
    tryAgain: 'फिर से प्रयास करें',
    question: 'प्रश्न',
    score: 'आपका स्कोर',
    result: 'टेस्ट पूरा हुआ!',
    questions: [
      {
        question: 'निर्धारित दवा के बारे में संदेह होने पर किससे सलाह लेनी चाहिए?',
        options: [
          'योग्य स्वास्थ्य विशेषज्ञ',
          'दोस्त',
          'सोशल मीडिया उपयोगकर्ता',
          'किसी से नहीं',
        ],
        answer: 0,
      },
      {
        question: 'यदि प्रिस्क्रिप्शन में दवा की मात्रा स्पष्ट नहीं है, तो क्या करना चाहिए?',
        options: [
          'मात्रा का अनुमान लगाना',
          'योग्य स्वास्थ्य विशेषज्ञ से पूछना',
          'दोगुनी मात्रा लेना',
          'सभी दवाएँ हमेशा के लिए बंद करना',
        ],
        answer: 1,
      },
      {
        question: 'निर्धारित दवा समय-सारणी का पालन करना क्यों महत्वपूर्ण है?',
        options: [
          'प्रिस्क्रिप्शन देखने से बचने के लिए',
          'दवाएँ कभी भी लेने के लिए',
          'उपचार के निर्देशों का सही पालन करने के लिए',
          'खुद से दवा की मात्रा बदलने के लिए',
        ],
        answer: 2,
      },
    ],
  },
};

export default function KnowledgeTestScreen({ onBack }) {
  const [language, setLanguage] = useState('English');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [finished, setFinished] = useState(false);

  const quiz = quizData[language];
  const current = quiz.questions[currentQuestion];

  const selectAnswer = (index) => {
    setSelectedAnswers((previous) => ({
      ...previous,
      [currentQuestion]: index,
    }));
  };

  const finishTest = () => {
    setFinished(true);
  };

  const resetTest = () => {
    setCurrentQuestion(0);
    setSelectedAnswers({});
    setFinished(false);
  };

  const score = quiz.questions.reduce((total, question, index) => {
    return total + (selectedAnswers[index] === question.answer ? 1 : 0);
  }, 0);

  const changeLanguage = (newLanguage) => {
    setLanguage(newLanguage);
    setCurrentQuestion(0);
    setSelectedAnswers({});
    setFinished(false);
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <TouchableOpacity onPress={onBack}>
        <Text style={styles.backText}>‹ Back to Home</Text>
      </TouchableOpacity>

      <Text style={styles.title}>{quiz.title}</Text>
      <Text style={styles.description}>{quiz.description}</Text>

      <View style={styles.languageContainer}>
        <Text style={styles.label}>Choose Language</Text>

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

      {!finished ? (
        <View style={styles.questionCard}>
          <Text style={styles.questionNumber}>
            {quiz.question} {currentQuestion + 1} / {quiz.questions.length}
          </Text>

          <Text style={styles.questionText}>
            {current.question}
          </Text>

          {current.options.map((option, index) => (
            <TouchableOpacity
              key={index}
              style={[
                styles.option,
                selectedAnswers[currentQuestion] === index &&
                  styles.selectedOption,
              ]}
              onPress={() => selectAnswer(index)}
            >
              <Text
                style={[
                  styles.optionText,
                  selectedAnswers[currentQuestion] === index &&
                    styles.selectedOptionText,
                ]}
              >
                {option}
              </Text>
            </TouchableOpacity>
          ))}

          <TouchableOpacity
            style={[
              styles.actionButton,
              selectedAnswers[currentQuestion] === undefined &&
                styles.disabledButton,
            ]}
            disabled={selectedAnswers[currentQuestion] === undefined}
            onPress={() => {
              if (currentQuestion < quiz.questions.length - 1) {
                setCurrentQuestion(currentQuestion + 1);
              } else {
                finishTest();
              }
            }}
          >
            <Text style={styles.actionButtonText}>
              {currentQuestion === quiz.questions.length - 1
                ? quiz.finish
                : quiz.next}
            </Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.resultCard}>
          <Text style={styles.resultTitle}>{quiz.result}</Text>

          <Text style={styles.scoreText}>
            {quiz.score}: {score} / {quiz.questions.length}
          </Text>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={resetTest}
          >
            <Text style={styles.actionButtonText}>
              {quiz.tryAgain}
            </Text>
          </TouchableOpacity>
        </View>
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
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 10,
    marginBottom: 20,
  },
  languageContainer: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 12,
    marginBottom: 20,
  },
  label: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  languageRow: {
    flexDirection: 'row',
    gap: 8,
  },
  languageButton: {
    flex: 1,
    padding: 12,
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
  questionCard: {
    backgroundColor: '#FFFFFF',
    padding: 18,
    borderRadius: 12,
    elevation: 2,
  },
  questionNumber: {
    color: '#1769AA',
    fontWeight: 'bold',
    marginBottom: 15,
  },
  questionText: {
    fontSize: 17,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
    lineHeight: 25,
  },
  option: {
    padding: 14,
    borderWidth: 1,
    borderColor: '#DCE5EF',
    borderRadius: 9,
    marginBottom: 12,
  },
  selectedOption: {
    backgroundColor: '#E4F1FF',
    borderColor: '#1769AA',
  },
  optionText: {
    fontSize: 14,
    color: '#333',
  },
  selectedOptionText: {
    color: '#1769AA',
    fontWeight: 'bold',
  },
  actionButton: {
    backgroundColor: '#1769AA',
    padding: 15,
    borderRadius: 9,
    alignItems: 'center',
    marginTop: 15,
  },
  disabledButton: {
    backgroundColor: '#9CB8D2',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  resultCard: {
    backgroundColor: '#FFFFFF',
    padding: 25,
    borderRadius: 12,
    alignItems: 'center',
    elevation: 2,
  },
  resultTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1769AA',
  },
  scoreText: {
    fontSize: 20,
    color: '#333',
    marginTop: 20,
  },
});
