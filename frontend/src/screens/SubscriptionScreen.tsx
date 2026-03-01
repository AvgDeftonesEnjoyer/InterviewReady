import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Platform,
  Linking,
  AppState,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { theme } from '../theme';
import { apiClient } from '../api/client';
import { PlanCard } from '../components/PlanCard';
import { PLANS } from '../config/plans';
import { ActivityIndicator } from 'react-native';
import { ArrowLeft } from 'lucide-react-native';
import { PurchasesPackage } from 'react-native-purchases';
import { getOfferings, purchasePackage, restorePurchases } from '../utils/revenuecat';

// Declare window for TypeScript (web only)
declare global {
  interface Window {
    open: (url?: string, target?: string, features?: string) => Window | null;
  }
}

export const SubscriptionScreen = () => {
  const navigation = useNavigation<any>();
  const [status, setStatus]       = useState<any>(null);
  const [packages, setPackages]   = useState<PurchasesPackage[]>([]);
  const [cycle, setCycle]         = useState<'monthly' | 'annual'>('monthly');
  const [loading, setLoading]     = useState(true);
  const [purchasing, setPurchasing] = useState(false);

  useEffect(() => {
    loadData();

    // AppState listener для Android (повернення після Stripe):
    const subscription = AppState.addEventListener(
      'change',
      async (nextState) => {
        if (nextState === 'active') {
          // Юзер повернувся в додаток — перевірити статус
          await loadData();
        }
      }
    );

    // WEB: Перевірка URL параметрів після повернення з Stripe
    let pollingInterval: NodeJS.Timeout | null = null;
    if (Platform.OS === 'web') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('subscription') === 'success') {
        // Очистити URL
        window.history.replaceState({}, '', window.location.pathname);
        
        // Polling: перевіряти статус кожні 2 секунди (max 15 секунд)
        let attempts = 0;
        const maxAttempts = 15;
        
        pollingInterval = setInterval(async () => {
          attempts++;
          console.log(`Polling attempt ${attempts}/${maxAttempts}...`);
          await loadData();
          
          // Stop polling if subscription is active or max attempts reached
          if (attempts >= maxAttempts) {
            if (pollingInterval) clearInterval(pollingInterval);
          }
        }, 2000);
      }
    }

    return () => {
      subscription?.remove();
      if (pollingInterval) clearInterval(pollingInterval);
    };
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Завантажити статус підписки з нашого API
      const { data } = await apiClient.get('/api/subscriptions/status/');
      setStatus(data);

      // Завантажити пакети з RevenueCat (для iOS)
      if (Platform.OS === 'ios') {
        const pkgs = await getOfferings();
        setPackages(pkgs);
      }
    } catch (e) {
      console.error('Failed to load subscription data', e);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (plan: 'PRO' | 'PRO_PLUS') => {
    console.log('handleUpgrade called:', { plan, platform: Platform.OS });
    setPurchasing(true);

    try {
      if (Platform.OS === 'android' || Platform.OS === 'web') {
        // ANDROID & WEB → Stripe через браузер
        console.log('Starting Stripe checkout (Android/Web)');
        await handleStripeCheckout(plan);
      } else {
        // iOS → Apple IAP через RevenueCat
        console.log('iOS: Starting Apple IAP');
        await handleAppleIAP(plan);
      }
    } catch (e: any) {
      console.error('handleUpgrade error:', e);
      if (!e.userCancelled) {
        Alert.alert('Error', 'Purchase failed. Please try again.');
      }
    } finally {
      setPurchasing(false);
    }
  };

  // ANDROID & WEB: Stripe
  const handleStripeCheckout = async (plan: string) => {
    console.log('Starting Stripe checkout:', { plan, cycle, platform: Platform.OS });
    try {
      const { data } = await apiClient.post(
        '/api/subscriptions/stripe/create-checkout/',
        { plan, billing_cycle: cycle }
      );

      console.log('Stripe response:', data);

      if (data.checkout_url) {
        // Відкрити Stripe в браузері
        console.log('Opening Stripe checkout:', data.checkout_url);
        
        if (Platform.OS === 'web') {
          // WEB: відкрити в новому вікні
          window.open(data.checkout_url, '_blank');
        } else {
          // ANDROID: відкрити через Linking
          const supported = await Linking.canOpenURL(data.checkout_url);
          if (supported) {
            await Linking.openURL(data.checkout_url);
          } else {
            Alert.alert('Error', 'Cannot open browser');
          }
        }
        // Після повернення — AppState listener перевірить статус
      } else {
        console.error('No checkout_url in response');
        Alert.alert('Error', 'Failed to create checkout session');
      }
    } catch (e: any) {
      console.error('Stripe checkout error:', {
        message: e.message,
        response: e.response?.data,
        status: e.response?.status
      });
      const errorMsg = e.response?.data?.error || e.message || 'Stripe checkout failed';
      Alert.alert('Error', errorMsg);
      throw e;
    }
  };

  // iOS: Apple IAP
  const handleAppleIAP = async (plan: string) => {
    // Знайти потрібний пакет
    const targetId = plan === 'PRO'
      ? `com.interviewready.${plan.toLowerCase()}.${cycle}`
      : `com.interviewready.proplus.${cycle}`;

    const pkg = packages.find(p =>
      p.product.identifier === targetId
    );

    if (!pkg) {
      Alert.alert('Error', 'Product not available');
      return;
    }

    // Купити через Apple IAP
    const customerInfo = await purchasePackage(pkg);

    // Перевірити що підписка активна
    const isActive =
      customerInfo.entitlements.active['pro'] !== undefined ||
      customerInfo.entitlements.active['pro_plus'] !== undefined;

    if (isActive) {
      // RevenueCat автоматично надішле webhook на бекенд
      // Просто оновити UI:
      await loadData();
      Alert.alert('Success! 🎉', `Welcome to ${plan.toUpperCase()}!`);
    }
  };

  const handleCancel = async () => {
    const performCancel = async () => {
      try {
        if (Platform.OS === 'android') {
          await apiClient.post('/subscriptions/stripe/cancel/');
          await loadData();
          Alert.alert('Subscription Canceled', 'Your subscription will not renew.');
        } else {
          // iOS: через налаштування Apple
          await Linking.openURL(
            'https://apps.apple.com/account/subscriptions'
          );
          Alert.alert('Info', 'Please cancel your subscription in Apple Settings');
        }
      } catch (e) {
        Alert.alert('Error', 'Could not cancel subscription');
      }
    };

    Alert.alert(
      'Cancel Subscription',
      'Are you sure? You will lose PRO access at the end of billing period.',
      [
        { text: 'Keep PRO', style: 'cancel' },
        {
          text: 'Cancel',
          style: 'destructive',
          onPress: performCancel
        }
      ]
    );
  };

  const handleRestore = async () => {
    try {
      setPurchasing(true);
      const customerInfo = await restorePurchases();
      await loadData();
      Alert.alert('Done', 'Purchases restored successfully!');
    } catch (e) {
      Alert.alert('Error', 'Could not restore purchases');
    } finally {
      setPurchasing(false);
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
          onUpgrade={() => handleUpgrade(plan as 'PRO' | 'PRO_PLUS')}
        />
      ))}

      {/* RESTORE PURCHASES */}
      {Platform.OS === 'ios' && currentPlan === 'FREE' && (
        <TouchableOpacity
          style={styles.restoreBtn}
          onPress={handleRestore}
        >
          <Text style={styles.restoreText}>
            Restore Purchases
          </Text>
        </TouchableOpacity>
      )}

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

      {purchasing && (
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
  restoreBtn: {
    marginTop: 16,
    padding: 16,
    alignItems: 'center',
    backgroundColor: '#161827',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  restoreText: {
    color: theme.colors.text.primary,
    fontWeight: '600',
    fontSize: 15,
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
