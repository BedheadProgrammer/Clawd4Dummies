import { memo, ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  borderColor?: string;
}

export const Card = memo(function Card({
  children,
  className = '',
  padding = 'md',
  borderColor,
}: CardProps) {
  const paddingStyles = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  const borderStyle = borderColor ? `border-l-4 ${borderColor}` : '';

  return (
    <div className={`bg-elevated rounded-lg ${borderStyle} ${paddingStyles[padding]} ${className}`}>
      {children}
    </div>
  );
});
