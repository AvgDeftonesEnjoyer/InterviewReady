import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View } from 'react-native';
import { theme } from '../../theme';

interface QuickActionBtnProps {
  icon: React.ReactNode;
  label: string;
  onPress: () => void;
  color?: string;
  style?: any;
}

export const QuickActionBtn: React.FC<QuickActionBtnProps> = ({ icon, label, onPress, color, style }) => {
  return (
    <TouchableOpacity 
      style={[styles.container, style]} 
      onPress={onPress}
      activeOpacity={0.8}
    >
      <View style={[styles.iconContainer, color ? { backgroundColor: `${color}15` } : null]}>
        {icon}
      </View>
      <Text style={styles.label}>{label}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'rgba(30, 32, 53, 0.6)', // Glassmorphism background
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  label: {
    color: theme.colors.text.primary,
    fontSize: 13,
    fontWeight: theme.typography.weight.semibold,
    textAlign: 'center',
  }
});
