import React, { useState, useEffect, useRef } from 'react';
import { 
  View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, 
  Alert, Animated, Platform, ScrollView, Easing, KeyboardAvoidingView 
} from 'react-native';
import { useEvaluateAI } from './hooks';
import { LinearGradient } from 'expo-linear-gradient';
import { Bot, Play, ArrowRight, RefreshCw } from 'lucide-react-native';

type Phase = 'START' | 'ACTIVE' | 'EVALUATION';

export const AIPracticeScreen = () => {
  const [phase, setPhase] = useState<Phase>('START');
  
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

  const handleStartPressIn = () => Animated.spring(btnScaleAnim, { toValue: 0.97, useNativeDriver: true }).start();
  const handleStartPressOut = () => Animated.spring(btnScaleAnim, { toValue: 1, useNativeDriver: true }).start();

  const handleStart = () => {
    setPhase('ACTIVE');
    setAnswer('');
    setFeedback(null);
    setTimer(0);
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
      {phase === 'START' && (
        <View style={styles.lobbyContainer}>
          {/* Hero Section */}
          <View style={styles.lobbyHero}>
            <Animated.View style={[styles.heroOrb, { transform: [{ scale: pulseAnim }] }]}>
              <View style={styles.heroAvatar}>
                <Bot size={40} color="#FFF" />
              </View>
            </Animated.View>

            <Text style={styles.lobbyTitle}>Ready for your AI Interview?</Text>
            <Text style={styles.lobbySubtitle}>
              Our HR Bot will ask you real interview questions and evaluate your answers with AI
            </Text>
          </View>

          {/* Settings Card */}
          <View style={styles.settingsCard}>
            <View style={styles.settingRow}>
              <Text style={styles.settingIcon}>🎯</Text>
              <Text style={styles.settingLabel}>Topic:</Text>
              <Text style={styles.settingValue}>React Native ▾</Text>
            </View>
            <View style={styles.settingRow}>
              <Text style={styles.settingIcon}>📊</Text>
              <Text style={styles.settingLabel}>Difficulty:</Text>
              <Text style={styles.settingValue}>Medium ▾</Text>
            </View>
            <View style={styles.settingRow}>
              <Text style={styles.settingIcon}>⏱</Text>
              <Text style={styles.settingLabel}>Questions:</Text>
              <Text style={styles.settingValue}>5 ▾</Text>
            </View>
          </View>

          {/* Bottom Call To Action */}
          <View style={styles.lobbyFooter}>
            <Animated.View style={{ transform: [{ scale: btnScaleAnim }] }}>
              <TouchableOpacity 
                activeOpacity={1} 
                onPressIn={handleStartPressIn} 
                onPressOut={handleStartPressOut}
                onPress={handleStart}
              >
                <LinearGradient
                  colors={['#6C63FF', '#818CF8']}
                  start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
                  style={styles.lobbyStartBtn}
                >
                  <Play size={20} color="#FFF" fill="#FFF" />
                  <Text style={styles.lobbyStartBtnText}>Start Interview</Text>
                </LinearGradient>
              </TouchableOpacity>
            </Animated.View>
            <Text style={styles.lobbyTip}>💡 Tip: Answer as you would in a real interview</Text>
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
  lobbyHero: {
    alignItems: 'center',
    marginBottom: 40,
    marginTop: 40,
  },
  heroOrb: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: 'rgba(108,99,255,0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 30,
    borderWidth: 1,
    borderColor: 'rgba(108,99,255,0.3)',
    shadowColor: '#6C63FF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.4,
    shadowRadius: 30,
    elevation: 10,
  },
  heroAvatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#6C63FF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  lobbyTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFF',
    textAlign: 'center',
    marginBottom: 16,
  },
  lobbySubtitle: {
    fontSize: 16,
    color: '#A0A0B0',
    textAlign: 'center',
    lineHeight: 24,
    paddingHorizontal: 10,
  },
  settingsCard: {
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
    borderRadius: 16,
    padding: 20,
    marginBottom: 40,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
  },
  settingIcon: {
    fontSize: 18,
    marginRight: 12,
  },
  settingLabel: {
    flex: 1,
    color: '#E0E0E0',
    fontSize: 16,
  },
  settingValue: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
  lobbyFooter: {
    marginTop: 'auto',
    marginBottom: 20,
  },
  lobbyStartBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 56,
    borderRadius: 28,
    gap: 12,
  },
  lobbyStartBtnText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  lobbyTip: {
    color: '#888',
    textAlign: 'center',
    marginTop: 16,
    fontSize: 13,
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
