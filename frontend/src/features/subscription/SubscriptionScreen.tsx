import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, Platform, ScrollView, Image } from 'react-native';
import { useSubscription, initiateStripePayment, initiateApplePayment } from './hooks';
import { theme } from '../../theme';
import { LinearGradient } from 'expo-linear-gradient';
import { Check, X, ShieldCheck, Zap, Star } from 'lucide-react-native';

const FEATURES = [
  { name: 'Basic Interview Questions', free: true, pro: true },
  { name: 'Daily Progress Tracking', free: true, pro: true },
  { name: 'Unlimited AI Sandbox', free: false, pro: true },
  { name: 'Hard Scripted Scenarios', free: false, pro: true },
  { name: 'Advanced Analytics', free: false, pro: true },
  { name: 'Priority Support', free: false, pro: true },
];

const TESTIMONIALS = [
  {
    id: 1,
    name: 'Sarah J.',
    role: 'Landed offer at Google',
    text: 'The AI practice mode completely changed my confidence. Worth every penny.',
    avatar: 'https://i.pravatar.cc/150?u=sarah',
  },
  {
    id: 2,
    name: 'Michael T.',
    role: 'Senior Frontend Engineer',
    text: 'Best investment for interview prep. The hard scenarios are incredibly realistic.',
    avatar: 'https://i.pravatar.cc/150?u=michael',
  }
];

