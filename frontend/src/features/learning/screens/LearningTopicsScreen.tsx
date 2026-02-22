import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Animated, { FadeInDown, useAnimatedStyle, useSharedValue, withTiming } from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import { theme } from '../../../theme';
import { useTopics } from '../hooks';
import { CheckCircle2 } from 'lucide-react-native';

export const LearningTopicsScreen = ({ navigation, route }: any) => {
  const insets = useSafeAreaInsets();
  const { data: topics, isLoading, isError, refetch } = useTopics();

  useEffect(() => {
    // If navigated from Home "NEXT UP" with a specific topic_id
    if (route.params?.topic_id) {
      navigation.navigate('LearningSession', { topic_id: route.params.topic_id });
    }
  }, [route.params]);

  const startTopic = (topic: any) => {
    navigation.navigate('LearningSession', { topic_id: topic.id, title: topic.name });
  };

  if (isLoading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color={theme.colors.primary.DEFAULT} />
      </View>
    );
  }

  if (isError || !topics) {
    return (
      <View style={[styles.container, styles.centered]}>
        <Text style={styles.errorText}>Failed to load topics</Text>
        <TouchableOpacity style={styles.retryButton} onPress={() => refetch()}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (topics.length === 0) {
      return (
        <View style={[styles.container, styles.centered]}>
            <Text style={styles.emptyIcon}>📭</Text>
            <Text style={styles.emptyTitle}>No topics yet</Text>
            <Text style={styles.emptySubtitle}>We will add more content soon.</Text>
            <TouchableOpacity style={styles.tryAiButton} onPress={() => navigation.navigate('AI')}>
                <Text style={styles.tryAiButtonText}>Try AI Interview instead →</Text>
            </TouchableOpacity>
        </View>
      );
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>Explore Topics</Text>
          <Text style={styles.subtitle}>Choose a subject to practice</Text>
        </View>

        <View style={styles.list}>
          {topics.map((topic, index) => {
            const isCompleted = topic.is_completed;
            
            return (
              <Animated.View key={topic.id} entering={FadeInDown.delay(index * 80).springify()}>
                <TouchableOpacity
                  activeOpacity={0.8}
                  onPress={() => startTopic(topic)}
                  style={[styles.card, isCompleted && styles.cardCompleted]}
                >
                  <View style={styles.cardContent}>
                    {/* Left Icon */}
                    <View style={styles.iconCircle}>
                      <Text style={styles.iconText}>{topic.icon}</Text>
                    </View>

                    {/* Middle Info */}
                    <View style={styles.infoContainer}>
                      <Text style={styles.topicName}>{topic.name}</Text>
                      <Text style={styles.countText}>
                        {topic.completed_questions}/{topic.total_questions} questions
                      </Text>

                      {/* Progress Bar */}
                      <View style={styles.progressBg}>
                        <LinearGradient
                          colors={['#6C63FF', '#818CF8']}
                          start={{ x: 0, y: 0 }}
                          end={{ x: 1, y: 0 }}
                          style={[styles.progressFill, { width: `${topic.progress_percent}%` }]}
                        />
                      </View>
                    </View>

                    {/* Right Badge */}
                    <View style={styles.rightSection}>
                      {isCompleted ? (
                        <CheckCircle2 color={theme.colors.status.success} size={24} />
                      ) : (
                        <Text style={styles.percentText}>{topic.progress_percent}%</Text>
                      )}
                    </View>
                  </View>
                </TouchableOpacity>
              </Animated.View>
            );
          })}
        </View>
        <View style={{ height: 100 }} />
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  header: {
    marginBottom: 32,
  },
  title: {
    fontSize: 32,
    fontWeight: theme.typography.weight.bold,
    color: theme.colors.text.primary,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.text.secondary,
  },
  list: {
    gap: 16,
  },
  card: {
    backgroundColor: theme.colors.background.card,
    borderRadius: 20,
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  cardCompleted: {
    borderColor: 'rgba(34,197,94,0.3)',
    backgroundColor: 'rgba(34,197,94,0.05)',
  },
  cardContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(108,99,255,0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  iconText: {
    fontSize: 24,
  },
  infoContainer: {
    flex: 1,
  },
  topicName: {
    color: theme.colors.text.primary,
    fontSize: 18,
    fontWeight: theme.typography.weight.semibold,
    marginBottom: 4,
  },
  countText: {
    color: theme.colors.text.secondary,
    fontSize: 13,
    marginBottom: 10,
  },
  progressBg: {
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 3,
    overflow: 'hidden',
    width: '90%',
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  rightSection: {
    alignItems: 'flex-end',
    justifyContent: 'center',
    width: 40,
  },
  percentText: {
    color: theme.colors.primary.light,
    fontSize: 16,
    fontWeight: theme.typography.weight.bold,
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
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  retryButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  emptyIcon: {
      fontSize: 48,
      marginBottom: 16,
  },
  emptyTitle: {
      fontSize: 24,
      fontWeight: 'bold',
      color: theme.colors.text.primary,
      marginBottom: 8,
  },
  emptySubtitle: {
      fontSize: 16,
      color: theme.colors.text.secondary,
      textAlign: 'center',
      marginBottom: 32,
  },
  tryAiButton: {
      backgroundColor: theme.colors.primary.DEFAULT,
      paddingHorizontal: 24,
      paddingVertical: 14,
      borderRadius: 12,
  },
  tryAiButtonText: {
      color: theme.colors.text.primary,
      fontWeight: 'bold',
      fontSize: 16,
  }
});
