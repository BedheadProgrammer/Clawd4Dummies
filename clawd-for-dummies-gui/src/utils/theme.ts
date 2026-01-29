// Theme color tokens matching tailwind.config.js
export const colors = {
  // Primary backgrounds
  spaceBlack: '#0D1117',
  elevated: '#161B22',
  // Text
  textPrimary: '#E6EDF3',
  textSecondary: '#7D8590',
  // Accent
  actionBlue: '#58A6FF',
  // Severity colors
  critical: '#F85149',
  high: '#DB6D28',
  medium: '#D29922',
  low: '#3FB950',
  info: '#8B949E',
} as const;

// Animation tokens
export const transitions = {
  fast: 'duration-150',
  normal: 'duration-250',
  slow: 'duration-500',
} as const;

// Spacing tokens
export const spacing = {
  xs: 'p-1',
  sm: 'p-2',
  md: 'p-4',
  lg: 'p-6',
  xl: 'p-8',
} as const;
