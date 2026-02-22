import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../theme';
import { LucideIcon } from 'lucide-react-native';
import { AnimatedNumberText } from './AnimatedNumberText';

interface StatCardProps {
  icon: LucideIcon;
  number: number;
  label: string;
  trend?: 'up' | 'down' | 'neutral';
  trendLabel?: string;
  caption?: string;
  color?: string;
  animate?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({ 
  icon: Icon, 
  number, 
  label, 
  trendLabel,
  caption,
  color = theme.colors.primary.DEFAULT,
  animate = false
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={[styles.iconWrapper, { backgroundColor: `${color}15` }]}>
          <Icon size={20} color={color} />
        </View>
        {trendLabel && (
          <View style={styles.trendWrapper}>
            <Text style={styles.trendText}>{trendLabel}</Text>
          </View>
        )}
      </View>
      
      <View>
        {animate ? (
          <AnimatedNumberText value={number} style={styles.number} />
        ) : (
          <Text style={styles.number}>{number}</Text>
        )}
        <Text style={styles.label}>{label}</Text>
        {caption && <Text style={styles.caption}>{caption}</Text>}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.background.card,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
    flex: 1,
    minHeight: 120,
    justifyContent: 'space-between',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  iconWrapper: {
    padding: 8,
    borderRadius: 10,
  },
  trendWrapper: {
    backgroundColor: 'rgba(34, 197, 94, 0.15)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  trendText: {
    color: '#22c55e',
    fontSize: 10,
    fontWeight: 'bold',
  },
  number: {
    fontSize: theme.typography.size.h2,
    fontWeight: theme.typography.weight.bold,
    color: theme.colors.text.primary,
    marginBottom: 2,
  },
  label: {
    fontSize: theme.typography.size.caption,
    color: theme.colors.text.secondary,
  },
  caption: {
    fontSize: 10,
    color: theme.colors.text.muted,
    marginTop: 4,
  }
});
