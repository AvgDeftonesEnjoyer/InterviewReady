import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, ActivityIndicator } from 'react-native';
import { useAuthStore } from '../store/useAuthStore';
import { apiClient } from '../api/client';
import { theme } from '../theme';

const LANGUAGES = [
  { id: 'python', label: '🐍 Python' },
  { id: 'javascript', label: '🟨 JavaScript' },
  { id: 'java', label: '☕ Java' },
  { id: 'go', label: '🔵 Go' },
  { id: 'csharp', label: '🟣 C#' },
];

const SPECIALIZATIONS: Record<string, { id: string, label: string }[]> = {
  python: [
    { id: 'backend', label: 'Backend' },
    { id: 'data', label: 'Data Science' },
    { id: 'ml', label: 'ML/AI' },
  ],
  javascript: [
    { id: 'frontend', label: 'Frontend' },
    { id: 'backend', label: 'Backend' },
    { id: 'fullstack', label: 'Fullstack' },
  ],
  java: [
    { id: 'backend', label: 'Backend' },
  ],
  go: [
    { id: 'backend', label: 'Backend' },
  ],
  csharp: [
    { id: 'backend', label: 'Backend' },
  ]
};

const EXPERIENCE_LEVELS = [
  { id: 'junior', label: '🌱 Junior', desc: '0-1 year' },
  { id: 'middle', label: '🚀 Middle', desc: '1-3 years' },
  { id: 'senior', label: '⭐ Senior', desc: '3+ years' },
];

export const OnboardingScreen = ({ navigation }: any) => {
  const [step, setStep] = useState(1);
  const [language, setLanguage] = useState('');
  const [specialization, setSpecialization] = useState('');
  const [experience, setExperience] = useState('');
  const [loading, setLoading] = useState(false);
  const { setOnboardingCompleted } = useAuthStore();

  const handleNext = async () => {
    if (step === 1 && language) setStep(2);
    else if (step === 2 && specialization) setStep(3);
    else if (step === 3 && experience) {
      setLoading(true);
      try {
        await apiClient.post('/auth/onboarding/', {
          language,
          specialization,
          experience_level: experience
        });
        setOnboardingCompleted(true);
      } catch (error) {
        console.error('Failed formatting onboarding', error);
      } finally {
        setLoading(false);
      }
    }
  };

  const renderStep1 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.title}>Welcome! Choose your primary language</Text>
      <View style={styles.grid}>
        {LANGUAGES.map((lang) => (
          <TouchableOpacity
            key={lang.id}
            style={[styles.card, language === lang.id && styles.cardSelected]}
            onPress={() => setLanguage(lang.id)}
          >
            <Text style={styles.cardText}>{lang.label}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const renderStep2 = () => {
    const specs = SPECIALIZATIONS[language] || SPECIALIZATIONS['python'];
    return (
      <View style={styles.stepContainer}>
        <Text style={styles.title}>What is your specialization?</Text>
        <View style={styles.list}>
          {specs.map((spec) => (
            <TouchableOpacity
              key={spec.id}
              style={[styles.listCard, specialization === spec.id && styles.cardSelected]}
              onPress={() => setSpecialization(spec.id)}
            >
              <Text style={styles.cardText}>{spec.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    );
  };

  const renderStep3 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.title}>What is your experience level?</Text>
      <View style={styles.list}>
        {EXPERIENCE_LEVELS.map((exp) => (
          <TouchableOpacity
            key={exp.id}
            style={[styles.listCard, experience === exp.id && styles.cardSelected]}
            onPress={() => setExperience(exp.id)}
          >
            <Text style={styles.cardText}>{exp.label}</Text>
            <Text style={styles.cardDesc}>{exp.desc}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const isNextDisabled = () => {
    if (step === 1 && !language) return true;
    if (step === 2 && !specialization) return true;
    if (step === 3 && !experience) return true;
    return false;
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}
        {step === 3 && renderStep3()}
        
        <TouchableOpacity
          style={[styles.nextButton, isNextDisabled() && styles.nextButtonDisabled]}
          disabled={isNextDisabled() || loading}
          onPress={handleNext}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.nextButtonText}>
              {step === 3 ? "Let's Go!" : "Continue"}
            </Text>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: 'space-between',
  },
  stepContainer: {
    flex: 1,
    marginTop: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 32,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
    justifyContent: 'space-between',
  },
  card: {
    width: '47%',
    backgroundColor: theme.colors.background.card,
    padding: 20,
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  list: {
    gap: 16,
  },
  listCard: {
    backgroundColor: theme.colors.background.card,
    padding: 24,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  cardSelected: {
    borderColor: theme.colors.primary.DEFAULT,
    shadowColor: theme.colors.primary.DEFAULT,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 8,
  },
  cardText: {
    color: theme.colors.text.primary,
    fontSize: 18,
    fontWeight: '600',
  },
  cardDesc: {
    color: theme.colors.text.secondary,
    fontSize: 14,
    marginTop: 8,
  },
  nextButton: {
    backgroundColor: theme.colors.primary.DEFAULT,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 20,
  },
  nextButtonDisabled: {
    opacity: 0.5,
  },
  nextButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  }
});
