import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { HomeScreen } from '../screens/HomeScreen';
import { LearningTopicsScreen } from '../features/learning/screens/LearningTopicsScreen';
import { AIPracticeScreen } from '../features/ai/AIPracticeScreen';
import { ProfileScreen } from '../screens/ProfileScreen';
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
      <Tab.Screen name="Learning" component={LearningTopicsScreen} />
      <Tab.Screen name="AI" component={AIPracticeScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
};
