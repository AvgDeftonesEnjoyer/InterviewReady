import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { HomeScreen } from '../screens/HomeScreen';
import { LearningScreen } from '../features/learning/LearningScreen';
import { InterviewScreen } from '../features/interview/InterviewScreen';
import { AIPracticeScreen } from '../features/ai/AIPracticeScreen';
import { ProgressScreen } from '../features/progress/ProgressScreen';
import { SubscriptionScreen } from '../features/subscription/SubscriptionScreen'; // Adding Sub as Profile stand-in for now
import CustomTabBar from '../components/navigation/CustomTabBar';

const Tab = createBottomTabNavigator();

export const MainTabs = () => {
  return (
    <Tab.Navigator
      tabBar={props => <CustomTabBar {...props} />}
      screenOptions={{
        headerShown: false,
      }}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Learning" component={LearningScreen} />
      <Tab.Screen name="Interview" component={InterviewScreen} />
      <Tab.Screen name="AI" component={AIPracticeScreen} />
      <Tab.Screen name="Progress" component={ProgressScreen} />
      <Tab.Screen name="PRO" component={SubscriptionScreen} />
    </Tab.Navigator>
  );
};
