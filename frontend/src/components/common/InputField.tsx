import React from 'react';

interface InputFieldProps {
    label: string;
    type?: string;
    placeholder: string;
    icon: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const Inputfield: React.FC<InputFieldProps> = ({ label, type = 'text', placeholder, icon, value, onChange }) => {
   return (
    <div className="space-y-2">
      <label className="block text-xs font-semibold uppercase tracking-widest text-on-surface-variant px-1">
        {label}
      </label>
      <div className="relative">
        <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline text-xl">
          {icon}
        </span>
        <input 
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className="w-full pl-12 pr-4 py-4 bg-surface-container-lowest border-none rounded-xl focus:ring-2 focus:ring-primary outline-none transition-all shadow-sm"
          required
        />
      </div>
    </div>
  ); 
};

export default Inputfield;