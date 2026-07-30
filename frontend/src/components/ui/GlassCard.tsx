import React from 'react';

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hoverable?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({ children, className = '', hoverable = false, ...props }) => {
  return (
    <div 
      className={`
        glass rounded-xl p-6 
        ${hoverable ? 'hover:shadow-lg hover:-translate-y-1 hover:bg-white/80 dark:hover:bg-gray-800/80 cursor-pointer' : ''} 
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};
