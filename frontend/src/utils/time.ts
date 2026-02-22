export const getTimeUntilMidnight = (): string => {
  const now = new Date();
  const midnight = new Date();
  midnight.setUTCHours(23, 59, 59, 999);
  
  // If we passed UTC midnight locally, we might need to adjust, 
  // but generally DRF resets at UTC Midnight. Let's use local midnight for the UI if that's what the user prefers, or stick to UTC.
  // The user snip suggested:
  // midnight.setHours(24, 0, 0, 0)
  
  const localMidnight = new Date();
  localMidnight.setHours(24, 0, 0, 0);
  
  const diff = localMidnight.getTime() - now.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  
  return `${hours}h ${minutes}m`;
};
