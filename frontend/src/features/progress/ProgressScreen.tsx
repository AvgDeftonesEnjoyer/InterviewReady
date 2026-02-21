import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator, ScrollView, Dimensions } from 'react-native';
import { useProgressStats } from './hooks';
import { theme } from '../../theme';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { Trophy, Flame, TrendingUp, Medal, Star, Target, Zap } from 'lucide-react-native';
import { LinearGradient } from 'expo-linear-gradient';

const { width } = Dimensions.get('window');

// Mock data for the heatmap (7 days x 4 weeks = 28 days)
const STREAK_HEATMAP = Array.from({ length: 28 }, () => Math.random() > 0.4 ? Math.floor(Math.random() * 4) + 1 : 0);

// Mock data for weekly chart
const WEEKLY_DATA = [40, 65, 30, 85, 120, 50, 90];
const MAX_DATA = Math.max(...WEEKLY_DATA);

// Mock Achievements
const ACHIEVEMENTS = [
  { id: 1, title: 'First Steps', icon: Zap, unlocked: true },
  { id: 2, title: '7 Day Streak', icon: Flame, unlocked: true },
  { id: 3, title: 'Top 10%', icon: TrendingUp, unlocked: false },
  { id: 4, title: 'System Design Pro', icon: Target, unlocked: false },
  { id: 5, title: 'Perfect Interview', icon: Star, unlocked: false },
  { id: 6, title: 'Grandmaster', icon: Medal, unlocked: false },
];

