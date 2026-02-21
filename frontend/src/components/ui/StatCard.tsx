import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../theme';
import { LucideIcon } from 'lucide-react-native';

interface StatCardProps {
  icon: LucideIcon;
  number: string | number;
  label: string;
  trend?: 'up' | 'down' | 'neutral';
  color?: string;
}

export const StatCard: React.FC<StatCardProps> = ({ 
  icon: Icon, 
  number, 
  label, 
  trend,
  color = theme.colors.primary.DEFAULT 
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={[styles.iconWrapper, { backgroundColor: `${color}15` }]}>
          <Icon size={20} color={color} />
        </View>
        {trend && (
          <View style={styles.trendWrapper}>
            {/* Trend arrows can go here */}
          </View>
        )}
      </View>
      
      <Text style={styles.number}>{number}</Text>
      <Text style={styles.label}>{label}</Text>
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
    minHeight: 110,
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
  trendWrapper: {},
  number: {
    fontSize: theme.typography.size.h2,
    fontWeight: theme.typography.weight.bold,
    color: theme.colors.text.primary,
    marginBottom: 4,
  },
  label: {
    fontSize: theme.typography.size.caption,
    color: theme.colors.text.secondary,
  }
});
