'use client';

import { ReactNode } from 'react';

interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: ReactNode;
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => onOpenChange(false)} />
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full">
          {children}
        </div>
      </div>
    </div>
  );
}

interface DialogContentProps {
  children: ReactNode;
  className?: string;
}

export function DialogContent({ children, className = '' }: DialogContentProps) {
  return (
    <div className={`p-6 ${className}`}>
      {children}
    </div>
  );
}

interface DialogHeaderProps {
  children: ReactNode;
  className?: string;
}

export function DialogHeader({ children, className = '' }: DialogHeaderProps) {
  return (
    <div className={`mb-4 ${className}`}>
      {children}
    </div>
  );
}

interface DialogTitleProps {
  children: ReactNode;
  className?: string;
}

export function DialogTitle({ children, className = '' }: DialogTitleProps) {
  return (
    <h2 className={`text-lg font-semibold text-gray-900 ${className}`}>
      {children}
    </h2>
  );
}

interface DialogDescriptionProps {
  children: ReactNode;
  className?: string;
}

export function DialogDescription({ children, className = '' }: DialogDescriptionProps) {
  return (
    <p className={`text-sm text-gray-600 mt-1 ${className}`}>
      {children}
    </p>
  );
}

interface DialogFooterProps {
  children: ReactNode;
  className?: string;
}

export function DialogFooter({ children, className = '' }: DialogFooterProps) {
  return (
    <div className={`flex items-center justify-end gap-2 mt-6 ${className}`}>
      {children}
    </div>
  );
}
