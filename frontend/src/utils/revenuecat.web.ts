// Web stub — react-native-purchases is not available on web.
// Metro picks this file automatically when bundling for web (*.web.ts takes priority).

export const initRevenueCat = async (_userId: string): Promise<void> => {}

export const getOfferings = async (): Promise<any[]> => []

export const purchasePackage = async (_pkg: any): Promise<any> => {
  throw new Error('In-app purchases are not available on web')
}

export const getCustomerInfo = async (): Promise<null> => null

export const restorePurchases = async (): Promise<null> => null
