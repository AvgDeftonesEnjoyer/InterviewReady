import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../theme';
import { Star } from 'lucide-react-native';

interface XPBadgeProps {
  xp: number;
  level: number;
}

export const XPBadge: React.FC<XPBadgeProps> = ({ xp, level }) => {
  return (
    <View style={styles.container}>
      <View style={styles.iconContainer}>
        <Star size={16} color={theme.colors.status.warning} fill={theme.colors.status.warning} />
      </View>
      <View style={styles.textContainer}>
        <Text style={styles.xpText}>{xp} XP</Text>
        <Text style={styles.levelText}>Lvl {level}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.background.card,
    borderRadius: 16,
    padding: 6,
    paddingRight: 16,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  iconContainer: {
    backgroundColor: 'rgba(245, 158, 11, 0.15)',
    padding: 8,
    borderRadius: 12,
    marginRight: 12,
  },
  textContainer: {
    justifyContent: 'center',
  },
  xpText: {
    color: theme.colors.text.primary,
    fontSize: theme.typography.size.body,
    fontWeight: theme.typography.weight.bold,
    lineHeight: 18,
  },
  levelText: {
    color: theme.colors.text.secondary,
    fontSize: theme.typography.size.caption,
    fontWeight: theme.typography.weight.medium,
  }
});
