import React from 'react';
import { GlassCard } from './GlassCard';

interface StatCardProps {
  title: string;
  value: string | number;
  trend?: string;
  trendUp?: boolean;
  colorBorder?: 'blue' | 'green' | 'yellow' | 'red';
}

export const StatCard: React.FC<StatCardProps> = ({ title, value, trend, trendUp, colorBorder }) => {
  const borderColors = {
    blue: 'border-l-4 border-l-blue-500',
    green: 'border-l-4 border-l-green-500',
    yellow: 'border-l-4 border-l-yellow-500',
    red: 'border-l-4 border-l-red-500',
  };

  return (
    <GlassCard className={`flex flex-col ${colorBorder ? borderColors[colorBorder] : ''}`}>
      <span className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</span>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-3xl font-semibold tracking-tight text-gray-900 dark:text-white">{value}</span>
        {trend && (
          <span className={`text-sm font-medium ${trendUp ? 'text-green-600' : 'text-red-600'}`}>
            {trend}
          </span>
        )}
      </div>
    </GlassCard>
  );
};
