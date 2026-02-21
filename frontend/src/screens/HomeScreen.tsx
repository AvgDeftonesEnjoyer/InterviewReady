import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { theme } from '../theme';
import { StatCard } from '../components/ui/StatCard';
import { StreakBadge } from '../components/ui/StreakBadge';
import { ProgressBar } from '../components/ui/ProgressBar';
import { LinearGradient } from 'expo-linear-gradient';
import { Play, Target, Zap, Clock, Trophy } from 'lucide-react-native';
import { useAuthStore } from '../store/useAuthStore';

export const HomeScreen = () => {
  const insets = useSafeAreaInsets();
  const { user } = useAuthStore();
  
  // Dummy data for now
  const userName = user?.email?.split('@')[0] || 'Explorer';
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        
        {/* Header Section */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>{getGreeting()},</Text>
            <Text style={styles.name}>{userName} 👋</Text>
          </View>
          <StreakBadge count={12} />
        </View>

        {/* Continue Learning Highlight Card */}
        <TouchableOpacity activeOpacity={0.9} style={styles.heroCardContainer}>
          <LinearGradient
            colors={[theme.colors.primary.DEFAULT, '#4F46E5']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.heroCard}
          >
            <View style={styles.heroContent}>
              <View>
                <Text style={styles.heroSubtitle}>NEXT UP</Text>
                <Text style={styles.heroTitle}>Python Architecture</Text>
              </View>
              <View style={styles.playButton}>
                <Play fill={theme.colors.primary.DEFAULT} color={theme.colors.primary.DEFAULT} size={20} />
              </View>
            </View>
            <View style={styles.heroFooter}>
              <ProgressBar 
                progress={65} 
                showPercentage={false} 
                colorStart="rgba(255,255,255,0.5)" 
                colorEnd="#ffffff" 
              />
              <Text style={styles.heroProgressText}>65% Complete</Text>
            </View>
          </LinearGradient>
        </TouchableOpacity>

        {/* Quick Stats Grid */}
        <Text style={styles.sectionTitle}>Your Progress</Text>
        <View style={styles.statsGrid}>
          <StatCard icon={Zap} number={450} label="XP Today" color={theme.colors.status.warning} />
          <StatCard icon={Target} number={24} label="Questions" color={theme.colors.status.success} />
        </View>

        {/* Daily Challenge Card */}
        <Text style={styles.sectionTitle}>Daily Challenge</Text>
        <View style={styles.challengeCard}>
          <View style={styles.challengeHeader}>
            <View style={styles.challengeIconRow}>
              <View style={styles.challengeIconBg}>
                <Trophy size={20} color={theme.colors.status.warning} />
              </View>
              <Text style={styles.challengeTitle}>Answer 10 Hard Questions</Text>
            </View>
            <View style={styles.timerChip}>
              <Clock size={12} color={theme.colors.status.error} style={{marginRight: 4}} />
              <Text style={styles.timerText}>4h 12m</Text>
            </View>
          </View>
          <ProgressBar progress={40} colorStart={theme.colors.status.warning} colorEnd="#fbbf24" label="4 / 10 Completed" />
        </View>
        
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
  greeting: {
    fontSize: theme.typography.size.body,
    color: theme.colors.text.secondary,
    marginBottom: 4,
  },
  name: {
    fontSize: theme.typography.size.h1,
    fontWeight: theme.typography.weight.bold,
    color: theme.colors.text.primary,
  },
  heroCardContainer: {
    borderRadius: 24,
    shadowColor: theme.colors.primary.DEFAULT,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
    marginBottom: 32,
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
    color: 'rgba(255,255,255,0.7)',
    fontSize: theme.typography.size.caption,
    fontWeight: theme.typography.weight.bold,
    letterSpacing: 1.2,
    marginBottom: 8,
  },
  heroTitle: {
    color: theme.colors.text.primary,
    fontSize: theme.typography.size.h2,
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
  heroProgressText: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 12,
    marginTop: 8,
    fontWeight: theme.typography.weight.medium,
  },
  sectionTitle: {
    fontSize: theme.typography.size.h3,
    fontWeight: theme.typography.weight.bold,
    color: theme.colors.text.primary,
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 32,
  },
  challengeCard: {
    backgroundColor: theme.colors.background.card,
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  challengeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  challengeIconRow: {
    flex: 1,
    paddingRight: 16,
  },
  challengeIconBg: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  challengeTitle: {
    fontSize: 16,
    fontWeight: theme.typography.weight.semibold,
    color: theme.colors.text.primary,
    lineHeight: 22,
  },
  timerChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  timerText: {
    color: theme.colors.status.error,
    fontSize: 12,
    fontWeight: theme.typography.weight.bold,
  }
});
