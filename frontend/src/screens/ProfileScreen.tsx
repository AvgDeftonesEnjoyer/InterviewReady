import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Modal,
  ActivityIndicator,
  Alert,
  SafeAreaView,
} from 'react-native';
import { User, LogOut, ChevronRight, Code, Briefcase, Zap, Settings, Star } from 'lucide-react-native';
import { useNavigation } from '@react-navigation/native';
import { useAuthStore } from '../store/useAuthStore';
import { apiClient } from '../api/client';
import { storage } from '../utils/storage';
import { theme } from '../theme';
import { useTranslation } from 'react-i18next';
import { changeLanguage } from '../i18n';

const LANGUAGES = [
  { id: 'python', label: '🐍 Python' },
  { id: 'javascript', label: '🟨 JavaScript' },
  { id: 'java', label: '☕ Java' },
  { id: 'go', label: '🔵 Go' },
  { id: 'csharp', label: '🟣 C#' },
];

const SPECIALIZATIONS = [
  { id: 'backend', label: '⚙️ Backend' },
  { id: 'frontend', label: '🎨 Frontend' },
  { id: 'fullstack', label: '🔄 Fullstack' },
  { id: 'data', label: '📊 Data Science' },
  { id: 'ml', label: '🤖 ML/AI' },
];

const EXPERIENCE_LEVELS = [
  { id: 'junior', label: '🌱 Junior' },
  { id: 'middle', label: '🚀 Middle' },
  { id: 'senior', label: '⭐ Senior' },
];

interface ProfileData {
  username: string;
  email: string;
  primary_language: string | null;
  specialization: string | null;
  experience_level: string | null;
  ui_language: string;
  total_xp: number;
  current_level: number;
}

type PickerField = 'primary_language' | 'specialization' | 'experience_level' | null;

