import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useTranslation } from 'react-i18next';
import { theme } from '../theme';
import { useLanguage } from '../hooks/useLanguage';
import { ArrowLeft } from 'lucide-react-native';

export const SettingsScreen = ({ navigation }: any) => {
  const insets = useSafeAreaInsets();
  const { t, i18n } = useTranslation();
  const { switchLanguage, loading } = useLanguage();

  const handleLanguageSwitch = async (lang: 'en' | 'uk') => {
    if (i18n.language !== lang) {
      await switchLanguage(lang);
    }
  };

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <ArrowLeft color={theme.colors.text.primary} size={24} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{t('settings.title')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <View style={styles.content}>
        <Text style={styles.sectionTitle}>{t('settings.language')}</Text>
        
        <View style={styles.card}>
          <TouchableOpacity 
            style={[styles.langOption, i18n.language === 'en' && styles.activeLang]} 
            onPress={() => handleLanguageSwitch('en')}
            disabled={loading}
          >
            <Text style={[styles.langText, i18n.language === 'en' && styles.activeLangText]}>English</Text>
            {i18n.language === 'en' && <Text style={styles.checkIcon}>✅</Text>}
          </TouchableOpacity>
          
          <View style={styles.divider} />
          
          <TouchableOpacity 
            style={[styles.langOption, i18n.language === 'uk' && styles.activeLang]} 
            onPress={() => handleLanguageSwitch('uk')}
            disabled={loading}
          >
            <Text style={[styles.langText, i18n.language === 'uk' && styles.activeLangText]}>Українська</Text>
            {i18n.language === 'uk' && <Text style={styles.checkIcon}>✅</Text>}
          </TouchableOpacity>
        </View>

        {loading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color={theme.colors.primary.DEFAULT} />
          </View>
        )}
      </View>
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
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text.secondary,
    marginBottom: 12,
    textTransform: 'uppercase',
  },
  card: {
    backgroundColor: theme.colors.background.card,
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  langOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
  },
  activeLang: {
    backgroundColor: 'rgba(108, 99, 255, 0.1)',
  },
  langText: {
    fontSize: 18,
    color: theme.colors.text.primary,
  },
  activeLangText: {
    color: theme.colors.primary.light,
    fontWeight: 'bold',
  },
  divider: {
    height: 1,
    backgroundColor: theme.colors.border.subtle,
    marginLeft: 20,
  },
  checkIcon: {
    fontSize: 16,
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 16,
  }
});
