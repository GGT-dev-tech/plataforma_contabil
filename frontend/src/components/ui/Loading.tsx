import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../utils/cn';

interface LoadingProps {
  text?: string;
  fullScreen?: boolean;
}

export const Loading: React.FC<LoadingProps> = ({ text = 'Carregando...', fullScreen = false }) => {
  const content = (
    <div className="flex flex-col items-center justify-center p-8 text-gray-500 dark:text-gray-400">
      <Loader2 className="w-8 h-8 animate-spin mb-4 text-blue-500" />
      <p className="text-sm font-medium">{text}</p>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
        {content}
      </div>
    );
  }

  return content;
};

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

export const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(({ className, ...props }, ref) => {
  return (
    <div ref={ref} className={cn("animate-pulse rounded-md bg-gray-200/50 dark:bg-gray-800/50", className)} {...props} />
  );
});
Skeleton.displayName = "Skeleton";
