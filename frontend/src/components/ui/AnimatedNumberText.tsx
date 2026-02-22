import React, { useEffect, useState } from 'react';
import { StyleSheet, Text } from 'react-native';

interface AnimatedNumberTextProps {
  value: number;
  style?: any;
  duration?: number;
}

export const AnimatedNumberText: React.FC<AnimatedNumberTextProps> = ({ value, style, duration = 1500 }) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let startTimestamp: number | null = null;
    const startValue = displayValue;
    const difference = value - startValue;

    if (difference === 0) {
      setDisplayValue(value);
      return;
    }

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      
      const easeProgress = 1 - Math.pow(1 - progress, 4);
      setDisplayValue(Math.round(startValue + difference * easeProgress));

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    };

    const animationId = requestAnimationFrame(step);
    return () => cancelAnimationFrame(animationId);
  }, [value, duration]);

  return <Text style={[styles.text, style]}>{displayValue}</Text>;
};

const styles = StyleSheet.create({
  text: {
    color: '#fff',
    padding: 0,
    margin: 0,
  }
});
