import React from 'react';
import { Search } from 'lucide-react';
import { Input } from './Input';
import { cn } from '../../utils/cn';

interface SearchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const SearchInput = React.forwardRef<HTMLInputElement, SearchInputProps>(
  ({ className, ...props }, ref) => {
    return (
      <div className={cn("relative", className)}>
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input 
          ref={ref} 
          type="search" 
          className="pl-9"
          {...props} 
        />
      </div>
    );
  }
);
SearchInput.displayName = 'SearchInput';
