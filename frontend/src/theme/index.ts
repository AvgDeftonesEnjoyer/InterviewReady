import { colors } from './colors';
import { typography } from './typography';

export const theme = {
  colors,
  typography,
  shadows: {
    glow: {
      shadowColor: colors.primary.DEFAULT,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 24,
      elevation: 8, // Android equivalent
    }
  }
};
