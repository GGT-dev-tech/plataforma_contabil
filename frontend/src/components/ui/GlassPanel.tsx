import React from 'react';

interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const GlassPanel: React.FC<GlassPanelProps> = ({ children, className = '', ...props }) => {
  return (
    <div 
      className={`glass-panel rounded-2xl overflow-hidden ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
