import React, { useEffect, forwardRef, useImperativeHandle } from 'react';
import { TextInput, TextInputProps, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSequence,
  withTiming,
  withRepeat,
} from 'react-native-reanimated';

const AnimatedTextInput = Animated.createAnimatedComponent(TextInput);

export interface AnimatedInputProps extends TextInputProps {
  error?: boolean;
}

export interface AnimatedInputRef {
  shake: () => void;
  focus: () => void;
  blur: () => void;
}

export const AnimatedInput = forwardRef<AnimatedInputRef, AnimatedInputProps>(
  ({ error, style, ...props }, ref) => {
    const shakeX = useSharedValue(0);
    const inputRef = React.useRef<TextInput>(null);

    const triggerShake = () => {
      shakeX.value = withSequence(
        withTiming(-10, { duration: 50 }),
        withRepeat(withTiming(10, { duration: 100 }), 3, true),
        withTiming(0, { duration: 50 })
      );
    };

    useImperativeHandle(ref, () => ({
      shake: triggerShake,
      focus: () => inputRef.current?.focus(),
      blur: () => inputRef.current?.blur(),
    }));

    // Optionally shake automatically when error prop changes from false to true
    useEffect(() => {
      if (error) {
        triggerShake();
      }
    }, [error]);

    const animatedStyle = useAnimatedStyle(() => {
      return {
        transform: [{ translateX: shakeX.value }],
      };
    });

    return (
      <AnimatedTextInput
        ref={inputRef}
        style={[style, animatedStyle]}
        {...props}
      />
    );
  }
);
