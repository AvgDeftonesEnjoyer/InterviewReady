import React, { useEffect } from 'react';
import { StyleSheet, TextInput } from 'react-native';
import Animated, { useAnimatedProps, useSharedValue, withTiming } from 'react-native-reanimated';

const AnimatedTextInput = Animated.createAnimatedComponent(TextInput);

interface AnimatedNumberTextProps {
  value: number;
  style?: any;
  duration?: number;
}

export const AnimatedNumberText: React.FC<AnimatedNumberTextProps> = ({ value, style, duration = 1500 }) => {
  const animatedValue = useSharedValue(0);

  useEffect(() => {
    animatedValue.value = withTiming(value, { duration });
  }, [value]);

  const animatedProps = useAnimatedProps(() => {
    return {
      text: Math.round(animatedValue.value).toString(),
      value: Math.round(animatedValue.value).toString(),
    };
  });

  return (
    <AnimatedTextInput
      underlineColorAndroid="transparent"
      editable={false}
      animatedProps={animatedProps}
      style={[styles.text, style]}
    />
  );
};

const styles = StyleSheet.create({
  text: {
    color: '#fff',
    padding: 0,
    margin: 0,
  }
});
