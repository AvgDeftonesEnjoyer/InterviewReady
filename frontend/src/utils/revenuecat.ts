import Purchases, {
  PurchasesPackage,
  CustomerInfo,
} from 'react-native-purchases'
import { Platform } from 'react-native'

const REVENUECAT_KEYS = {
  ios:     'appl_xxxxxxxxxx',  // з RevenueCat dashboard
  android: 'goog_xxxxxxxxxx',  // з RevenueCat dashboard
}

export const initRevenueCat = async (userId: string) => {
  Purchases.setLogLevel(Purchases.LOG_LEVEL.DEBUG)

  await Purchases.configure({
    apiKey: Platform.OS === 'ios'
      ? REVENUECAT_KEYS.ios
      : REVENUECAT_KEYS.android,
    appUserID: userId,  // наш user.id як ідентифікатор
  })
}

export const getOfferings = async () => {
  try {
    const offerings = await Purchases.getOfferings()
    return offerings.current?.availablePackages || []
  } catch (e) {
    console.error('RevenueCat getOfferings error:', e)
    return []
  }
}

export const purchasePackage = async (pkg: PurchasesPackage) => {
  const { customerInfo } = await Purchases.purchasePackage(pkg)
  return customerInfo
}

export const getCustomerInfo = async (): Promise<CustomerInfo> => {
  return await Purchases.getCustomerInfo()
}

export const restorePurchases = async () => {
  return await Purchases.restorePurchases()
}
