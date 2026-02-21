import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring,
  withTiming
} from 'react-native-reanimated';
import { theme } from '../../theme';

interface ProgressBarProps {
  progress: number; // 0 to 100
  label?: string;
  showPercentage?: boolean;
  colorStart?: string;
  colorEnd?: string;
  height?: number;
  containerStyle?: ViewStyle;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  label,
  showPercentage = true,
  colorStart = theme.colors.primary.light,
  colorEnd = theme.colors.primary.DEFAULT,
  height = 8,
  containerStyle
}) => {
  const animatedWidth = useSharedValue(0);

  useEffect(() => {
    animatedWidth.value = withSpring(progress, {
      damping: 15,
      stiffness: 90
    });
  }, [progress]);

  const progressStyle = useAnimatedStyle(() => {
    return {
      width: `${animatedWidth.value}%`
    };
  });

  return (
    <View style={[styles.container, containerStyle]}>
      {(label || showPercentage) && (
        <View style={styles.header}>
          {label && <Text style={styles.label}>{label}</Text>}
          {showPercentage && <Text style={styles.percentage}>{Math.round(progress)}%</Text>}
        </View>
      )}
      
      <View style={[styles.track, { height, borderRadius: height / 2 }]}>
        <Animated.View style={[styles.fill, progressStyle]}>
          <LinearGradient
            colors={[colorStart, colorEnd]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={[StyleSheet.absoluteFill, { borderRadius: height / 2 }]}
          />
        </Animated.View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  label: {
    fontSize: theme.typography.size.caption,
    fontWeight: theme.typography.weight.semibold,
    color: theme.colors.text.secondary,
  },
  percentage: {
    fontSize: theme.typography.size.caption,
    color: theme.colors.text.primary,
    fontWeight: theme.typography.weight.bold,
  },
  track: {
    backgroundColor: theme.colors.background.elevated,
    width: '100%',
    overflow: 'hidden',
    borderColor: theme.colors.border.subtle,
    borderWidth: 1,
  },
  fill: {
    height: '100%',
    backgroundColor: theme.colors.primary.DEFAULT,
  }
});