export const ProfileScreen = () => {
  const navigation = useNavigation<any>();
  const { logout } = useAuthStore();
  const { i18n } = useTranslation();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [pickerField, setPickerField] = useState<PickerField>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await apiClient.get('/auth/me/');
      setProfile(res.data);
    } catch (e) {
      console.error('Failed to load profile', e);
    } finally {
      setLoading(false);
    }
  };

  const updateField = async (field: string, value: string) => {
    if (!profile) return;
    setSaving(true);
    try {
      await apiClient.patch('/auth/me/', { [field]: value });
      setProfile(prev => prev ? { ...prev, [field]: value } : prev);

      // If changing UI language, update i18n
      if (field === 'ui_language') {
        await changeLanguage(value as 'en' | 'uk');
      }
    } catch (e) {
      Alert.alert('Error', 'Failed to save. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Log Out',
      'Are you sure you want to log out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Log Out',
          style: 'destructive',
          onPress: async () => {
            await storage.clearTokens();
            logout();
          },
        },
      ]
    );
  };

  const getPickerOptions = () => {
    if (pickerField === 'primary_language') return LANGUAGES;
    if (pickerField === 'specialization') return SPECIALIZATIONS;
    if (pickerField === 'experience_level') return EXPERIENCE_LEVELS;
    return [];
  };

  const getDisplayLabel = (field: string, value: string | null) => {
    if (!value) return 'Not set';
    const list = field === 'primary_language' ? LANGUAGES :
                 field === 'specialization' ? SPECIALIZATIONS :
                 EXPERIENCE_LEVELS;
    return list.find(i => i.id === value)?.label || value;
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={theme.colors.primary.DEFAULT} />
      </View>
    );
  }

  const initials = profile?.username
    ? profile.username.slice(0, 2).toUpperCase()
    : profile?.email?.slice(0, 2).toUpperCase() || '??';

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>

        {/* Header */}
        <View style={styles.header}>
          <View style={styles.avatarContainer}>
            <Text style={styles.avatarText}>{initials}</Text>
          </View>
          <Text style={styles.username}>{profile?.username || 'User'}</Text>
          <Text style={styles.email}>{profile?.email}</Text>
          <View style={styles.levelBadge}>
            <Zap size={12} color={theme.colors.status.warning} />
            <Text style={styles.levelText}>Level {profile?.current_level} · {profile?.total_xp} XP</Text>
          </View>
        </View>

        {/* Learning Profile */}
        <Text style={styles.sectionTitle}>Learning Profile</Text>
        <View style={styles.card}>
          <SettingRow
            icon={<Code size={18} color={theme.colors.primary.DEFAULT} />}
            label="Primary Language"
            value={getDisplayLabel('primary_language', profile?.primary_language ?? null)}
            onPress={() => setPickerField('primary_language')}
          />
          <View style={styles.divider} />
          <SettingRow
            icon={<Briefcase size={18} color={theme.colors.primary.DEFAULT} />}
            label="Specialization"
            value={getDisplayLabel('specialization', profile?.specialization ?? null)}
            onPress={() => setPickerField('specialization')}
          />
          <View style={styles.divider} />
          <SettingRow
            icon={<Zap size={18} color={theme.colors.primary.DEFAULT} />}
            label="Experience Level"
            value={getDisplayLabel('experience_level', profile?.experience_level ?? null)}
            onPress={() => setPickerField('experience_level')}
          />
        </View>

        {/* App Settings */}
        <Text style={styles.sectionTitle}>App Settings</Text>
        <View style={styles.card}>
          <SettingRow
            icon={<Settings size={18} color={theme.colors.primary.DEFAULT} />}
            label="Advanced Settings"
            value=""
            onPress={() => navigation.navigate('Settings')}
          />
        </View>

        {/* Subscription */}
        <Text style={styles.sectionTitle}>Subscription</Text>
        <TouchableOpacity
          onPress={() => navigation.navigate('Subscription')}
          style={[styles.card, styles.subscripRow]}
        >
          <View style={styles.proHeader}>
            <View style={styles.proIconWrap}>
              <Star size={20} color="#fbbf24" fill="#fbbf24" />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.proTitle}>Manage Subscription</Text>
              <Text style={styles.proSubtitle}>View plans and upgrade to PRO</Text>
            </View>
            <ChevronRight size={16} color={theme.colors.text.muted} />
          </View>
        </TouchableOpacity>

        {/* Danger Zone */}
        <Text style={styles.sectionTitle}>Account</Text>
        <View style={styles.card}>
          <TouchableOpacity style={styles.row} onPress={handleLogout}>
            <View style={styles.rowLeft}>
              <LogOut size={18} color={theme.colors.status.error} />
              <Text style={[styles.rowLabel, { color: theme.colors.status.error }]}>Log Out</Text>
            </View>
          </TouchableOpacity>
        </View>

        {saving && (
          <View style={styles.savingBanner}>
            <ActivityIndicator size="small" color="#fff" />
            <Text style={styles.savingText}>Saving...</Text>
          </View>
        )}
      </ScrollView>

      {/* Picker Modal */}
      <Modal visible={!!pickerField} transparent animationType="slide">
        <TouchableOpacity style={styles.modalOverlay} activeOpacity={1} onPress={() => setPickerField(null)} />
        <View style={styles.modalSheet}>
          <View style={styles.modalHandle} />
          <Text style={styles.modalTitle}>
            {pickerField === 'primary_language' ? 'Primary Language' :
             pickerField === 'specialization' ? 'Specialization' : 'Experience Level'}
          </Text>
          {getPickerOptions().map(opt => {
            const isSelected = profile?.[pickerField!] === opt.id;
            return (
              <TouchableOpacity
                key={opt.id}
                style={[styles.modalOption, isSelected && styles.modalOptionSelected]}
                onPress={() => {
                  if (pickerField) updateField(pickerField, opt.id);
                  setPickerField(null);
                }}
              >
                <Text style={[styles.modalOptionText, isSelected && styles.modalOptionTextSelected]}>
                  {opt.label}
                </Text>
                {isSelected && <Text style={styles.checkmark}>✓</Text>}
              </TouchableOpacity>
            );
          })}
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const SettingRow = ({ icon, label, value, onPress }: {
  icon: React.ReactNode;
  label: string;
  value: string;
  onPress: () => void;
}) => (
  <TouchableOpacity style={styles.row} onPress={onPress}>
    <View style={styles.rowLeft}>
      {icon}
      <Text style={styles.rowLabel}>{label}</Text>
    </View>
    <View style={styles.rowRight}>
      {value ? <Text style={styles.rowValue}>{value}</Text> : null}
      <ChevronRight size={16} color={theme.colors.text.muted} />
    </View>
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background.primary,
  },
  scroll: {
    padding: 20,
    paddingBottom: 100,
  },
  header: {
    alignItems: 'center',
    paddingVertical: 28,
    marginBottom: 8,
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: theme.colors.primary.DEFAULT,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: theme.colors.primary.DEFAULT,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 8,
  },
  avatarText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  username: {
    fontSize: 22,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 4,
  },
  email: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    marginBottom: 10,
  },
  levelBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,190,0,0.12)',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 20,
    gap: 6,
  },
  levelText: {
    color: theme.colors.status.warning,
    fontSize: 13,
    fontWeight: '600',
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
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  rowLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  rowRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  rowLabel: {
    fontSize: 16,
    color: theme.colors.text.primary,
  },
  rowValue: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    maxWidth: 150,
  },
  divider: {
    height: 1,
    backgroundColor: theme.colors.border.subtle,
    marginLeft: 16,
  },
  langToggle: {
    flexDirection: 'row',
    backgroundColor: theme.colors.background.primary,
    borderRadius: 10,
    overflow: 'hidden',
  },
  langBtn: {
    paddingHorizontal: 14,
    paddingVertical: 6,
  },
  langBtnActive: {
    backgroundColor: theme.colors.primary.DEFAULT,
    borderRadius: 8,
  },
  langBtnText: {
    color: theme.colors.text.muted,
    fontWeight: '600',
    fontSize: 13,
  },
  langBtnTextActive: {
    color: '#fff',
  },
  savingBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: theme.colors.primary.DEFAULT,
    padding: 12,
    borderRadius: 12,
    marginTop: 16,
    justifyContent: 'center',
  },
  savingText: {
    color: '#fff',
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  modalSheet: {
    backgroundColor: theme.colors.background.modal,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    paddingBottom: 40,
    minHeight: 200,
  },
  modalHandle: {
    width: 40,
    height: 4,
    backgroundColor: theme.colors.border.subtle,
    borderRadius: 2,
    alignSelf: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 16,
    textAlign: 'center',
  },
  modalOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 4,
  },
  modalOptionSelected: {
    backgroundColor: `${theme.colors.primary.DEFAULT}22`,
    borderWidth: 1,
    borderColor: theme.colors.primary.DEFAULT,
  },
  modalOptionText: {
    fontSize: 16,
    color: theme.colors.text.primary,
  },
  modalOptionTextSelected: {
    color: theme.colors.primary.light,
    fontWeight: 'bold',
  },
  checkmark: {
    color: theme.colors.primary.DEFAULT,
    fontWeight: 'bold',
    fontSize: 16,
  },
  proCard: {
    borderColor: 'rgba(251,191,36,0.3)',
    backgroundColor: 'rgba(251,191,36,0.05)',
    padding: 16,
    gap: 14,
  },
  proHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
  },
  proIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(251,191,36,0.15)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  proTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 2,
  },
  proSubtitle: {
    fontSize: 13,
    color: theme.colors.text.secondary,
  },
  upgradeBtn: {
    backgroundColor: '#fbbf24',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  upgradeBtnText: {
    color: '#000',
    fontWeight: 'bold',
    fontSize: 15,
  },
});
