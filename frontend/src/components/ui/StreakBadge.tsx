import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { theme } from '../../theme';
import { Flame } from 'lucide-react-native';

interface StreakBadgeProps {
  count: number;
  containerStyle?: ViewStyle;
}

export const StreakBadge: React.FC<StreakBadgeProps> = ({ count, containerStyle }) => {
  const isActive = count > 0;
  
  return (
    <View style={[
      styles.container, 
      isActive && styles.activeContainer,
      containerStyle
    ]}>
      <Flame 
        size={16} 
        color={isActive ? theme.colors.status.warning : theme.colors.text.muted} 
        fill={isActive ? theme.colors.status.warning : 'transparent'}
      />
      <Text style={[
        styles.text, 
        isActive && styles.activeText
      ]}>
        {count} {count === 1 ? 'Day' : 'Days'}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 20,
    backgroundColor: theme.colors.background.card,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
    gap: 6,
  },
  activeContainer: {
    backgroundColor: 'rgba(245, 158, 11, 0.1)', // Subtle orange tint
    borderColor: 'rgba(245, 158, 11, 0.3)',
  },
  text: {
    fontSize: theme.typography.size.body,
    fontWeight: theme.typography.weight.semibold,
    color: theme.colors.text.muted,
  },
  activeText: {
    color: theme.colors.status.warning,
  }
});
