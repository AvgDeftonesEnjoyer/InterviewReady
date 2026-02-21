import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { Home, BookOpen, MessageSquare, Compass, Award, Star } from 'lucide-react-native';
import { theme } from '../../theme';
import Animated, { useAnimatedStyle, withSpring } from 'react-native-reanimated';

export default function CustomTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  return (
    <View style={styles.tabBar}>
      {state.routes.map((route, index) => {
        const { options } = descriptors[route.key];
        const label =
          options.tabBarLabel !== undefined
            ? options.tabBarLabel
            : options.title !== undefined
            ? options.title
            : route.name;

        const isFocused = state.index === index;

        const onPress = () => {
          const event = navigation.emit({
            type: 'tabPress',
            target: route.key,
            canPreventDefault: true,
          });

          if (!isFocused && !event.defaultPrevented) {
            navigation.navigate(route.name, route.params);
          }
        };

        const onLongPress = () => {
          navigation.emit({
            type: 'tabLongPress',
            target: route.key,
          });
        };

        // Select correct icon based on route
        let IconComponent = Home;
        if (route.name === 'Learning') IconComponent = BookOpen;
        else if (route.name === 'Interview') IconComponent = MessageSquare;
        else if (route.name === 'AI') IconComponent = Compass;
        else if (route.name === 'Progress') IconComponent = Award;
        else if (route.name === 'PRO') IconComponent = Star;

        return (
          <TouchableOpacity
            key={index}
            accessibilityRole="button"
            accessibilityState={isFocused ? { selected: true } : {}}
            accessibilityLabel={options.tabBarAccessibilityLabel}
            testID={options.tabBarTestID}
            onPress={onPress}
            onLongPress={onLongPress}
            style={styles.tabItem}
          >
            <View style={styles.iconContainer}>
              {isFocused && (
                <View style={styles.glowIndicator} />
              )}
              <IconComponent 
                size={22} 
                color={isFocused ? (route.name === 'PRO' ? theme.colors.status.warning : theme.colors.primary.DEFAULT) : theme.colors.text.muted} 
                strokeWidth={isFocused ? 2.5 : 2}
              />
              <Text 
                style={[
                  styles.tabLabel, 
                  isFocused && styles.tabLabelFocused,
                  isFocused && route.name === 'PRO' && { color: theme.colors.status.warning }
                ]}
              >
                {label as string}
              </Text>
            </View>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    flexDirection: 'row',
    height: 80, // Taller for iOS styles
    backgroundColor: theme.colors.background.modal,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.subtle,
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingBottom: 20, // SafeArea substitute
    paddingTop: 10,
    elevation: 8,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    height: '100%',
  },
  tabLabel: {
    fontSize: 10,
    marginTop: 4,
    color: theme.colors.text.muted,
    fontWeight: theme.typography.weight.medium,
  },
  tabLabelFocused: {
    color: theme.colors.primary.DEFAULT,
    fontWeight: theme.typography.weight.bold,
  },
  glowIndicator: {
    position: 'absolute',
    top: -12,
    width: 24,
    height: 4,
    borderRadius: 2,
    backgroundColor: theme.colors.primary.DEFAULT,
    shadowColor: theme.colors.primary.DEFAULT,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.8,
    shadowRadius: 8,
    elevation: 10,
  }
});
