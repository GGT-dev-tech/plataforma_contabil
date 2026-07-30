export const VARIANTS = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary',
  DANGER: 'danger',
  GHOST: 'ghost'
} as const;

export type ButtonVariant = typeof VARIANTS[keyof typeof VARIANTS];

export const SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg'
} as const;

export type ComponentSize = typeof SIZES[keyof typeof SIZES];
