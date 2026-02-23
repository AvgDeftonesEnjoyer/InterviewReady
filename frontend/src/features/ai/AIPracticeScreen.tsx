import React, { useState, useEffect, useRef } from 'react';
import { 
  View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, 
  Alert, Animated, Platform, ScrollView, Easing, KeyboardAvoidingView 
} from 'react-native';
import { useEvaluateAI } from './hooks';
import { LinearGradient } from 'expo-linear-gradient';
import { Bot, Play, ArrowRight, RefreshCw, XCircle } from 'lucide-react-native';
import Reanimated, { FadeInDown } from 'react-native-reanimated';
import { apiClient } from '../../api/client';
import { useNavigation } from '@react-navigation/native';

type Phase = 'START' | 'ACTIVE' | 'EVALUATION';

export const AIPracticeScreen = () => {
  const navigation = useNavigation<any>();
  const [phase, setPhase] = useState<Phase>('START');
  
  // New Setup States
  const [selectedMode, setSelectedMode] = useState<'hr' | 'tech' | 'combined' | null>(null);
  const [selectedLang, setSelectedLang] = useState<string | null>(null);
  const [questionCount, setQuestionCount] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [quota, setQuota] = useState<{ remaining: number, limit: number, can_start: boolean } | null>(null);
  const [showPaywall, setShowPaywall] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);

  const [question, setQuestion] = useState('Tell me about your experience with building scalable React Native applications. What challenges did you face?');
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState<{ evaluation: string; followup: string; score?: number } | null>(null);

  const [timer, setTimer] = useState(0);
  const [isTyping, setIsTyping] = useState(true);
  const [displayedQuestion, setDisplayedQuestion] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const evaluateAI = useEvaluateAI();

  // Animations
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const btnScaleAnim = useRef(new Animated.Value(1)).current;
  const modalSlideAnim = useRef(new Animated.Value(1000)).current;

  // Render Bot Pulse Loop
  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.05, duration: 1500, easing: Easing.inOut(Easing.ease), useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 1500, easing: Easing.inOut(Easing.ease), useNativeDriver: true })
      ])
    ).start();
  }, [pulseAnim]);

  // Handle Active Interview Initializations (Timer & Typewriter)
  useEffect(() => {
    let timerInt: ReturnType<typeof setInterval>;
    let typeInterval: ReturnType<typeof setInterval>;
    let waitTimer: ReturnType<typeof setTimeout>;

    if (phase === 'ACTIVE') {
      const start = Date.now();
      timerInt = setInterval(() => {
        setTimer(Math.floor((Date.now() - start) / 1000));
      }, 1000);

      setIsTyping(true);
      setDisplayedQuestion('');
      waitTimer = setTimeout(() => {
        setIsTyping(false);
        let i = 0;
        typeInterval = setInterval(() => {
          setDisplayedQuestion(question.substring(0, i + 1));
          i++;
          if (i >= question.length) clearInterval(typeInterval);
        }, 30);
      }, 2000); // 2 second mock thinking/typing
    }

    return () => {
      clearInterval(timerInt);
      clearInterval(typeInterval);
      clearTimeout(waitTimer);
    };
  }, [phase, question]);

  // Handle Modal Presentation
  useEffect(() => {
    if (phase === 'EVALUATION') {
      Animated.spring(modalSlideAnim, { toValue: 0, tension: 50, friction: 8, useNativeDriver: true }).start();
    } else {
      modalSlideAnim.setValue(1000);
    }
  }, [phase, modalSlideAnim]);

  // Fetch Quota
  useEffect(() => {
    const fetchQuota = async () => {
      try {
        const { data } = await apiClient.get('/interviews/quota/');
        setQuota(data);
        if (!data.can_start) {
          setShowPaywall(true);
        }
      } catch (err) {
        console.error('Failed to get quota', err);
      }
    };
    fetchQuota();
  }, [phase]);

  const canStart =
    selectedMode !== null &&
    (selectedMode === 'hr' || selectedLang !== null) &&
    questionCount !== null &&
    !isLoading;

  const handleStartPressIn = () => Animated.spring(btnScaleAnim, { toValue: 0.97, useNativeDriver: true }).start();
  const handleStartPressOut = () => Animated.spring(btnScaleAnim, { toValue: 1, useNativeDriver: true }).start();

  const handleStart = async () => {
    if (!canStart || isLoading) return;
    setIsLoading(true);

    try {
      const response = await apiClient.post('/interviews/start/', {
        mode: selectedMode,
        language: selectedLang || '',
        question_count: questionCount,
      });

      setSessionId(response.data.session_id);
      setQuestion(response.data.message);
      
      setPhase('ACTIVE');
      setAnswer('');
      setFeedback(null);
      setTimer(0);
    } catch (error: any) {
      if (error.response?.status === 403) {
        setShowPaywall(true);
      } else {
        Alert.alert('Error', 'Could not start interview.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = () => {
    if (!answer.trim()) return;
    
    evaluateAI.mutate(
      { question, answer },
      {
        onSuccess: (data) => {
          const mockedScore = Math.floor(Math.random() * 20) + 75; // 75-95 mock
          setFeedback({ ...data, score: mockedScore });
          setPhase('EVALUATION');
        },
        onError: (err: any) => {
          if (err.response?.status === 403) {
            Alert.alert('Limit Reached', 'You have reached your daily AI practice limit. Upgrade to PRO for unlimited usage!');
          } else {
            Alert.alert('Error', 'Failed to evaluate answer.');
          }
        }
      }
    );
  };

  const handleNextQuestion = () => {
    setQuestion('How do you manage complex global state in a React application? Provide examples.');
    setPhase('START');
  };

  const formatTimer = (s: number) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  const renderActiveInterview = () => (
    <View style={styles.activeContainer}>
      {/* TOP SECTION: Question Display */}
      <View style={styles.topSection}>
        <View style={styles.activeHeader}>
          <Text style={styles.questionCounter}>Question 2 of 5</Text>
          <View style={styles.progressBarBg}>
            <View style={[styles.progressBarFill, { width: '40%' }]} />
          </View>
        </View>

        <View style={styles.hrCard}>
          <View style={styles.hrBotColumn}>
            <Animated.View style={[styles.hrAvatarBg, { transform: [{ scale: pulseAnim }] }]}>
              <LinearGradient colors={['#6C63FF', '#818CF8']} style={styles.hrAvatarGradient}>
                 <Bot color="#FFF" size={24} />
              </LinearGradient>
            </Animated.View>
            <View style={styles.liveIndicatorRow}>
              <View style={styles.liveDot} />
              <Text style={styles.liveText}>Live</Text>
            </View>
          </View>
          <View style={styles.hrBubble}>
            {isTyping ? (
              <Text style={styles.typingText}>typing•••</Text>
            ) : (
              <Text style={styles.hrBubbleText}>{displayedQuestion}</Text>
            )}
          </View>
        </View>
      </View>

      {/* MIDDLE SECTION: Answer Input */}
      <View style={styles.middleSection}>
        <View style={styles.inputHeader}>
          <Text style={styles.inputLabel}>Your Answer</Text>
          <Text style={styles.timerText}>⏱ {formatTimer(timer)}</Text>
        </View>
        
        <View style={styles.textareaContainer}>
          <TextInput
            style={[styles.textarea, isFocused && styles.textareaFocused]}
            value={answer}
            onChangeText={setAnswer}
            placeholder="Speak your mind — be specific and confident..."
            placeholderTextColor="rgba(255,255,255,0.4)"
            multiline
            maxLength={1000}
            textAlignVertical="top"
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
          />
          <Text style={styles.charCounter}>{answer.length} / 1000</Text>
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tipsScroll}>
          {['Use examples', 'Mention years', 'Be concise', 'STAR method'].map((tip, i) => (
            <View key={i} style={styles.tipChip}>
              <Text style={styles.tipChipText}>{tip}</Text>
            </View>
          ))}
        </ScrollView>
      </View>

      {/* BOTTOM SECTION: Actions */}
      <View style={styles.bottomSection}>
        <TouchableOpacity style={styles.skipBtn} onPress={handleNextQuestion}>
          <Text style={styles.skipBtnText}>Skip Question</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.submitBtn, !answer.trim() && { opacity: 0.5 }]} 
          onPress={handleSubmit}
          disabled={!answer.trim() || evaluateAI.isPending}
        >
          <LinearGradient
            colors={['#6C63FF', '#818CF8']}
            style={styles.submitGradient}
            start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
          >
            {evaluateAI.isPending ? <ActivityIndicator color="#FFF" /> : (
              <>
                <Text style={styles.submitBtnText}>Submit Answer</Text>
                <ArrowRight size={18} color="#FFF" />
              </>
            )}
          </LinearGradient>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderEvaluationModal = () => {
    if (!feedback) return null;
    return (
      <Animated.View style={[styles.evalModal, { transform: [{ translateY: modalSlideAnim }] }]}>
        <LinearGradient colors={['#1e2035', '#161827']} style={styles.evalGradientBg}>
          <View style={styles.evalDragHandle} />
          
          <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 40 }}>
            {/* Animated Score Ring */}
            <View style={styles.scoreContainer}>
               <View style={styles.scoreRing}>
                  <Text style={styles.scoreValue}>{feedback.score}</Text>
                  <Text style={styles.scoreMax}>/ 100</Text>
               </View>
            </View>

            {/* Rating Breakdown */}
            <View style={styles.breakdownSection}>
              {[
                { label: 'Relevance', score: 8, max: 10 },
                { label: 'Clarity', score: 7, max: 10 },
                { label: 'Examples', score: 9, max: 10 }
              ].map((item, idx) => (
                <View key={idx} style={styles.breakdownRow}>
                  <Text style={styles.breakdownLabel}>{item.label}</Text>
                  <View style={styles.breakdownBarBg}>
                    <View style={[styles.breakdownBarFill, { width: `${(item.score / item.max) * 100}%` }]} />
                  </View>
                  <Text style={styles.breakdownScore}>{item.score}/{item.max}</Text>
                </View>
              ))}
            </View>

            {/* AI Feedback */}
            <View style={styles.feedbackBox}>
               <Text style={styles.feedbackText}>{feedback.evaluation}</Text>
            </View>

            {/* Actions */}
            <View style={styles.evalActions}>
              <TouchableOpacity style={styles.evalTryAgain} onPress={() => setPhase('ACTIVE')}>
                <RefreshCw size={16} color="#E0E0E0" />
                <Text style={styles.evalTryAgainText}>Try Again</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.evalNext} onPress={handleNextQuestion}>
                <Text style={styles.evalNextText}>Next Question</Text>
                <ArrowRight size={16} color="#FFF" />
              </TouchableOpacity>
            </View>
          </ScrollView>

        </LinearGradient>
      </Animated.View>
    );
  };

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      {phase === 'START' && showPaywall && (
        <View style={styles.lobbyContainer}>
          <View style={styles.paywallBox}>
             <View style={{alignItems: 'center', marginBottom: 20}}>
               <XCircle size={48} color="#EF4444" />
             </View>
             <Text style={styles.paywallTitle}>Daily Limit Reached</Text>
             <Text style={styles.paywallSubtitle}>You've used all interviews for today</Text>

             <TouchableOpacity style={styles.planCard} onPress={() => navigation.navigate('Subscription')}>
                <Text style={styles.planFeature}>💎 PRO    5/day   $5/mo  →</Text>
             </TouchableOpacity>

             <TouchableOpacity style={styles.planCard} onPress={() => navigation.navigate('Subscription')}>
                <Text style={styles.planFeature}>🚀 PRO+  10/day  $10/mo  →</Text>
             </TouchableOpacity>

             <Text style={styles.paywallResetTime}>Resets tomorrow</Text>
             <TouchableOpacity style={styles.evalTryAgain} onPress={() => navigation.goBack()}>
                <Text style={styles.evalTryAgainText}>Come back tomorrow</Text>
             </TouchableOpacity>
          </View>
        </View>
      )}

      {phase === 'START' && !showPaywall && (
        <View style={styles.lobbyContainer}>
          <ScrollView showsVerticalScrollIndicator={false}>
            {/* HEADER */}
            <View style={styles.header}>
              <View style={styles.botAvatarLarge}>
                <Animated.View style={[styles.pulseRing1, { transform: [{ scale: pulseAnim }], opacity: pulseAnim.interpolate({inputRange: [1, 1.05], outputRange: [1, 0]}) }]} />
                <Animated.View style={[styles.pulseRing2, { transform: [{ scale: pulseAnim }], opacity: pulseAnim.interpolate({inputRange: [1, 1.05], outputRange: [1, 0]}) }]} />
                <Bot size={40} color="#fff" />
              </View>
              <Text style={styles.title}>Ready for your AI Interview?</Text>
              <Text style={styles.subtitle}>
                Our HR Bot will ask you real questions and evaluate answers
              </Text>

              {/* Quota badge */}
              {quota && (
                <View style={styles.quotaBadge}>
                  <Text style={styles.quotaText}>🎯 {quota.remaining}/{quota.limit} interviews today</Text>
                </View>
              )}
            </View>

            {/* STEP 1 — MODE SELECTION */}
            <Text style={styles.sectionLabel}>Choose Interview Type</Text>
            {[
              {
                id: 'hr', icon: '👔', title: 'HR Interview', subtitle: 'Soft skills, motivation, teamwork', color: '#2d5986', gradient: ['#1e3a5f', '#2d5986'],
              },
              {
                id: 'tech', icon: '💻', title: 'Technical', subtitle: 'Code, architecture, best practices', color: '#4338ca', gradient: ['#1a1e3a', '#4338ca'],
              },
              {
                id: 'combined', icon: '🎯', title: 'Full Interview', subtitle: 'HR + Technical combined', color: '#065f46', gradient: ['#1a3a2d', '#065f46'],
              },
            ].map(mode => (
              <TouchableOpacity
                key={mode.id}
                onPress={() => setSelectedMode(mode.id as any)}
                style={[
                  styles.modeCard,
                  selectedMode === mode.id && { borderColor: mode.color, borderWidth: 2 }
                ]}
              >
                <LinearGradient
                  colors={selectedMode === mode.id ? mode.gradient : ['#161827', '#1e2035']}
                  style={styles.modeCardInner}
                >
                  <Text style={styles.modeIcon}>{mode.icon}</Text>
                  <View style={styles.modeInfo}>
                    <Text style={styles.modeTitle}>{mode.title}</Text>
                    <Text style={styles.modeSubtitle}>{mode.subtitle}</Text>
                  </View>
                  {selectedMode === mode.id && (
                    <View style={styles.checkmark}>
                      <Text style={{color: '#fff', fontWeight: 'bold'}}>✓</Text>
                    </View>
                  )}
                </LinearGradient>
              </TouchableOpacity>
            ))}

            {/* STEP 2 — LANGUAGE */}
            {(selectedMode === 'tech' || selectedMode === 'combined') && (
              <Reanimated.View entering={FadeInDown.duration(300)} style={styles.section}>
                <Text style={styles.sectionLabel}>Programming Language</Text>
                <View style={styles.languageGrid}>
                  {[
                    { id: 'python', icon: '🐍', label: 'Python' },
                    { id: 'javascript', icon: '🟨', label: 'JavaScript' },
                    { id: 'java', icon: '☕', label: 'Java' },
                    { id: 'go', icon: '🔵', label: 'Go' },
                    { id: 'csharp', icon: '🟣', label: 'C#' },
                    { id: 'typescript', icon: '🔷', label: 'TypeScript' },
                  ].map(lang => (
                    <TouchableOpacity
                      key={lang.id}
                      onPress={() => setSelectedLang(lang.id)}
                      style={[styles.langChip, selectedLang === lang.id && styles.langChipActive]}
                    >
                      <Text>{lang.icon}</Text>
                      <Text style={[styles.langLabel, selectedLang === lang.id && styles.langLabelActive]}>{lang.label}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </Reanimated.View>
            )}

            {/* STEP 3 — KILKIST PYTAN */}
            <Text style={styles.sectionLabel}>Number of Questions</Text>
            <View style={styles.countRow}>
              {[
                { count: 10, time: '~15 min' },
                { count: 15, time: '~25 min' },
                { count: 20, time: '~35 min' },
              ].map(opt => (
                <TouchableOpacity
                  key={opt.count}
                  onPress={() => setQuestionCount(opt.count)}
                  style={[styles.countCard, questionCount === opt.count && styles.countCardActive]}
                >
                  <Text style={styles.countNumber}>{opt.count}</Text>
                  <Text style={styles.countTime}>{opt.time}</Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* SUMMARY */}
            {selectedMode && (
              <View style={styles.summaryCard}>
                <Text style={styles.summaryText}>
                  {selectedMode === 'hr' && '👔 HR Interview'}
                  {selectedMode === 'tech' && `💻 ${selectedLang || '...'} Technical`}
                  {selectedMode === 'combined' && `🎯 Full: HR + ${selectedLang || '...'}`}
                  {'  •  '}{questionCount || '?'} questions  {'  •  '}
                  {questionCount === 10 ? '~15 min' : questionCount === 15 ? '~25 min' : questionCount === 20 ? '~35 min' : '? mins'}
                </Text>
              </View>
            )}

            {/* Spacing for bottom bar */}
            <View style={{height: 120}} />
          </ScrollView>

          {/* START BUTTON */}
          <View style={styles.bottomBar}>
            <TouchableOpacity
              activeOpacity={0.8}
              style={[styles.startBtn, (!canStart) && styles.startBtnDisabled]}
              onPress={handleStart}
              disabled={!canStart || isLoading}
            >
              <LinearGradient colors={['#4338ca', '#6C63FF']} style={styles.startBtnGradient}>
                {isLoading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <>
                    <Play size={20} color="#fff" />
                    <Text style={styles.startBtnText}>Start Interview</Text>
                  </>
                )}
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {(phase === 'ACTIVE' || phase === 'EVALUATION') && renderActiveInterview()}
      
      {phase === 'EVALUATION' && (
        <>
          <View style={styles.modalBackdrop} />
          {renderEvaluationModal()}
        </>
      )}
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0d0f1a',
  },
  // -- Phase 1: Pre-Interview Lobby --
  lobbyContainer: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    paddingTop: 40,
    paddingBottom: 24,
    paddingHorizontal: 20,
  },
  botAvatarLarge: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#6C63FF',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  pulseRing1: {
    position: 'absolute',
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 2,
    borderColor: 'rgba(108,99,255,0.4)',
  },
  pulseRing2: {
    position: 'absolute',
    width: 140,
    height: 140,
    borderRadius: 70,
    borderWidth: 1,
    borderColor: 'rgba(108,99,255,0.2)',
  },
  quotaBadge: {
    backgroundColor: 'rgba(108,99,255,0.15)',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: 'rgba(108,99,255,0.3)',
    marginTop: 12,
  },
  quotaText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFF',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#A0A0B0',
    textAlign: 'center',
    paddingHorizontal: 10,
  },
  sectionLabel: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 20,
    marginTop: 20,
    marginBottom: 12,
  },
  modeCard: {
    marginHorizontal: 20,
    marginBottom: 12,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    overflow: 'hidden',
  },
  modeCardInner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    gap: 16,
  },
  modeIcon: {
    fontSize: 32,
  },
  modeInfo: {
    flex: 1,
  },
  modeTitle: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  modeSubtitle: {
    color: '#94a3b8',
    fontSize: 13,
  },
  checkmark: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#10b981',
    alignItems: 'center',
    justifyContent: 'center',
  },
  section: {},
  languageGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    paddingHorizontal: 20,
  },
  langChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: '#161827',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  langChipActive: {
    backgroundColor: 'rgba(108,99,255,0.2)',
    borderColor: '#6C63FF',
  },
  langLabel: {
    color: '#a1a1aa',
    fontWeight: '500',
  },
  langLabelActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  countRow: {
    flexDirection: 'row',
    gap: 12,
    paddingHorizontal: 20,
  },
  countCard: {
    flex: 1,
    backgroundColor: '#161827',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  countCardActive: {
    backgroundColor: 'rgba(108,99,255,0.2)',
    borderColor: '#6C63FF',
  },
  countNumber: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  countTime: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 4,
  },
  summaryCard: {
    margin: 20,
    backgroundColor: 'rgba(108,99,255,0.1)',
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: 'rgba(108,99,255,0.2)',
    alignItems: 'center',
  },
  summaryText: {
    color: '#fff',
    fontWeight: '500',
  },
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 20,
    paddingBottom: 36,
    backgroundColor: '#0d0f1a',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
  startBtn: {
    borderRadius: 16,
    overflow: 'hidden',
  },
  startBtnGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    paddingVertical: 18,
  },
  startBtnDisabled: {
    opacity: 0.5,
  },
  startBtnText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  paywallBox: {
    backgroundColor: '#161827',
    borderRadius: 24,
    padding: 30,
    borderWidth: 1,
    borderColor: 'rgba(108,99,255,0.3)',
  },
  paywallTitle: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  paywallSubtitle: {
    color: '#e2e8f0',
    textAlign: 'center',
    marginBottom: 30,
    fontSize: 16,
  },
  planCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  planFeature: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  paywallResetTime: {
    color: '#94a3b8',
    textAlign: 'center',
    marginTop: 20,
    marginBottom: 10,
  },

  // -- Phase 2: Active Interview --
  activeContainer: {
    flex: 1,
    padding: 20,
    paddingTop: 60,
  },
  topSection: {
    marginBottom: 24,
  },
  activeHeader: {
    marginBottom: 20,
  },
  questionCounter: {
    color: '#6C63FF',
    fontSize: 14,
    fontWeight: 'bold',
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  progressBarBg: {
    height: 4,
    backgroundColor: '#1E2035',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#6C63FF',
    borderRadius: 2,
  },
  hrCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  hrBotColumn: {
    alignItems: 'center',
    width: 60,
  },
  hrAvatarBg: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginBottom: 8,
    overflow: 'hidden',
  },
  hrAvatarGradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  liveIndicatorRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
  },
  liveDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#10B981',
    marginRight: 4,
  },
  liveText: {
    color: '#E0E0E0',
    fontSize: 10,
    fontWeight: 'bold',
  },
  hrBubble: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
    borderRadius: 16,
    borderTopLeftRadius: 4,
    padding: 20,
    marginLeft: 12,
  },
  typingText: {
    color: '#888',
    fontStyle: 'italic',
    fontSize: 16,
    letterSpacing: 2,
  },
  hrBubbleText: {
    color: '#FFF',
    fontSize: 16,
    lineHeight: 26,
  },

  middleSection: {
    flex: 1,
  },
  inputHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
    paddingHorizontal: 4,
  },
  inputLabel: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  timerText: {
    color: '#A0A0B0',
    fontSize: 14,
  },
  textareaContainer: {
    position: 'relative',
    marginBottom: 16,
  },
  textarea: {
    backgroundColor: '#161827',
    borderWidth: 1,
    borderColor: 'rgba(108,99,255,0.3)',
    borderRadius: 16,
    color: '#FFF',
    padding: 20,
    paddingTop: 20,
    minHeight: 200,
    fontSize: 16,
    lineHeight: 24,
  },
  textareaFocused: {
    borderColor: '#6C63FF',
    shadowColor: '#6C63FF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.4,
    shadowRadius: 10,
    elevation: 8,
  },
  charCounter: {
    position: 'absolute',
    bottom: 16,
    right: 20,
    color: '#888',
    fontSize: 12,
  },
  tipsScroll: {
    flexGrow: 0,
    marginBottom: 20,
  },
  tipChip: {
    backgroundColor: '#1E2035',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  tipChipText: {
    color: '#A0A0B0',
    fontSize: 13,
    fontWeight: '600',
  },

  bottomSection: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 20,
  },
  skipBtn: {
    flex: 1,
    height: 56,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
  },
  skipBtnText: {
    color: '#A0A0B0',
    fontSize: 16,
    fontWeight: 'bold',
  },
  submitBtn: {
    flex: 1.5,
    height: 56,
    borderRadius: 28,
    overflow: 'hidden',
  },
  submitGradient: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 10,
  },
  submitBtnText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },

  // -- Phase 3: Evaluation Modal --
  modalBackdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(13,15,26,0.85)',
    zIndex: 10,
  },
  evalModal: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '75%',
    zIndex: 20,
    borderTopLeftRadius: 32,
    borderTopRightRadius: 32,
    overflow: 'hidden',
  },
  evalGradientBg: {
    flex: 1,
    padding: 24,
  },
  evalDragHandle: {
    width: 48,
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 3,
    alignSelf: 'center',
    marginBottom: 24,
  },
  evalHeader: {
    color: '#FFF',
    fontSize: 22,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 24,
  },
  scoreContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  scoreRing: {
    width: 140,
    height: 140,
    borderRadius: 70,
    borderWidth: 8,
    borderColor: '#6C63FF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#6C63FF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.6,
    shadowRadius: 20,
    elevation: 10,
  },
  scoreValue: {
    color: '#FFF',
    fontSize: 42,
    fontWeight: '900',
  },
  scoreMax: {
    color: '#A0A0B0',
    fontSize: 16,
    marginTop: -4,
  },
  breakdownSection: {
    marginBottom: 24,
  },
  breakdownTitle: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  breakdownRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  breakdownLabel: {
    width: 90,
    color: '#E0E0E0',
    fontSize: 14,
    fontWeight: '600',
  },
  breakdownBarBg: {
    flex: 1,
    height: 8,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 4,
    marginHorizontal: 12,
    overflow: 'hidden',
  },
  breakdownBarFill: {
    height: '100%',
    backgroundColor: '#6C63FF',
    borderRadius: 4,
  },
  breakdownScore: {
    width: 40,
    color: '#FFF',
    fontSize: 14,
    textAlign: 'right',
    fontWeight: 'bold',
  },
  feedbackBox: {
    backgroundColor: 'rgba(255,255,255,0.04)',
    padding: 20,
    borderRadius: 16,
    marginBottom: 32,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
  },
  feedbackText: {
    color: '#E0E0E0',
    fontSize: 15,
    lineHeight: 24,
  },
  evalActions: {
    flexDirection: 'row',
    gap: 12,
    paddingBottom: 20,
  },
  evalTryAgain: {
    flex: 1,
    height: 56,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
    borderRadius: 28,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  evalTryAgainText: {
    color: '#E0E0E0',
    fontSize: 16,
    fontWeight: 'bold',
  },
  evalNext: {
    flex: 1.5,
    height: 56,
    backgroundColor: '#6C63FF',
    borderRadius: 28,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    shadowColor: '#6C63FF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 10,
    elevation: 8,
  },
  evalNextText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
