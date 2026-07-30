import React from 'react';

export const Tooltip: React.FC<{ children: React.ReactNode; content: string }> = ({ children, content }) => {
  return (
    <div className="relative group inline-block">
      {children}
      <div className="absolute z-10 hidden group-hover:block w-auto p-2 min-w-max bottom-full left-1/2 -translate-x-1/2 mb-2 bg-gray-900 text-white text-xs rounded shadow-lg transition-opacity">
        {content}
        <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
      </div>
    </div>
  );
};
