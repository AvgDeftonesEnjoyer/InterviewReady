import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore } from '../store/useAuthStore';
import { AuthStack } from './AuthStack';
import { MainTabs } from './MainTabs';
import { OnboardingScreen } from '../screens/OnboardingScreen';
import { LearningSessionScreen } from '../features/learning/screens/LearningSessionScreen';
import { SettingsScreen } from '../screens/SettingsScreen';
import { SubscriptionScreen } from '../screens/SubscriptionScreen';
import * as Linking from 'expo-linking';
import { initRevenueCat } from '../utils/revenuecat';

const Stack = createNativeStackNavigator();

const AppStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="MainTabs" component={MainTabs} />
    <Stack.Screen name="LearningSession" component={LearningSessionScreen} />
    <Stack.Screen name="Settings" component={SettingsScreen} />
    <Stack.Screen
      name="Subscription"
      component={SubscriptionScreen}
      options={{ presentation: 'modal' }}
    />
  </Stack.Navigator>
);

const OnboardingStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Onboarding" component={OnboardingScreen} />
  </Stack.Navigator>
);

// Deep linking configuration for Stripe redirect
const linking = {
  prefixes: ['interviewready://'],
  config: {
    screens: {
      'SubscriptionSuccess': 'subscription/success',
      'SubscriptionCancel': 'subscription/cancel',
    }
  }
};

export const RootNavigator = () => {
  const { isAuthenticated, user, onboardingCompleted } = useAuthStore();

  // Initialize RevenueCat after user logs in
  useEffect(() => {
    if (isAuthenticated && user?.id) {
      initRevenueCat(String(user.id)).catch((err) => {
        console.error('Failed to initialize RevenueCat:', err);
      });
    }
  }, [isAuthenticated, user?.id]);

  return (
    <NavigationContainer linking={linking}>
      {!isAuthenticated && <AuthStack />}
      {isAuthenticated && !onboardingCompleted && <OnboardingStack />}
      {isAuthenticated && onboardingCompleted && <AppStack />}
    </NavigationContainer>
  );
};
