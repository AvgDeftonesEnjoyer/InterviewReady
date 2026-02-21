export const typography = {
  // Font Families
  family: {
    primary: 'System', // Since we don't have Inter/SF Pro loaded yet, fallback to System fonts which look like SF Pro on iOS
  },

  // Font Sizes
  size: {
    h1: 28, // Headers: 28px
    h2: 24, // Secondary Headers
    h3: 18, // Subheaders: 18px
    body: 15, // Body: 15px
    caption: 12, // Caption: 12px
  },

  // Font Weights
  weight: {
    bold: '700' as const,     // Headers: 28px bold
    semibold: '600' as const, // Subheaders: 18px semibold
    medium: '500' as const,
    regular: '400' as const,  // Body: 15px regular
  },
};
