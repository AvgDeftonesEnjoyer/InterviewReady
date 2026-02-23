import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { theme } from '../theme';
import { ArrowLeft } from 'lucide-react-native';

export const SettingsScreen = ({ navigation }: any) => {
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <ArrowLeft color={theme.colors.text.primary} size={24} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Advanced Settings</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.sectionTitle}>Notifications</Text>
        <View style={styles.card}>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Daily Reminder</Text>
            <Text style={styles.comingSoon}>Coming soon</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Streak Alerts</Text>
            <Text style={styles.comingSoon}>Coming soon</Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>Privacy</Text>
        <View style={styles.card}>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Analytics</Text>
            <Text style={styles.comingSoon}>Coming soon</Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.card}>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Version</Text>
            <Text style={styles.valueText}>1.0.0</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Terms of Service</Text>
            <Text style={styles.comingSoon}>→</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Privacy Policy</Text>
            <Text style={styles.comingSoon}>→</Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.subtle,
  },
  backBtn: {
    padding: 8,
    marginLeft: -8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
  },
  content: {
    padding: 20,
    paddingBottom: 60,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: theme.colors.text.muted,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginTop: 24,
    marginBottom: 10,
    marginLeft: 4,
  },
  card: {
    backgroundColor: theme.colors.background.card,
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 18,
  },
  rowLabel: {
    fontSize: 16,
    color: theme.colors.text.primary,
  },
  valueText: {
    fontSize: 14,
    color: theme.colors.text.secondary,
  },
  comingSoon: {
    fontSize: 13,
    color: theme.colors.text.muted,
    fontStyle: 'italic',
  },
  divider: {
    height: 1,
    backgroundColor: theme.colors.border.subtle,
    marginLeft: 18,
  },
});
