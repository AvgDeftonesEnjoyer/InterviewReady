import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';
import { theme } from '../../theme';

interface SkeletonBoxProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: any;
}

/**
 * Skeleton Box Component
 * Placeholder for content that is loading
 */
export const SkeletonBox: React.FC<SkeletonBoxProps> = ({
  width = '100%',
  height = 20,
  borderRadius = 8,
  style,
}) => {
  const animatedValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(animatedValue, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(animatedValue, {
          toValue: 0,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    );
    animation.start();

    return () => animation.stop();
  }, [animatedValue]);

  const opacity = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: [0.3, 0.6],
  });

  return (
    <Animated.View
      style={[
        styles.skeleton,
        { width, height, borderRadius },
        { opacity },
        style,
      ]}
    />
  );
};

/**
 * Skeleton Text Component
 * Placeholder for text content
 */
export const SkeletonText: React.FC<{
  lines?: number;
  width?: string | number;
  height?: number;
}> = ({ lines = 1, width = '100%', height = 16 }) => {
  return (
    <View style={styles.textContainer}>
      {Array.from({ length: lines }).map((_, index) => (
        <SkeletonBox
          key={index}
          height={height}
          width={index === lines - 1 ? '60%' : width}
          style={index > 0 && styles.textLine}
        />
      ))}
    </View>
  );
};

/**
 * Skeleton Card Component
 * Placeholder for card content
 */
export const SkeletonCard: React.FC = () => {
  return (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <SkeletonBox width={40} height={40} borderRadius={20} />
        <View style={styles.cardHeaderText}>
          <SkeletonBox width={120} height={16} />
          <SkeletonBox width={80} height={12} style={styles.cardHeaderSubtext} />
        </View>
      </View>
      <SkeletonBox width="100%" height={100} style={styles.cardContent} />
      <View style={styles.cardFooter}>
        <SkeletonBox width={60} height={24} borderRadius={12} />
        <SkeletonBox width={60} height={24} borderRadius={12} />
      </View>
    </View>
  );
};

/**
 * Skeleton Dashboard Component
 * Full dashboard loading placeholder
 */
export const SkeletonDashboard: React.FC = () => {
  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <SkeletonBox width={150} height={32} />
        <SkeletonBox width={100} height={40} />
      </View>

      {/* Hero Card */}
      <SkeletonCard />

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <SkeletonCard />
        <SkeletonCard />
      </View>

      {/* Daily Challenges */}
      <View style={styles.challenges}>
        <SkeletonBox width={150} height={24} style={styles.sectionTitle} />
        <SkeletonCard />
        <SkeletonCard />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    paddingTop: 60,
  },
  skeleton: {
    backgroundColor: theme.colors.background.card,
  },
  textContainer: {
    width: '100%',
  },
  textLine: {
    marginTop: 8,
  },
  card: {
    backgroundColor: theme.colors.background.card,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardHeaderText: {
    marginLeft: 12,
    flex: 1,
  },
  cardHeaderSubtext: {
    marginTop: 4,
  },
  cardContent: {
    marginBottom: 12,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  statsGrid: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  challenges: {
    marginTop: 8,
  },
  sectionTitle: {
    marginBottom: 12,
  },
});

export default SkeletonBox;