export const SubscriptionScreen = () => {
  const { data: sub, isLoading, refetch } = useSubscription();
  const [processing, setProcessing] = useState(false);
  const [isAnnual, setIsAnnual] = useState(true);

  const handleUpgrade = async () => {
    setProcessing(true);
    try {
      if (Platform.OS === 'ios') {
        await initiateApplePayment();
      } else {
        await initiateStripePayment();
      }
      Alert.alert("Success", "Welcome to PRO!");
      refetch();
    } catch (error) {
           Alert.alert("Payment Failed", "Something went wrong.");
    } finally {
      setProcessing(false);
    }
  };

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={theme.colors.status.warning} />
      </View>
    );
  }

  if (sub?.is_pro) {
    return (
      <View style={styles.center}>
        <LinearGradient
          colors={['rgba(250, 204, 21, 0.2)', 'rgba(250, 204, 21, 0.05)']}
          style={styles.proActiveCard}
        >
          <View style={styles.proIconBg}>
             <ShieldCheck color={theme.colors.status.warning} size={48} />
          </View>
          <Text style={styles.proActiveTitle}>You are a PRO</Text>
          <Text style={styles.proActiveDesc}>Your unlimited access to all premium features is active. Keep crushing those interviews!</Text>
        </LinearGradient>
      </View>
    );
  }

  const price = isAnnual ? '$7.99' : '$12.99';
  const period = isAnnual ? '/ mo, billed annually' : '/ mo';

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      {/* Hero Section */}
      <View style={styles.heroContainer}>
        <LinearGradient
          colors={['#F59E0B', '#FCD34D', '#F59E0B']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.heroBadge}
        >
          <Text style={styles.heroBadgeText}>PRO</Text>
        </LinearGradient>
        <Text style={styles.headerTitle}>Unlock Your True Potential</Text>
        <Text style={styles.headerSubtitle}>Join thousands of engineers landing their dream jobs.</Text>
      </View>

      {/* Pricing Toggle */}
      <View style={styles.toggleContainer}>
        <View style={styles.toggleBg}>
          <TouchableOpacity 
            style={[styles.toggleBtn, !isAnnual && styles.toggleBtnActive]}
            onPress={() => setIsAnnual(false)}
          >
            <Text style={[styles.toggleText, !isAnnual && styles.toggleTextActive]}>Monthly</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.toggleBtn, isAnnual && styles.toggleBtnActive]}
            onPress={() => setIsAnnual(true)}
          >
            <Text style={[styles.toggleText, isAnnual && styles.toggleTextActive]}>Annually</Text>
            {isAnnual && <View style={styles.savePill}><Text style={styles.savePillText}>SAVE 38%</Text></View>}
          </TouchableOpacity>
        </View>
      </View>

      {/* Feature Comparison */}
      <View style={styles.comparisonCard}>
        <View style={styles.tableHeader}>
          <View style={styles.colLabel}><Text style={styles.colHeaderText}>Features</Text></View>
          <View style={styles.colFree}><Text style={styles.colHeaderText}>Free</Text></View>
          <View style={styles.colPro}>
             <Text style={styles.colHeaderTextPro}>PRO</Text>
          </View>
        </View>

        {FEATURES.map((feat, index) => (
          <View key={index} style={styles.tableRow}>
            <View style={styles.colLabel}>
               <Text style={styles.featureName}>{feat.name}</Text>
            </View>
            <View style={styles.colFree}>
               {feat.free 
                 ? <Check size={18} color={theme.colors.text.muted} /> 
                 : <X size={18} color={theme.colors.border.strong} />
               }
            </View>
            <View style={styles.colPro}>
               {feat.pro 
                 ? <Check size={18} color={theme.colors.status.warning} /> 
                 : <X size={18} color={theme.colors.text.muted} />
               }
            </View>
          </View>
        ))}
      </View>

      {/* Details & CTA */}
      <View style={styles.checkoutSection}>
         <Text style={styles.priceValue}>{price} <Text style={styles.pricePeriod}>{period}</Text></Text>
         
         <TouchableOpacity activeOpacity={0.9} onPress={handleUpgrade} disabled={processing}>
           <LinearGradient
              colors={['#F59E0B', '#D97706']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.ctaButton}
           >
             {processing ? (
                <ActivityIndicator color="#000" />
             ) : (
                <>
                  <Zap size={20} color="#000" />
                  <Text style={styles.ctaText}>Upgrade Now</Text>
                </>
             )}
           </LinearGradient>
         </TouchableOpacity>
         <Text style={styles.guaranteeText}>Cancel anytime. Secure checkout.</Text>
      </View>

      {/* Testimonials */}
      <Text style={styles.testimonialsHeader}>Hall of Fame</Text>
      {TESTIMONIALS.map(t => (
        <View key={t.id} style={styles.testimonialCard}>
          <Image source={{ uri: t.avatar }} style={styles.tAvatar} />
          <View style={styles.tContent}>
            <View style={styles.tHeaderRow}>
               <Text style={styles.tName}>{t.name}</Text>
               <View style={styles.starsRow}>
                  {[1,2,3,4,5].map(s => <Star key={s} size={12} color={theme.colors.status.warning} fill={theme.colors.status.warning} />)}
               </View>
            </View>
            <Text style={styles.tRole}>{t.role}</Text>
            <Text style={styles.tText}>"{t.text}"</Text>
          </View>
        </View>
      ))}

      <View style={{ height: 120 }} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: theme.colors.background.primary, 
  },
  content: {
    padding: 20,
    paddingTop: 60,
  },
  center: { 
    flex: 1, 
    backgroundColor: theme.colors.background.primary, 
    justifyContent: 'center', 
    alignItems: 'center',
    padding: 24,
  },
  
  heroContainer: {
    alignItems: 'center',
    marginBottom: 32,
    marginTop: 20,
  },
  heroBadge: {
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 12,
    marginBottom: 20,
  },
  heroBadgeText: {
    color: '#000',
    fontWeight: '900',
    fontSize: 16,
    letterSpacing: 2,
  },
  headerTitle: {
    color: theme.colors.text.primary,
    fontSize: 32,
    fontWeight: theme.typography.weight.bold,
    textAlign: 'center',
    marginBottom: 12,
    lineHeight: 40,
  },
  headerSubtitle: {
    color: theme.colors.text.secondary,
    fontSize: 16,
    textAlign: 'center',
    paddingHorizontal: 20,
    lineHeight: 24,
  },

  toggleContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  toggleBg: {
    flexDirection: 'row',
    backgroundColor: theme.colors.background.card,
    borderRadius: 16,
    padding: 4,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  toggleBtn: {
    flexDirection: 'row',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
  },
  toggleBtnActive: {
    backgroundColor: theme.colors.background.elevated,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  toggleText: {
    color: theme.colors.text.muted,
    fontWeight: theme.typography.weight.bold,
    fontSize: 15,
  },
  toggleTextActive: {
    color: theme.colors.text.primary,
  },
  savePill: {
    backgroundColor: `${theme.colors.status.success}20`,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
    marginLeft: 8,
  },
  savePillText: {
    color: theme.colors.status.success,
    fontSize: 10,
    fontWeight: 'bold',
  },

  comparisonCard: {
    backgroundColor: theme.colors.background.card,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
    overflow: 'hidden',
    marginBottom: 32,
  },
  tableHeader: {
    flexDirection: 'row',
    padding: 16,
    paddingVertical: 20,
    backgroundColor: theme.colors.background.elevated,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.subtle,
  },
  tableRow: {
    flexDirection: 'row',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.subtle,
    alignItems: 'center',
  },
  colLabel: {
    flex: 3,
  },
  colFree: {
    flex: 1,
    alignItems: 'center',
  },
  colPro: {
    flex: 1,
    alignItems: 'center',
  },
  colHeaderText: {
    color: theme.colors.text.secondary,
    fontWeight: theme.typography.weight.bold,
    fontSize: 13,
    textTransform: 'uppercase',
  },
  colHeaderTextPro: {
    color: theme.colors.status.warning,
    fontWeight: theme.typography.weight.bold,
    fontSize: 13,
    textTransform: 'uppercase',
  },
  featureName: {
    color: theme.colors.text.primary,
    fontSize: 14,
    fontWeight: theme.typography.weight.medium,
  },

  checkoutSection: {
    backgroundColor: `${theme.colors.status.warning}10`,
    padding: 24,
    borderRadius: 24,
    alignItems: 'center',
    marginBottom: 40,
    borderWidth: 1,
    borderColor: `${theme.colors.status.warning}30`,
  },
  priceValue: {
    color: theme.colors.text.primary,
    fontSize: 36,
    fontWeight: theme.typography.weight.bold,
    marginBottom: 20,
  },
  pricePeriod: {
    color: theme.colors.status.warning,
    fontSize: 16,
    fontWeight: theme.typography.weight.medium,
  },
  ctaButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    paddingHorizontal: 32,
    borderRadius: 16,
    width: '100%',
    shadowColor: theme.colors.status.warning,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 8,
  },
  ctaText: {
    color: '#000',
    fontSize: 18,
    fontWeight: '900',
    marginLeft: 8,
    letterSpacing: 0.5,
  },
  guaranteeText: {
    color: theme.colors.text.muted,
    fontSize: 12,
    marginTop: 16,
  },

  testimonialsHeader: {
    color: theme.colors.text.primary,
    fontSize: 20,
    fontWeight: theme.typography.weight.bold,
    marginBottom: 20,
    paddingHorizontal: 8,
  },
  testimonialCard: {
    flexDirection: 'row',
    backgroundColor: theme.colors.background.card,
    padding: 20,
    borderRadius: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: theme.colors.border.subtle,
  },
  tAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    marginRight: 16,
    backgroundColor: theme.colors.background.elevated,
  },
  tContent: {
    flex: 1,
  },
  tHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  tName: {
    color: theme.colors.text.primary,
    fontWeight: theme.typography.weight.bold,
    fontSize: 15,
  },
  starsRow: {
    flexDirection: 'row',
    gap: 2,
  },
  tRole: {
    color: theme.colors.primary.light,
    fontSize: 12,
    marginBottom: 8,
  },
  tText: {
    color: theme.colors.text.secondary,
    fontSize: 14,
    fontStyle: 'italic',
    lineHeight: 20,
  },

  proActiveCard: {
    padding: 32,
    borderRadius: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: `${theme.colors.status.warning}40`,
    width: '100%',
  },
  proIconBg: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: `${theme.colors.status.warning}20`,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  proActiveTitle: {
    color: theme.colors.status.warning,
    fontSize: 28,
    fontWeight: theme.typography.weight.bold,
    marginBottom: 12,
  },
  proActiveDesc: {
    color: theme.colors.text.secondary,
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
  }
});
