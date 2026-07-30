import React from 'react';
import { cn } from '../../utils/cn';

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hoverable?: boolean;
}

export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ children, className, hoverable = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "rounded-xl border border-white/40 bg-white/50 text-gray-950 shadow-sm backdrop-blur-md transition-all dark:border-white/10 dark:bg-gray-900/50 dark:text-gray-50",
          hoverable && "hover:-translate-y-1 hover:shadow-lg hover:bg-white/80 dark:hover:bg-gray-800/80 cursor-pointer",
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
GlassCard.displayName = "GlassCard";
