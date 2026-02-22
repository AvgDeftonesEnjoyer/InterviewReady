import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, ScrollView } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Animated, { FadeInDown, useAnimatedStyle, useSharedValue, withSpring, withTiming, runOnJS } from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import { theme } from '../../../theme';
import { useTopicQuestions, useSubmitLearningAnswer, useSessionSummary, Question } from '../hooks';
import { CheckCircle2, XCircle, Share2, PartyPopper } from 'lucide-react-native';
import Markdown from 'react-native-markdown-display';
import { useTranslation } from 'react-i18next';

// Custom ProgressBar for local scoped display
const ProgressBar = ({ percent }: { percent: number }) => (
    <View style={styles.progressBarBg}>
        <Animated.View style={[styles.progressBarFill, { width: `${percent}%` }]} />
    </View>
);

export const LearningSessionScreen = ({ navigation, route }: any) => {
  const { t } = useTranslation();
  const insets = useSafeAreaInsets();
  const topicId = route.params?.topic_id;
  const topicTitle = route.params?.title || t('nav.learning');

  const { data: questions, isLoading, isError, refetch } = useTopicQuestions(topicId);
  const submitAnswer = useSubmitLearningAnswer();
  
  const [phase, setPhase] = useState<'session' | 'summary'>('session');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOptionId, setSelectedOptionId] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<any>(null); // Results from individual POST
  const [sessionResults, setSessionResults] = useState<any[]>([]);
  
  // Use expo-crypto for valid UUIDs matching Django's UUIDField
  const [sessionId, setSessionId] = useState(() => {
    try {
      // In Expo, standard approach is using Crypto.randomUUID()
      const Crypto = require('expo-crypto');
      return Crypto.randomUUID();
    } catch (e) {
      // Fallback pseudo-UUID if crypto is unavailable
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
    }
  });

  const shuffledQuestions = React.useMemo(() => {
    if (!questions) return null;
    const arr = [...questions];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }, [questions]);

  // For Phase 3 stats
  const { data: summaryData, refetch: fetchSummary } = useSessionSummary(sessionId);

  useEffect(() => {
    if (phase === 'summary') {
      fetchSummary();
    }
  }, [phase]);

  if (isLoading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color={theme.colors.primary.DEFAULT} />
      </View>
    );
  }

  if (isError || !shuffledQuestions) {
    return (
      <View style={[styles.container, styles.centered]}>
        <Text style={styles.errorText}>{t('common.error')}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={() => refetch()}>
          <Text style={styles.buttonText}>{t('common.retry')}</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // --- Phase 3: Summary Screen ---
  if (phase === 'summary' || (shuffledQuestions.length === 0)) {
    const isCompleted = summaryData?.topic_progress === 100;
    const accuracy = summaryData?.accuracy || 0;
    
    return (
      <View style={styles.celebrationContainer}>
        <ScrollView contentContainerStyle={styles.celebrationScroll}>
          <Animated.View entering={FadeInDown.springify()} style={styles.celebrationIconBg}>
            <Text style={{fontSize: 48}}>{accuracy >= 80 ? '🏆' : accuracy >= 60 ? '👍' : '💪'}</Text>
          </Animated.View>
          
          <Animated.Text entering={FadeInDown.delay(100).springify()} style={styles.celebrationTitle}>
             {t('learning.session_complete')}
          </Animated.Text>

          <Animated.View entering={FadeInDown.delay(200).springify()} style={styles.statsRow}>
            <View style={styles.statCard}>
                <Text style={styles.statIcon}>✅</Text>
                <Text style={styles.statValue}>{summaryData?.correct || 0}</Text>
                <Text style={styles.statLabel}>{t('learning.correct_label', { defaultValue: 'Correct' })}</Text>
            </View>
            <View style={styles.statCard}>
                <Text style={styles.statIcon}>⚡</Text>
                <Text style={styles.statValue}>+{summaryData?.xp_earned || 0}</Text>
                <Text style={styles.statLabel}>{t('learning.xp_earned')}</Text>
            </View>
            <View style={styles.statCard}>
                <Text style={styles.statIcon}>🎯</Text>
                <Text style={styles.statValue}>{accuracy}%</Text>
                <Text style={styles.statLabel}>{t('learning.accuracy')}</Text>
            </View>
          </Animated.View>

          {isCompleted && (
            <Animated.View entering={FadeInDown.delay(300).springify()} style={styles.completedBadge}>
              <Text style={styles.completedBadgeText}>{t('learning.topic_mastered')}</Text>
            </Animated.View>
          )}

          <Animated.View entering={FadeInDown.delay(400).springify()} style={styles.bottomActions}>
              <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
                 <Text style={styles.backButtonText}>{t('learning.back_to_topics')}</Text>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.primaryBtn} onPress={() => {
                  if (isCompleted) {
                      navigation.navigate('AI');
                  } else {
                      // Reset and refetch
                      setSessionId(Math.random().toString(36).substring(2) + Date.now().toString(36));
                      setPhase('session');
                      setCurrentIndex(0);
                      refetch();
                  }
              }}>
                 <Text style={styles.primaryBtnText}>
                   {isCompleted ? t('learning.try_ai_interview') : t('learning.continue_learning')}
                 </Text>
              </TouchableOpacity>
          </Animated.View>
        </ScrollView>
      </View>
    );
  }

  // --- Phase 2: Session Screen ---
  const currentQuestion = shuffledQuestions[currentIndex];
  const total = shuffledQuestions.length;
  const isLastQuestion = currentIndex >= total - 1;

  const selectAnswer = (optionId: number) => {
    if (feedback) return;
    setSelectedOptionId(optionId);
    
    submitAnswer.mutate(
      { question_id: currentQuestion.id, answer_option_id: optionId, session_id: sessionId },
      {
        onSuccess: (data) => {
          setFeedback(data);
          setSessionResults(prev => [...prev, data]);
        },
        onError: () => {
          Alert.alert('Error', 'Failed to submit answer');
        }
      }
    );
  };

  const goToNext = () => {
    if (isLastQuestion) {
      setPhase('summary');
    } else {
      setFeedback(null);
      setSelectedOptionId(null);
      setCurrentIndex(i => i + 1);
    }
  };

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      {/* TOP BAR */}
      <View style={styles.topBar}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.exitBtn}>
          <Text style={styles.exitText}>✕</Text>
        </TouchableOpacity>
        
        <View style={styles.progressContainer}>
           <ProgressBar percent={(currentIndex / total) * 100} />
        </View>
        
        <Text style={styles.counter}>
          {currentIndex + 1}/{total}
        </Text>
      </View>

      {/* XP Badge */}
      <View style={styles.xpBadgeContainer}>
        <View style={[styles.xpBadge, feedback?.previously_answered && styles.xpBadgeWarning]}>
          <Text style={[styles.xpBadgeText, feedback?.previously_answered && styles.xpBadgeTextWarning]}>
            {feedback?.previously_answered 
              ? '⚠️ Already Answered (0 XP)' 
              : `⚡ +${currentQuestion.xp_reward} XP`}
          </Text>
        </View>
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollArea}>
        
        {/* QUESTION CARD */}
        <Animated.View entering={FadeInDown.springify()} key={`question-${currentQuestion.id}`} style={styles.questionCard}>
          <View style={styles.difficultyChip}>
            <Text style={styles.difficultyText}>{currentQuestion.difficulty}</Text>
          </View>
          <Markdown style={markdownStyles}>
            {currentQuestion.text}
          </Markdown>
        </Animated.View>

        {/* ANSWER OPTIONS */}
        <View style={styles.optionsContainer}>
          {currentQuestion.options.map((option, i) => {
            const isSelected = selectedOptionId === option.id;
            const isAnswered = !!feedback;
            const isCorrectOption = feedback?.correct_option_id === option.id;
            
            let optionStyle = styles.optionCard;
            let textStyle = styles.optionText;
            
            if (isAnswered) {
                if (isCorrectOption) {
                    optionStyle = [styles.optionCard, styles.correctCard];
                    textStyle = [styles.optionText, styles.correctText];
                } else if (isSelected && !feedback.is_correct) {
                    optionStyle = [styles.optionCard, styles.wrongCard];
                    textStyle = [styles.optionText, styles.wrongText];
                }
            } else if (isSelected) {
                optionStyle = [styles.optionCard, styles.selectedCard];
            }

            return (
              <TouchableOpacity
                key={option.id}
                onPress={() => selectAnswer(option.id)}
                disabled={isAnswered || submitAnswer.isPending}
                style={optionStyle}
                activeOpacity={0.8}
              >
                <View style={[styles.optionLetter, (isSelected && !isAnswered) && styles.selectedLetter]}>
                  <Text style={[styles.letterText, (isSelected && !isAnswered) && {color: theme.colors.primary.DEFAULT}]}>
                      {['A','B','C','D', 'E', 'F'][i]}
                  </Text>
                </View>
                <Text style={textStyle}>{option.text}</Text>
                
                {isAnswered && isCorrectOption && (
                   <CheckCircle2 color={theme.colors.status.success} size={20} style={styles.iconRight} />
                )}
                {isAnswered && isSelected && !feedback.is_correct && (
                   <XCircle color={theme.colors.status.error} size={20} style={styles.iconRight} />
                )}
              </TouchableOpacity>
            )
          })}
        </View>

        {submitAnswer.isPending && (
             <ActivityIndicator style={{marginTop: 20}} color={theme.colors.primary.light} />
        )}

      </ScrollView>

      {/* FEEDBACK PANEL */}
      {feedback && (
        <Animated.View entering={FadeInDown.duration(300)} style={styles.feedbackPanel}>
          {feedback.is_correct ? (
            <View style={styles.correctPanel}>
              <Text style={styles.feedbackTitle}>{t('learning.correct', { xp: feedback.xp_earned })}</Text>
            </View>
          ) : (
            <View style={styles.wrongPanel}>
              <Text style={styles.feedbackTitleError}>{t('learning.wrong')}</Text>
            </View>
          )}
          
          {feedback.explanation ? (
            <Markdown style={markdownStyles}>
              {feedback.explanation}
            </Markdown>
          ) : null}
          
          <TouchableOpacity style={styles.nextButton} onPress={goToNext}>
            <Text style={styles.nextButtonText}>
              {isLastQuestion ? t('learning.see_results') : t('learning.next_question')}
            </Text>
          </TouchableOpacity>
        </Animated.View>
      )}
    </View>
  );
};

