import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl, ActivityIndicator } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { theme } from '../theme';
import { StatCard } from '../components/ui/StatCard';
import { StreakBadge } from '../components/ui/StreakBadge';
import { AnimatedProgressBar } from '../components/ui/AnimatedProgressBar';
import { QuickActionBtn } from '../components/ui/QuickActionBtn';
import { LinearGradient } from 'expo-linear-gradient';
import { Play, Target, Zap, Clock, Trophy, BookOpen, Brain, BarChart2, RefreshCw } from 'lucide-react-native';
import { useAuthStore } from '../store/useAuthStore';
import { apiClient } from '../api/client';
import { useFocusEffect } from '@react-navigation/native';
import Animated, { FadeInDown, useAnimatedStyle, useSharedValue, withSpring } from 'react-native-reanimated';
import { useTranslation } from 'react-i18next';
import { useLanguage } from '../hooks/useLanguage';
import { storage } from '../utils/storage';
import { getTimeUntilMidnight } from '../utils/time';

export const HomeScreen = ({ navigation }: any) => {
  const { t, i18n } = useTranslation();
  const { switchLanguage, loading: langLoading } = useLanguage();
  const insets = useSafeAreaInsets();
  const { user } = useAuthStore();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState('');
  
  const playScale = useSharedValue(1);

  useFocusEffect(
    useCallback(() => {
      const interval = setInterval(() => {
        setTimeRemaining(getTimeUntilMidnight());
      }, 60000);
      setTimeRemaining(getTimeUntilMidnight());
      
      return () => clearInterval(interval);
    }, [])
  );

  const fetchDashboard = useCallback(async (isRefresh = false) => {
    try {
      if (!isRefresh) setLoading(true);
      setError(false);
      
      const res = await apiClient.get('/api/home/dashboard/');
      setData(res.data);
      
      // User hasn't finished onboarding
      if (res.data.onboarding_completed === false) {
        navigation.replace('Onboarding');
      }

    } catch (err) {
      console.error('Dashboard Error:', err);
      setError(true);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [navigation]);

  useFocusEffect(
    useCallback(() => {
      fetchDashboard();
    }, [fetchDashboard])
  );

  const onRefresh = () => {
    setRefreshing(true);
    fetchDashboard(true);
  };

  const handlePlayPress = async () => {
    playScale.value = withSpring(0.9, {}, () => {
      playScale.value = withSpring(1);
    });
    if (data?.next_up) {
      try {
         const res = await apiClient.post(`/api/home/start-topic/${data.next_up.topic_id}/`);
         navigation.navigate('Learning', { 
           questionId: res.data.first_question_id, 
           resume: true 
         });
      } catch (e) {
         console.warn("Failed starting topic");
      }
    }
  };

  const playAnimatedStyle = useAnimatedStyle(() => {
    return {
      transform: [{ scale: playScale.value }],
    };
  });

  const handleLanguageToggle = () => {
    if (langLoading) return;
    const nextLang = i18n.language === 'en' ? 'uk' : 'en';
    switchLanguage(nextLang);
  };

  const getLanguageIcon = (lang: string) => {
    switch(lang?.toLowerCase()) {
      case 'python': return '🐍 ';
      case 'javascript': return '🟨 ';
      case 'java': return '☕ ';
      case 'go': return '🔵 ';
      case 'csharp': return '🟣 ';
      default: return '💻 ';
    }
  };

  if (loading && !data) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color={theme.colors.primary.DEFAULT} />
      </View>
    );
  }

  if (error && !data) {
    return (
      <View style={[styles.container, styles.centered]}>
        <Text style={styles.errorText}>Couldn't load data</Text>
        <TouchableOpacity style={styles.retryButton} onPress={() => fetchDashboard()}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const isNewUser = data?.progress_today?.xp === 0 && data?.progress_today?.questions_answered === 0;

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <ScrollView 
        showsVerticalScrollIndicator={false} 
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl 
            refreshing={refreshing} 
            onRefresh={onRefresh} 
            tintColor={theme.colors.primary.DEFAULT}
            colors={[theme.colors.primary.DEFAULT]}
          />
        }
      >
        {/* Header Section */}
        <Animated.View entering={FadeInDown.delay(100).springify()} style={styles.header}>
          <View>
            <Text style={styles.greeting}>{data?.user?.greeting || t('home.greeting_morning')}</Text>
            <Text style={styles.name}>{data?.user?.name || 'Explorer'} 👋</Text>
          </View>
          <View style={styles.headerRight}>
            <TouchableOpacity 
              style={styles.langToggleBtn} 
              onPress={handleLanguageToggle}
              disabled={langLoading}
            >
              <Text style={styles.langToggleText}>
                {i18n.language === 'en' ? '🇺🇸 EN' : '🇺🇦 UK'}
              </Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => navigation.navigate('Progress')}>
              <StreakBadge count={data?.streak?.current || 0} />
            </TouchableOpacity>
          </View>
        </Animated.View>

        {/* Continue Learning Highlight Card */}
        <Animated.View entering={FadeInDown.delay(200).springify()}>
          {data?.next_up ? (
            <TouchableOpacity activeOpacity={0.9} style={styles.heroCardContainer} onPress={handlePlayPress}>
              <LinearGradient
                colors={['#4338ca', '#6C63FF']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.heroCard}
              >
                <View style={styles.heroContent}>
                  <View>
                    <Text style={styles.heroSubtitle}>{t('home.next_up')}</Text>
                    <Text style={styles.heroTitle}>
                      {getLanguageIcon(data.next_up.language)}{data.next_up.topic}
                    </Text>
                  </View>
                  <Animated.View style={[styles.playButton, playAnimatedStyle]}>
                    <Play fill={theme.colors.primary.DEFAULT} color={theme.colors.primary.DEFAULT} size={20} />
                  </Animated.View>
                </View>
                <View style={styles.heroFooter}>
                  <AnimatedProgressBar 
                    progress={data.next_up.progress_percent} 
                    colorStart="rgba(255,255,255,0.5)" 
                    colorEnd="#ffffff" 
                  />
                  <View style={styles.rowBetween}>
                    <Text style={styles.heroProgressText}>{t('home.complete', { percent: data.next_up.progress_percent })}</Text>
                    <Text style={styles.heroRemainingText}>{100 - data.next_up.progress_percent}%</Text>
                  </View>
                </View>
              </LinearGradient>
            </TouchableOpacity>
          ) : (
            <View style={[styles.heroCardContainer, styles.heroCardEmpty]}>
              <Text style={styles.heroTitleEmpty}>{t('home.all_topics_complete')}</Text>
              <Text style={styles.heroSubtitleEmpty}>{t('home.try_ai')}</Text>
            </View>
          )}
        </Animated.View>

        {/* Quick Stats Grid */}
        <Animated.View entering={FadeInDown.delay(300).springify()}>
          <Text style={styles.sectionTitle}>{t('home.your_progress')}</Text>
          <View style={styles.statsGrid}>
            <StatCard 
              icon={Zap} 
              number={isNewUser ? '—' : data?.progress_today?.xp || 0} 
              label={t('home.xp_today')} 
              color="#fbbf24"
              animate={!isNewUser}
              trendLabel={data?.progress_today?.xp > data?.progress_today?.xp_yesterday ? `▲ +${data.progress_today.xp - data.progress_today.xp_yesterday}` : undefined}
            />
            <StatCard 
              icon={Target} 
              number={isNewUser ? '—' : data?.progress_today?.questions_answered || 0} 
              label={t('home.questions')} 
              color="#22c55e"
              animate={!isNewUser}
              caption={t('home.personal_best', { count: data?.progress_today?.personal_best_questions || 0 })}
            />
          </View>
        </Animated.View>

        {/* Quick Actions */}
        <Animated.View entering={FadeInDown.delay(400).springify()} style={styles.quickActions}>
          <QuickActionBtn icon={<BookOpen size={20} color="#fff" />} label={t('home.practice')} onPress={() => navigation.navigate('Learning')} />
          <QuickActionBtn icon={<Brain size={20} color="#fff" />} label={t('home.ai_interview')} onPress={() => navigation.navigate('AI')} />
          <QuickActionBtn icon={<BarChart2 size={20} color="#fff" />} label={t('home.stats')} onPress={() => navigation.navigate('Progress')} />
        </Animated.View>

        {/* Daily Challenge Card System */}
        <Animated.View entering={FadeInDown.delay(500).springify()}>
          <View style={styles.sectionHeaderRow}>
            <Text style={styles.sectionTitle}>{t('home.daily_challenges')}</Text>
            <View style={styles.timerBadge}>
              <Clock size={12} color={theme.colors.text.secondary} />
              <Text style={styles.timerBadgeText}>{t('home.resets_in', { time: timeRemaining })}</Text>
            </View>
          </View>
          
          <View style={styles.challengesContainer}>
            {data?.daily_challenges?.length > 0 ? (
              data.daily_challenges.every((c: any) => c.is_completed) ? (
                <View style={styles.allDoneCard}>
                  <Text style={styles.allDoneTitle}>{t('home.all_topics_complete')}</Text>
                  <Text style={styles.allDoneSubtitle}>{t('home.check_tomorrow')}</Text>
                </View>
              ) : (
                data.daily_challenges.map((challenge: any, index: number) => {
                  const isCompleted = challenge.is_completed;
                  return (
                    <Animated.View key={challenge.id} entering={FadeInDown.delay(500 + (index * 100)).springify()}>
                      <TouchableOpacity 
                        style={[
                          styles.challengeCard, 
                          isNewUser && styles.lockedChallenge,
                          isCompleted && styles.completedChallengeCard
                        ]} 
                        disabled={isNewUser || isCompleted}
                        onPress={() => {
                          if (challenge.challenge_type === 'answer_hard') {
                            navigation.navigate('Learning', { difficulty: 'hard' });
                          } else if (challenge.challenge_type === 'ai_interview') {
                            navigation.navigate('AI');
                          } else if (challenge.challenge_type === 'complete_topic') {
                            // Find topic ID logic or just general learning screen
                            navigation.navigate('Learning');
                          } else {
                            // General answer questions
                            navigation.navigate('Learning');
                          }
                        }}
                      >
                        <View style={styles.challengeHeader}>
                          <View style={styles.challengeIconRow}>
                            <View style={[styles.challengeIconBg, isCompleted && styles.completedIconBg]}>
                              <Text style={{fontSize: 20}}>{challenge.icon}</Text>
                            </View>
                            <Text style={styles.challengeTitle}>
                              {isNewUser ? '🔒 Complete 1 lesson to unlock' : challenge.title}
                            </Text>
                          </View>
                          {!isNewUser && (
                            <Text style={styles.rewardTextMini}>{challenge.bonus_xp} XP</Text>
                          )}
                        </View>
                        
                        {!isNewUser && (
                          <View style={styles.challengeFooter}>
                            {isCompleted ? (
                              <View style={styles.completedFoot}>
                                <Text style={styles.completedFootText}>✅ Complete! +{challenge.bonus_xp} XP earned</Text>
                              </View>
                            ) : (
                              <>
                                <AnimatedProgressBar 
                                  progress={challenge.percent} 
                                  colorStart="#8b5cf6" 
                                  colorEnd="#a855f7" 
                                  label={`${challenge.completed_count}/${challenge.goal_count}      ${challenge.percent}%`}
                                />
                                <View style={styles.dotsRow}>
                                  {Array.from({ length: Math.min(challenge.goal_count, 15) }).map((_, i) => (
                                    <View key={i} style={[
                                      styles.dot, 
                                      i < challenge.completed_count ? styles.dotFilled : null
                                    ]} />
                                  ))}
                                </View>
                              </>
                            )}
                          </View>
                        )}
                      </TouchableOpacity>
                    </Animated.View>
                  );
                })
              )
            ) : (
              <View style={styles.challengeCard}>
                <Text style={styles.challengeTitle}>{t('home.check_tomorrow')}</Text>
              </View>
            )}
          </View>
        </Animated.View>
        
        {/* Bottom padding for Custom Tab Bar */}
        <View style={{ height: 100 }} />
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: theme.colors.background.primary 
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    color: theme.colors.text.secondary,
    marginBottom: 16,
  },
  retryButton: {
    padding: 12,
    backgroundColor: theme.colors.background.card,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 32,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  langToggleBtn: {
    backgroundColor: theme.colors.background.elevated,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  langToggleText: {
    color: theme.colors.text.primary,
    fontWeight: theme.typography.weight.bold,
    fontSize: 14,
  },
  greeting: {
    fontSize: 14,
    color: '#94a3b8',
    marginBottom: 4,
  },
  name: {
    fontSize: 28,
    fontWeight: theme.typography.weight.bold,
    color: theme.colors.text.primary,
  },
  heroCardContainer: {
    borderRadius: 24,
    shadowColor: '#6C63FF',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
    marginBottom: 32,
  },
  heroCardEmpty: {
    backgroundColor: '#1e2035',
    padding: 32,
    alignItems: 'center',
  },
  heroTitleEmpty: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  heroSubtitleEmpty: {
    color: '#94a3b8',
    fontSize: 14,
  },
  heroCard: {
    borderRadius: 24,
    padding: 24,
    minHeight: 160,
    justifyContent: 'space-between',
  },
  heroContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  heroSubtitle: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 11,
    fontWeight: theme.typography.weight.bold,
    letterSpacing: 1.2,
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  heroTitle: {
    color: theme.colors.text.primary,
    fontSize: 22,
    fontWeight: theme.typography.weight.bold,
  },
  playButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: theme.colors.text.primary,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
  },
  heroFooter: {
    marginTop: 24,
  },
  rowBetween: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  heroProgressText: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 12,
    fontWeight: theme.typography.weight.medium,
  },
  heroRemainingText: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 12,
  },
  sectionTitle: {
    fontSize: theme.typography.size.h3,
    fontWeight: theme.typography.weight.bold,
    color: theme.colors.text.primary,
  },
  statsGrid: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 24,
  },
  quickActions: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 32,
  },
  sectionHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  timerBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  timerBadgeText: {
    fontSize: 12,
    color: theme.colors.text.secondary,
  },
  challengesContainer: {
    gap: 12,
  },
  challengeCard: {
    backgroundColor: '#161827',
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: 'rgba(108, 99, 255, 0.3)',
  },
  completedChallengeCard: {
    borderColor: 'rgba(34, 197, 94, 0.4)',
    backgroundColor: 'rgba(34, 197, 94, 0.05)',
  },
  lockedChallenge: {
    opacity: 0.5,
  },
  allDoneCard: {
    backgroundColor: '#161827',
    borderRadius: 20,
    padding: 32,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(34, 197, 94, 0.3)',
  },
  allDoneTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 8,
  },
  allDoneSubtitle: {
    fontSize: 14,
    color: theme.colors.text.secondary,
  },
  challengeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  challengeIconRow: {
    flex: 1,
    paddingRight: 16,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  challengeIconBg: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(108, 99, 255, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  completedIconBg: {
    backgroundColor: 'rgba(34, 197, 94, 0.15)',
  },
  challengeTitle: {
    fontSize: 15,
    fontWeight: theme.typography.weight.semibold,
    color: theme.colors.text.primary,
    flex: 1,
  },
  rewardTextMini: {
    color: '#fbbf24',
    fontSize: 14,
    fontWeight: 'bold',
  },
  challengeFooter: {
    marginTop: 16,
  },
  completedFoot: {
    paddingTop: 8,
  },
  completedFootText: {
    color: '#22c55e',
    fontSize: 14,
    fontWeight: '600',
  },
  dotsRow: {
    flexDirection: 'row',
    gap: 4,
    marginTop: 12,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  dotFilled: {
    backgroundColor: '#8b5cf6',
  }
});
