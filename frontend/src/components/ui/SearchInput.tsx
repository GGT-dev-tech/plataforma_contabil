import React from 'react';
import { Search } from 'lucide-react';
import { Input } from './Input';

interface SearchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const SearchInput = React.forwardRef<HTMLInputElement, SearchInputProps>(
  (props, ref) => {
    return <Input ref={ref} icon={<Search className="h-5 w-5" />} type="search" {...props} />;
  }
);
SearchInput.displayName = 'SearchInput';
