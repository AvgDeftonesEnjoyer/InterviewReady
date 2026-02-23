import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { Home, BookOpen, Cpu, User } from 'lucide-react-native';
import { theme } from '../../theme';

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

        let IconComponent: any = Home;
        if (route.name === 'Learning') IconComponent = BookOpen;
        else if (route.name === 'AI') IconComponent = Cpu;
        else if (route.name === 'Profile') IconComponent = User;

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
              {isFocused && <View style={styles.glowIndicator} />}
              <IconComponent
                size={22}
                color={isFocused ? theme.colors.primary.DEFAULT : theme.colors.text.muted}
                strokeWidth={isFocused ? 2.5 : 2}
              />
              <Text style={[styles.tabLabel, isFocused && styles.tabLabelFocused]}>
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
    height: 80,
    backgroundColor: theme.colors.background.modal,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.subtle,
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingBottom: 20,
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
  },
  tabLabelFocused: {
    color: theme.colors.primary.DEFAULT,
    fontWeight: 'bold',
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
  },
});
