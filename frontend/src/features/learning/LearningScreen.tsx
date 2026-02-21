import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, ScrollView } from 'react-native';
import { useDailyQuestions, useSubmitAnswer } from './hooks';
import { theme } from '../../theme';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { CheckCircle2, XCircle, Share2, PartyPopper } from 'lucide-react-native';
import { LinearGradient } from 'expo-linear-gradient';

export const LearningScreen = () => {
  const { data: questions, isLoading, isError, refetch } = useDailyQuestions();
  const submitAnswer = useSubmitAnswer();
  
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<{ is_correct: boolean; explanation: string; xp_earned: number } | null>(null);
  const [score, setScore] = useState(0);

  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary.DEFAULT} />
      </View>
    );
  }

  if (isError || !questions) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Failed to load questions</Text>
        <TouchableOpacity onPress={() => refetch()} style={styles.retryButton}>
          <Text style={styles.buttonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Celebration State UI
  if (currentIndex >= questions.length && questions.length > 0) {
    return (
      <View style={styles.celebrationContainer}>
        <ScrollView contentContainerStyle={styles.celebrationScroll}>
          <View style={styles.celebrationIconBg}>
            <PartyPopper size={48} color={theme.colors.status.warning} />
          </View>
          <Text style={styles.celebrationTitle}>Day Complete!</Text>
          <Text style={styles.celebrationSubtitle}>You crushed today's challenge.</Text>

          <LinearGradient
            colors={['rgba(34, 197, 94, 0.15)', 'rgba(34, 197, 94, 0.05)']}
            style={styles.scoreCard}
          >
            <Text style={styles.scoreLabel}>Final Score</Text>
            <Text style={styles.scoreValue}>{score} / {questions.length}</Text>
          </LinearGradient>

          <View style={styles.timerCard}>
            <Text style={styles.timerLabel}>Next lock opens in</Text>
            <Text style={styles.timerValue}>14:22:05</Text>
          </View>
          
          <TouchableOpacity style={styles.shareButton}>
            <Share2 color={theme.colors.primary.DEFAULT} size={20} style={{ marginRight: 8 }} />
            <Text style={styles.shareText}>Share Progress</Text>
          </TouchableOpacity>
        </ScrollView>
      </View>
    );
  } else if (currentIndex >= questions.length) {
      return (
        <View style={styles.centerContainer}>
           <Text style={styles.celebrationSubtitle}>No questions available today.</Text>
        </View>
      );
  }

  const currentQuestion = questions[currentIndex];
  const progress = (currentIndex / questions.length) * 100;

  const handleSubmit = () => {
    if (!selectedOption) return;
    
    submitAnswer.mutate(
      { questionId: currentQuestion.id, optionId: selectedOption },
      {
        onSuccess: (data) => {
          setFeedback(data);
          if (data.is_correct) setScore(s => s + 1);
        },
        onError: () => {
          Alert.alert('Error', 'Failed to submit answer');
        }
      }
    );
  };

  const handleNext = () => {
    setFeedback(null);
    setSelectedOption(null);
    setCurrentIndex((prev) => prev + 1);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <ProgressBar progress={progress} showPercentage={false} height={12} />
        <Text style={styles.progressText}>{currentIndex + 1} / {questions.length}</Text>
      </View>
      
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollArea}>
        <View style={styles.questionCard}>
          <View style={styles.badgeContainer}>
            <Text style={styles.badge}>{currentQuestion.difficulty}</Text>
          </View>
          <Text style={styles.questionText}>{currentQuestion.text}</Text>
        </View>

        <View style={styles.optionsContainer}>
          {currentQuestion.options.map((opt) => {
            const isSelected = selectedOption === opt.id;
            
            // Determine active option style based on feedback state
            let optionStyle = styles.optionButton;
            let textStyle = styles.optionText;
            
            if (isSelected) {
              if (!feedback) {
                optionStyle = [styles.optionButton, styles.optionSelected];
                textStyle = [styles.optionText, styles.optionTextSelected];
              } else if (feedback.is_correct) {
                optionStyle = [styles.optionButton, styles.optionCorrect];
                textStyle = [styles.optionText, styles.optionTextCorrect];
              } else {
                optionStyle = [styles.optionButton, styles.optionWrong];
                textStyle = [styles.optionText, styles.optionTextWrong];
              }
            } else if (feedback && opt.is_correct) {
                // Highlight the correct answer if they got it wrong
                optionStyle = [styles.optionButton, styles.optionCorrectMissed];
                textStyle = [styles.optionText, styles.optionTextCorrect];
            }

            return (
              <TouchableOpacity 
                key={opt.id}
                style={optionStyle}
                onPress={() => !feedback && setSelectedOption(opt.id)}
                disabled={!!feedback}
                activeOpacity={0.8}
              >
                <Text style={textStyle}>{opt.text}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {feedback && (
          <View style={[styles.feedbackPanel, feedback.is_correct ? styles.feedbackCorrect : styles.feedbackWrong]}>
            <View style={styles.feedbackHeaderRow}>
               {feedback.is_correct ? <CheckCircle2 color={theme.colors.status.success} size={24} /> : <XCircle color={theme.colors.status.error} size={24} />}
               <Text style={[styles.feedbackTitle, { color: feedback.is_correct ? theme.colors.status.success : theme.colors.status.error }]}>
                 {feedback.is_correct ? 'Excellent!' : 'Not quite'}
               </Text>
            </View>
            <Text style={styles.feedbackExplanation}>{feedback.explanation}</Text>
            {feedback.xp_earned > 0 && (
              <View style={styles.xpPill}>
                 <Text style={styles.xpText}>+{feedback.xp_earned} XP</Text>
              </View>
            )}
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        {!feedback ? (
          <TouchableOpacity 
            style={[styles.actionButton, !selectedOption && styles.buttonDisabled]} 
            onPress={handleSubmit}
            disabled={!selectedOption || submitAnswer.isPending}
          >
            {submitAnswer.isPending ? <ActivityIndicator color="#FFF" /> : <Text style={styles.actionButtonText}>Check Answer</Text>}
          </TouchableOpacity>
        ) : (
          <TouchableOpacity style={styles.actionButton} onPress={handleNext}>
            <Text style={styles.actionButtonText}>Continue</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: theme.colors.background.primary, 
    paddingTop: 60,
  },
  centerContainer: { 
    flex: 1, 
    backgroundColor: theme.colors.background.primary, 
    justifyContent: 'center', 
    alignItems: 'center',
    padding: 20,
  },
  header: {
    paddingHorizontal: 20,
    marginBottom: 20,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  progressText: {
    color: theme.colors.text.secondary,
    fontWeight: theme.typography.weight.bold,
  },
  scrollArea: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  questionCard: { 
    backgroundColor: theme.colors.background.card, 
    padding: 24, 
    borderRadius: 24, 
    marginBottom: 24,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  badgeContainer: {
    backgroundColor: `${theme.colors.primary.DEFAULT}20`,
    alignSelf: 'flex-start',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginBottom: 16,
  },
  badge: { 
    color: theme.colors.primary.light, 
    fontSize: 12, 
    fontWeight: theme.typography.weight.bold, 
    textTransform: 'uppercase' 
  },
  questionText: { 
    color: theme.colors.text.primary, 
    fontSize: theme.typography.size.h3, 
    fontWeight: theme.typography.weight.semibold, 
    lineHeight: 28 
  },
  optionsContainer: { gap: 12 },
  optionButton: { 
    backgroundColor: theme.colors.background.card, 
    padding: 20, 
    borderRadius: 16, 
    borderWidth: 2, 
    borderColor: theme.colors.border.subtle 
  },
  optionSelected: { 
    borderColor: theme.colors.primary.DEFAULT, 
    backgroundColor: `${theme.colors.primary.DEFAULT}10` 
  },
  optionCorrect: {
    borderColor: theme.colors.status.success, 
    backgroundColor: `${theme.colors.status.success}10` 
  },
  optionCorrectMissed: {
    borderColor: theme.colors.status.success, 
    borderStyle: 'dashed',
  },
  optionWrong: {
    borderColor: theme.colors.status.error, 
    backgroundColor: `${theme.colors.status.error}10` 
  },
  optionText: { 
    color: theme.colors.text.primary, 
    fontSize: 16,
    fontWeight: theme.typography.weight.medium,
  },
  optionTextSelected: { 
    color: theme.colors.primary.light, 
    fontWeight: theme.typography.weight.bold 
  },
  optionTextCorrect: {
    color: theme.colors.status.success,
  },
  optionTextWrong: {
    color: theme.colors.status.error,
  },
  feedbackPanel: { 
    marginTop: 24, 
    padding: 20, 
    borderRadius: 16,
    borderWidth: 1,
  },
  feedbackHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
  },
  feedbackCorrect: { 
    backgroundColor: `${theme.colors.status.success}10`, 
    borderColor: `${theme.colors.status.success}40` 
  },
  feedbackWrong: { 
    backgroundColor: `${theme.colors.status.error}10`, 
    borderColor: `${theme.colors.status.error}40` 
  },
  feedbackTitle: { 
    fontSize: theme.typography.size.h3, 
    fontWeight: theme.typography.weight.bold, 
  },
  feedbackExplanation: { 
    color: theme.colors.text.secondary, 
    fontSize: 15, 
    lineHeight: 22 
  },
  xpPill: {
    backgroundColor: `${theme.colors.status.warning}20`,
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    marginTop: 16,
  },
  xpText: { 
    color: theme.colors.status.warning, 
    fontWeight: theme.typography.weight.bold, 
    fontSize: 14 
  },
  footer: { 
    padding: 20,
    paddingBottom: 110, // Account for CustomTabBar
    backgroundColor: theme.colors.background.primary,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.subtle,
  },
  actionButton: { 
    backgroundColor: theme.colors.primary.DEFAULT, 
    padding: 18, 
    borderRadius: 16, 
    alignItems: 'center',
    shadowColor: theme.colors.primary.DEFAULT,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  buttonDisabled: { 
    opacity: 0.5,
    shadowOpacity: 0,
  },
  actionButtonText: { 
    color: theme.colors.text.primary, 
    fontWeight: theme.typography.weight.bold, 
    fontSize: 18 
  },
  errorText: { 
    color: theme.colors.status.error, 
    marginBottom: 16, 
    fontSize: 16 
  },
  retryButton: { 
    backgroundColor: theme.colors.background.card, 
    paddingHorizontal: 20,
    paddingVertical: 12, 
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  buttonText: { 
    color: theme.colors.text.primary, 
    fontWeight: theme.typography.weight.semibold 
  },
  // Celebration Styles
  celebrationContainer: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  celebrationScroll: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
    paddingBottom: 120, // TabBar
  },
  celebrationIconBg: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: `${theme.colors.status.warning}15`,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
    borderWidth: 1,
    borderColor: `${theme.colors.status.warning}30`,
  },
  celebrationTitle: { 
    fontSize: 32, 
    fontWeight: theme.typography.weight.bold, 
    color: theme.colors.text.primary, 
    marginBottom: 8,
    textAlign: 'center',
  },
  celebrationSubtitle: { 
    color: theme.colors.text.secondary, 
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 40,
  },
  scoreCard: {
    width: '100%',
    padding: 24,
    borderRadius: 24,
    alignItems: 'center',
    marginBottom: 24,
    borderWidth: 1,
    borderColor: `${theme.colors.status.success}30`,
  },
  scoreLabel: {
    color: theme.colors.status.success,
    fontSize: 14,
    fontWeight: theme.typography.weight.bold,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 8,
  },
  scoreValue: {
    color: theme.colors.text.primary,
    fontSize: 40,
    fontWeight: theme.typography.weight.bold,
  },
  timerCard: {
    width: '100%',
    backgroundColor: theme.colors.background.card,
    padding: 20,
    borderRadius: 20,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
    marginBottom: 32,
  },
  timerLabel: {
    color: theme.colors.text.secondary,
    fontSize: 14,
    marginBottom: 4,
  },
  timerValue: {
    color: theme.colors.primary.light,
    fontSize: 24,
    fontWeight: theme.typography.weight.bold,
  },
  shareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: `${theme.colors.primary.DEFAULT}15`,
    paddingHorizontal: 24,
    paddingVertical: 14,
    borderRadius: 16,
  },
  shareText: {
    color: theme.colors.primary.light,
    fontSize: 16,
    fontWeight: theme.typography.weight.semibold,
  }
});
