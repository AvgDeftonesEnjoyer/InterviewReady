import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { theme } from '../../theme';
import { ChevronRight, Clock, BookOpen } from 'lucide-react-native';

interface QuestionCardProps {
  title: string;
  category: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  durationMins: number;
  onPress: () => void;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  title,
  category,
  difficulty,
  durationMins,
  onPress
}) => {

  const getDifficultyColor = () => {
    switch (difficulty) {
      case 'Easy': return theme.colors.status.success;
      case 'Medium': return theme.colors.status.warning;
      case 'Hard': return theme.colors.status.error;
    }
  };

  const diffColor = getDifficultyColor();

  return (
    <Pressable 
      style={({ pressed }) => [
        styles.container,
        pressed && styles.pressed
      ]}
      onPress={onPress}
    >
      <View style={styles.content}>
        <View style={styles.headerRow}>
          <View style={styles.chipRow}>
            <View style={styles.categoryChip}>
              <BookOpen size={12} color={theme.colors.primary.light} style={{ marginRight: 4 }} />
              <Text style={styles.categoryText}>{category}</Text>
            </View>
            <View style={[styles.difficultyChip, { backgroundColor: `${diffColor}15`, borderColor: `${diffColor}30` }]}>
              <View style={[styles.dot, { backgroundColor: diffColor }]} />
              <Text style={[styles.difficultyText, { color: diffColor }]}>{difficulty}</Text>
            </View>
          </View>
        </View>
        
        <Text style={styles.title} numberOfLines={2}>{title}</Text>
        
        <View style={styles.footerRow}>
          <View style={styles.timeWrapper}>
            <Clock size={14} color={theme.colors.text.muted} />
            <Text style={styles.timeText}>{durationMins} min</Text>
          </View>
        </View>
      </View>
      
      <View style={styles.chevronWrapper}>
        <ChevronRight size={20} color={theme.colors.text.secondary} />
      </View>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.background.card,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    marginBottom: 12,
  },
  pressed: {
    opacity: 0.8,
    backgroundColor: theme.colors.background.elevated,
    transform: [{ scale: 0.98 }]
  },
  content: {
    flex: 1,
    paddingRight: 16,
  },
  headerRow: {
    marginBottom: 8,
  },
  chipRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 8,
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: `${theme.colors.primary.DEFAULT}15`,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  categoryText: {
    color: theme.colors.primary.light,
    fontSize: 12,
    fontWeight: theme.typography.weight.semibold,
  },
  difficultyChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    borderWidth: 1,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 6,
  },
  difficultyText: {
    fontSize: 12,
    fontWeight: theme.typography.weight.semibold,
  },
  title: {
    fontSize: 17,
    fontWeight: theme.typography.weight.semibold,
    color: theme.colors.text.primary,
    marginBottom: 12,
    lineHeight: 22,
  },
  footerRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  timeWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  timeText: {
    color: theme.colors.text.secondary,
    fontSize: theme.typography.size.caption,
  },
  chevronWrapper: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.colors.background.elevated,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  }
});