const markdownStyles = {
  body: {
    color: theme.colors.text.primary,
    fontSize: 20,
    lineHeight: 28,
  },
  code_block: {
    backgroundColor: '#0d0f1a',
    borderRadius: 8,
    padding: 12,
    color: '#818CF8',
    fontFamily: 'monospace',
    fontSize: 14,
    borderWidth: 1,
    borderColor: 'rgba(108,99,255,0.2)',
  },
  code_inline: {
    backgroundColor: '#0d0f1a',
    color: '#818CF8',
    fontFamily: 'monospace',
    borderRadius: 4,
    paddingHorizontal: 4,
  },
  fence: {
    backgroundColor: '#0d0f1a',
    borderRadius: 8,
    padding: 12,
    borderWidth: 1,
    borderColor: 'rgba(108,99,255,0.2)',
  },
};

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: theme.colors.background.primary, 
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    color: theme.colors.status.error,
    marginBottom: 16,
    fontSize: 16,
  },
  retryButton: {
    padding: 12,
    backgroundColor: theme.colors.background.card,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  // TopBar 
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.subtle,
  },
  exitBtn: {
    padding: 8,
  },
  exitText: {
    color: theme.colors.text.secondary,
    fontSize: 20,
    fontWeight: 'bold',
  },
  progressContainer: {
    flex: 1,
    marginHorizontal: 16,
  },
  progressBarBg: {
    height: 8,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: theme.colors.primary.light,
    borderRadius: 4,
  },
  counter: {
    color: theme.colors.text.secondary,
    fontWeight: 'bold',
  },
  xpBadgeContainer: {
    alignItems: 'center',
    marginTop: 16,
  },
  xpBadge: {
    backgroundColor: 'rgba(245, 158, 11, 0.15)',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(245, 158, 11, 0.3)',
  },
  xpBadgeText: {
    color: '#fbbf24',
    fontWeight: 'bold',
  },
  xpBadgeWarning: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderColor: 'rgba(239, 68, 68, 0.3)',
  },
  xpBadgeTextWarning: {
    color: '#ef4444',
  },
  scrollArea: {
    padding: 20,
    paddingBottom: 120,
  },
  questionCard: {
    backgroundColor: theme.colors.background.card,
    padding: 24,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
    marginBottom: 24,
  },
  difficultyChip: {
    backgroundColor: 'rgba(108, 99, 255, 0.15)',
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 8,
    marginBottom: 16,
  },
  difficultyText: {
    color: theme.colors.primary.light,
    fontSize: 12,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  questionText: {
    color: theme.colors.text.primary,
    fontSize: 20,
    fontWeight: '600',
    lineHeight: 28,
  },
  optionsContainer: {
    gap: 12,
  },
  optionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1e2035',
    padding: 16,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: 'rgba(255,255,255,0.08)',
  },
  selectedCard: {
    backgroundColor: 'rgba(108,99,255,0.2)',
    borderColor: theme.colors.primary.DEFAULT,
  },
  correctCard: {
    backgroundColor: 'rgba(34,197,94,0.15)',
    borderColor: '#22c55e',
  },
  wrongCard: {
    backgroundColor: 'rgba(239,68,68,0.15)',
    borderColor: '#ef4444',
  },
  optionLetter: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  selectedLetter: {
    backgroundColor: '#fff',
  },
  letterText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  optionText: {
    flex: 1,
    color: theme.colors.text.primary,
    fontSize: 16,
  },
  correctText: {
    color: '#22c55e',
    fontWeight: 'bold',
  },
  wrongText: {
    color: '#ef4444',
  },
  iconRight: {
    marginLeft: 12,
  },
  // Feedback Panel
  feedbackPanel: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: theme.colors.background.elevated,
    padding: 24,
    paddingBottom: 40,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.subtle,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 20,
  },
  correctPanel: {
    marginBottom: 12,
  },
  wrongPanel: {
    marginBottom: 12,
  },
  feedbackTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#22c55e',
  },
  feedbackTitleError: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ef4444',
  },
  explanationText: {
    color: theme.colors.text.secondary,
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 20,
  },
  nextButton: {
    backgroundColor: theme.colors.primary.DEFAULT,
    padding: 18,
    borderRadius: 16,
    alignItems: 'center',
  },
  nextButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  // Celebration Screen (Phase 3)
  celebrationContainer: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  celebrationScroll: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  celebrationIconBg: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: 'rgba(255,255,255,0.05)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  celebrationTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 32,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 32,
    width: '100%',
  },
  statCard: {
    flex: 1,
    backgroundColor: theme.colors.background.card,
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
  },
  statIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: theme.colors.text.secondary,
  },
  completedBadge: {
    backgroundColor: 'rgba(34,197,94,0.15)',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(34,197,94,0.4)',
    marginBottom: 40,
  },
  completedBadgeText: {
    color: '#22c55e',
    fontWeight: 'bold',
    fontSize: 16,
  },
  bottomActions: {
    width: '100%',
    gap: 16,
  },
  backButton: {
    padding: 16,
    alignItems: 'center',
  },
  backButtonText: {
    color: theme.colors.text.secondary,
    fontSize: 16,
  },
  primaryBtn: {
    backgroundColor: theme.colors.primary.DEFAULT,
    padding: 18,
    borderRadius: 16,
    alignItems: 'center',
  },
  primaryBtnText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  }
});