export const ProgressScreen = () => {
  const { data: stats, isLoading } = useProgressStats();

  if (isLoading) {
    return (
       <View style={styles.center}>
         <ActivityIndicator size="large" color={theme.colors.primary.DEFAULT} />
       </View>
    );
  }

  if (!stats) return null;

  return (
    <ScrollView showsVerticalScrollIndicator={false} style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.header}>Your Journey</Text>

      {/* Hero Level Badge Card */}
      <LinearGradient
        colors={[theme.colors.background.card, `${theme.colors.primary.DEFAULT}15`]}
        style={styles.heroCard}
      >
        <View style={styles.levelBadgeGlow}>
           <View style={styles.levelBadge}>
              <Text style={styles.levelNumber}>{stats.current_level}</Text>
           </View>
        </View>
        
        <View style={styles.levelInfo}>
          <Text style={styles.levelTitle}>Level {stats.current_level} Scholar</Text>
          <Text style={styles.xpText}>{stats.total_xp} Total XP</Text>
        </View>

        <View style={styles.progressContainer}>
          <View style={styles.progressHeader}>
             <Text style={styles.progressLabel}>Progress to Level {stats.current_level + 1}</Text>
             <Text style={styles.progressAmount}>{stats.next_level_xp} XP left</Text>
          </View>
          <ProgressBar progress={stats.progress_percent} height={12} showPercentage={false} />
        </View>
      </LinearGradient>

      {/* Stats Row */}
      <View style={styles.statsRow}>
        <View style={styles.statBox}>
          <View style={[styles.statIconBg, { backgroundColor: `${theme.colors.status.warning}20` }]}>
             <Flame size={20} color={theme.colors.status.warning} />
          </View>
          <View>
            <Text style={styles.statValue}>{stats.streak_days}</Text>
            <Text style={styles.statLabel}>Day Streak</Text>
          </View>
        </View>
        
        <View style={styles.statBox}>
          <View style={[styles.statIconBg, { backgroundColor: `${theme.colors.primary.DEFAULT}20` }]}>
             <Trophy size={20} color={theme.colors.primary.DEFAULT} />
          </View>
          <View>
            <Text style={styles.statValue}>Top 15%</Text>
            <Text style={styles.statLabel}>This Week</Text>
          </View>
        </View>
      </View>

      {/* GitHub-style Heatmap */}
      <View style={styles.sectionCard}>
         <Text style={styles.sectionTitle}>Activity Heatmap</Text>
         <View style={styles.heatmapGrid}>
           {STREAK_HEATMAP.map((intensity, index) => {
             // Map intensity to opacity of primary color
             const backgroundColor = intensity === 0 
                ? theme.colors.background.elevated 
                : `${theme.colors.primary.DEFAULT}${Math.max(20, intensity * 25)}`;
             
             return (
               <View 
                 key={index} 
                 style={[styles.heatmapCell, { backgroundColor }]} 
               />
             );
           })}
         </View>
      </View>

      {/* Weekly Bar Chart */}
      <View style={styles.sectionCard}>
         <Text style={styles.sectionTitle}>Weekly XP</Text>
         <View style={styles.chartContainer}>
            {WEEKLY_DATA.map((value, index) => {
               const heightPercent = (value / MAX_DATA) * 100;
               const isToday = index === WEEKLY_DATA.length - 1;
               return (
                 <View key={index} style={styles.barColumn}>
                   <View style={styles.barTrack}>
                     <LinearGradient
                        colors={isToday ? [theme.colors.primary.light, theme.colors.primary.dark] : ['#3A3A4A', '#2A2A35']}
                        style={[styles.barFill, { height: `${heightPercent}%` }]}
                     />
                   </View>
                   <Text style={[styles.barLabel, isToday && styles.barLabelToday]}>
                     {['M', 'T', 'W', 'T', 'F', 'S', 'S'][index]}
                   </Text>
                 </View>
               );
            })}
         </View>
      </View>

      {/* Achievements Grid */}
      <View style={styles.sectionCard}>
         <Text style={styles.sectionTitle}>Achievements</Text>
         <View style={styles.achievementsGrid}>
            {ACHIEVEMENTS.map(ach => (
              <View key={ach.id} style={[styles.achievementBadge, !ach.unlocked && styles.achievementLocked]}>
                 <View style={[styles.achievementIconBg, !ach.unlocked && styles.iconBgLocked]}>
                    <ach.icon 
                      size={24} 
                      color={ach.unlocked ? theme.colors.primary.DEFAULT : theme.colors.text.muted} 
                    />
                 </View>
                 <Text style={styles.achievementTitle}>{ach.title}</Text>
              </View>
            ))}
         </View>
      </View>

      <View style={{ height: 100 }} /> {/* Tab bar spacer */}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: theme.colors.background.primary, 
  },
  content: {
    padding: 20,
    paddingTop: 60,
  },
  center: { 
    flex: 1, 
    backgroundColor: theme.colors.background.primary, 
    justifyContent: 'center', 
    alignItems: 'center' 
  },
  header: { 
    fontSize: theme.typography.size.h1, 
    fontWeight: theme.typography.weight.bold, 
    color: theme.colors.text.primary, 
    marginBottom: 24 
  },
  
  heroCard: {
    padding: 24,
    borderRadius: 24,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: `${theme.colors.primary.DEFAULT}30`,
    alignItems: 'center',
  },
  levelBadgeGlow: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: `${theme.colors.primary.DEFAULT}20`,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    borderWidth: 2,
    borderColor: theme.colors.primary.DEFAULT,
  },
  levelBadge: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: theme.colors.primary.DEFAULT,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: theme.colors.primary.DEFAULT,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
  },
  levelNumber: {
    color: '#FFF',
    fontSize: 36,
    fontWeight: theme.typography.weight.bold,
  },
  levelInfo: {
    alignItems: 'center',
    marginBottom: 24,
  },
  levelTitle: {
    color: theme.colors.text.primary,
    fontSize: theme.typography.size.h3,
    fontWeight: theme.typography.weight.bold,
    marginBottom: 4,
  },
  xpText: {
    color: theme.colors.text.secondary,
    fontSize: 14,
    fontWeight: theme.typography.weight.semibold,
  },
  progressContainer: {
    width: '100%',
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  progressLabel: {
    color: theme.colors.text.secondary,
    fontSize: 12,
    fontWeight: theme.typography.weight.medium,
  },
  progressAmount: {
    color: theme.colors.primary.light,
    fontSize: 12,
    fontWeight: theme.typography.weight.bold,
  },

  statsRow: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 20,
  },
  statBox: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.background.card,
    padding: 16,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  statIconBg: {
    width: 44,
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  statValue: {
    color: theme.colors.text.primary,
    fontSize: 18,
    fontWeight: theme.typography.weight.bold,
  },
  statLabel: {
    color: theme.colors.text.muted,
    fontSize: 12,
  },

  sectionCard: {
    backgroundColor: theme.colors.background.card,
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
    marginBottom: 20,
  },
  sectionTitle: {
    color: theme.colors.text.primary,
    fontSize: 18,
    fontWeight: theme.typography.weight.bold,
    marginBottom: 16,
  },

  heatmapGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  heatmapCell: {
    width: (width - 40 - 40 - 56) / 7, // calculating cell width based on container
    aspectRatio: 1,
    borderRadius: 6,
  },

  chartContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    height: 150,
    paddingTop: 20,
  },
  barColumn: {
    alignItems: 'center',
    width: '10%',
  },
  barTrack: {
    width: '100%',
    height: 100,
    backgroundColor: theme.colors.background.elevated,
    borderRadius: 6,
    justifyContent: 'flex-end',
    marginBottom: 8,
    overflow: 'hidden',
  },
  barFill: {
    width: '100%',
    borderRadius: 6,
  },
  barLabel: {
    color: theme.colors.text.muted,
    fontSize: 10,
    fontWeight: 'bold',
  },
  barLabelToday: {
    color: theme.colors.text.primary,
  },

  achievementsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  achievementBadge: {
    width: '30%',
    alignItems: 'center',
  },
  achievementLocked: {
    opacity: 0.4,
  },
  achievementIconBg: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: `${theme.colors.primary.DEFAULT}15`,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
    borderWidth: 1,
    borderColor: `${theme.colors.primary.DEFAULT}40`,
  },
  iconBgLocked: {
    backgroundColor: theme.colors.background.elevated,
    borderColor: theme.colors.border.subtle,
  },
  achievementTitle: {
    color: theme.colors.text.secondary,
    fontSize: 11,
    textAlign: 'center',
    fontWeight: theme.typography.weight.semibold,
  }
});
