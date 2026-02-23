import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Platform,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { theme } from '../theme';
import { apiClient } from '../api/client';
import { PlanCard } from '../components/PlanCard';
import { PLANS } from '../config/plans';
import { ActivityIndicator } from 'react-native';
import { ArrowLeft } from 'lucide-react-native';

export const SubscriptionScreen = () => {
  const navigation = useNavigation<any>();
  const [status, setStatus] = useState<any>(null);
  const [cycle, setCycle] = useState<'monthly' | 'annual'>('monthly');
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const { data } = await apiClient.get('/subscriptions/status/');
      setStatus(data);
    } catch (e) {
      console.error('Failed to load subscription status', e);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (plan: string) => {
    setUpgrading(true);
    try {
      await apiClient.post('/subscriptions/upgrade/', {
        plan,
        billing_cycle: cycle,
      });
      await fetchStatus();
      Alert.alert('Success', `Upgraded to ${PLANS[plan as keyof typeof PLANS].name} successfully!`);
      // Could also go back or show nice animation
    } catch (e) {
      Alert.alert('Error', 'Upgrade failed.');
    } finally {
      setUpgrading(false);
    }
  };

  const handleCancel = async () => {
    const performCancel = async () => {
       try {
         await apiClient.post('/subscriptions/cancel/');
         await fetchStatus();
         if (Platform.OS === 'web') {
             window.alert('Subscription Canceled. Your subscription will not renew.');
         } else {
             Alert.alert('Subscription Canceled', 'Your subscription will not renew.');
         }
       } catch(e) {
          if (Platform.OS === 'web') {
             window.alert('Error. Could not cancel subscription.');
          } else {
             Alert.alert('Error', 'Could not cancel subscription.');
          }
       }
    };

    if (Platform.OS === 'web') {
        const confirmed = window.confirm('Are you sure? You will lose PRO access when it expires.');
        if (confirmed) {
            performCancel();
        }
    } else {
        Alert.alert(
          'Cancel Subscription',
          'Are you sure? You will lose PRO access when it expires.',
          [
            { text: 'Keep PRO', style: 'cancel' },
            {
              text: 'Cancel',
              style: 'destructive',
              onPress: performCancel
            }
          ]
        );
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const d = new Date(dateString);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={theme.colors.primary.DEFAULT} />
      </View>
    );
  }

  const currentPlan = status?.plan || 'FREE';

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* HEADER */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <ArrowLeft color="#fff" size={24} />
        </TouchableOpacity>
        <Text style={styles.title}>
          {currentPlan === 'FREE'
            ? '✨ Upgrade Your Plan'
            : `${PLANS[currentPlan as keyof typeof PLANS].icon} ${PLANS[currentPlan as keyof typeof PLANS].name} Active`
          }
        </Text>
        <View style={styles.backBtnPlaceholder} />
      </View>

      {/* BILLING TOGGLE */}
      {currentPlan === 'FREE' && (
        <View style={styles.toggle}>
          <TouchableOpacity
            style={[styles.toggleBtn, cycle === 'monthly' && styles.toggleActive]}
            onPress={() => setCycle('monthly')}
          >
            <Text style={[styles.toggleText, cycle === 'monthly' && styles.toggleTextActive]}>
              Monthly
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.toggleBtn, cycle === 'annual' && styles.toggleActive]}
            onPress={() => setCycle('annual')}
          >
            <Text style={[styles.toggleText, cycle === 'annual' && styles.toggleTextActive]}>
              Annual  🏷 -20%
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* USAGE */}
      {currentPlan !== 'FREE' && status?.interviews_limit && (
        <View style={styles.usageCard}>
          <Text style={styles.usageTitle}>Today's Usage</Text>
          
          <View style={styles.progressBarBg}>
            <View 
              style={[
                styles.progressBarFill, 
                { width: `${((status.interviews_limit - status.interviews_remaining) / status.interviews_limit) * 100}%` }
              ]} 
            />
          </View>

          <Text style={styles.usageDesc}>
            {status.interviews_limit - status.interviews_remaining} / {status.interviews_limit} interviews used
          </Text>
          
          {status.expires_at && (
            <Text style={styles.renewText}>
              Renews: {formatDate(status.expires_at)}
            </Text>
          )}
        </View>
      )}

      {/* PLAN CARDS */}
      {(['FREE', 'PRO', 'PRO_PLUS'] as const).map(plan => (
        <PlanCard
          key={plan}
          plan={plan}
          isCurrentPlan={plan === currentPlan}
          billingCycle={cycle}
          onUpgrade={() => handleUpgrade(plan)}
        />
      ))}

      {/* CANCEL */}
      {currentPlan !== 'FREE' && (
        <TouchableOpacity
          style={styles.cancelBtn}
          onPress={handleCancel}
        >
          <Text style={styles.cancelText}>
            Cancel Subscription
          </Text>
        </TouchableOpacity>
      )}
      
      {upgrading && (
        <View style={styles.upgradingOverlay}>
           <ActivityIndicator size="large" color="#fff" />
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0d0f1a', // requested background
  },
  content: {
    padding: 20,
    paddingBottom: 60,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0d0f1a',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 20,
    marginBottom: 24,
  },
  backBtn: {
    padding: 8,
    marginLeft: -8,
  },
  backBtnPlaceholder: {
    width: 40,
  },
  title: {
    fontSize: 24, // reduced slightly to fit with icon seamlessly
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    flex: 1,
  },
  toggle: {
    flexDirection: 'row',
    backgroundColor: '#161827',
    borderRadius: 12,
    padding: 4,
    marginBottom: 24,
  },
  toggleBtn: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 8,
  },
  toggleActive: {
    backgroundColor: '#6C63FF',
  },
  toggleText: {
    color: '#94a3b8',
    fontWeight: '600',
    fontSize: 15,
  },
  toggleTextActive: {
    color: '#fff',
  },
  usageCard: {
    backgroundColor: '#161827',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  usageTitle: {
    color: theme.colors.text.primary,
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  progressBarBg: {
    height: 8,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 12,
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#6C63FF',
    borderRadius: 4,
  },
  usageDesc: {
    color: theme.colors.text.primary,
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  renewText: {
    color: theme.colors.text.muted,
    fontSize: 13,
  },
  cancelBtn: {
    marginTop: 16,
    padding: 16,
    alignItems: 'center',
  },
  cancelText: {
    color: theme.colors.status.error,
    fontWeight: '600',
    fontSize: 15,
  },
  upgradingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 16,
  }
});
