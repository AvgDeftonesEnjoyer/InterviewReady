import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { PLANS } from '../config/plans';
import { theme } from '../theme';

interface PlanCardProps {
  plan: 'FREE' | 'PRO' | 'PRO_PLUS';
  isCurrentPlan: boolean;
  billingCycle: 'monthly' | 'annual';
  onUpgrade: () => void;
}

export const PlanCard = ({ plan, isCurrentPlan, billingCycle, onUpgrade }: PlanCardProps) => {
  const config = PLANS[plan];
  
  if (!config) return null;

  const price = billingCycle === 'annual'
    ? config.price_year / 12
    : config.price_month;

  return (
    <View style={[
      styles.card,
      isCurrentPlan && styles.currentCard,
      plan === 'PRO' && styles.popularCard,
      plan === 'PRO_PLUS' && styles.proPlusCard,
    ]}>
      {plan === 'PRO' && (
        <View style={styles.popularBadge}>
          <Text style={styles.popularBadgeText}>POPULAR</Text>
        </View>
      )}

      <View style={styles.header}>
        <Text style={styles.planIcon}>{config.icon}</Text>
        <Text style={styles.planName}>{config.name}</Text>
      </View>

      <Text style={styles.price}>
        {price === 0 ? 'Free' : `$${price.toFixed(price % 1 !== 0 ? 2 : 0)} / month`}
      </Text>
      {billingCycle === 'annual' && price > 0 && (
        <Text style={styles.annualNote}>
          ${config.price_year} / year · Save 20%
        </Text>
      )}

      <View style={styles.features}>
        {config.features.map(f => (
          <View key={f} style={styles.featureRow}>
            <Text style={styles.check}>✓</Text>
            <Text style={styles.featureText}>{f}</Text>
          </View>
        ))}
        {config.limitations.map(l => (
          <View key={l} style={styles.featureRow}>
            <Text style={styles.cross}>✗</Text>
            <Text style={styles.limitText}>{l}</Text>
          </View>
        ))}
      </View>

      {!isCurrentPlan && plan !== 'FREE' && (
        <TouchableOpacity
          style={[styles.upgradeBtn, { backgroundColor: config.color }]}
          onPress={onUpgrade}
        >
          <Text style={styles.upgradeBtnText}>
            Upgrade to {config.name} →
          </Text>
        </TouchableOpacity>
      )}

      {isCurrentPlan && (
        <View style={styles.currentBadge}>
          <Text style={styles.currentBadgeText}>✓ Current Plan</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: theme.colors.background.card,
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    position: 'relative',
  },
  currentCard: {
    borderColor: 'rgba(34,197,94,0.4)', // green for current
  },
  popularCard: {
    borderColor: '#6C63FF',
    shadowColor: '#6C63FF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 5,
  },
  proPlusCard: {
    borderColor: '#f59e0b',
  },
  popularBadge: {
    position: 'absolute',
    top: -12,
    right: 20,
    backgroundColor: '#6C63FF',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  popularBadgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 16,
  },
  planIcon: {
    fontSize: 24,
  },
  planName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
  },
  price: {
    fontSize: 24,
    fontWeight: '800',
    color: theme.colors.text.primary,
    marginBottom: 4,
  },
  annualNote: {
    fontSize: 13,
    color: '#10b981', // green for savings
    fontWeight: '600',
    marginBottom: 16,
  },
  features: {
    marginTop: 16,
    marginBottom: 24,
    gap: 12,
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  check: {
    color: '#10b981',
    fontWeight: 'bold',
    fontSize: 16,
    marginTop: -2,
  },
  cross: {
    color: theme.colors.status.error,
    fontWeight: 'bold',
    fontSize: 16,
    marginTop: -2,
  },
  featureText: {
    color: theme.colors.text.primary,
    fontSize: 15,
    flex: 1,
    lineHeight: 22,
  },
  limitText: {
    color: theme.colors.text.muted,
    fontSize: 15,
    flex: 1,
    lineHeight: 22,
  },
  upgradeBtn: {
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  upgradeBtnText: {
    color: '#000', // Better contrast against bright colors generally, or conditional in a real app
    fontWeight: 'bold',
    fontSize: 16,
  },
  currentBadge: {
    backgroundColor: 'rgba(34,197,94,0.1)',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  currentBadgeText: {
    color: '#10b981',
    fontWeight: 'bold',
    fontSize: 16,
  },
});
