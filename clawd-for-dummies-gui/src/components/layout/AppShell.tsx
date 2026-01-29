import { memo, ReactNode } from 'react';
import { Header } from './Header';
import { Footer } from './Footer';

interface AppShellProps {
  children: ReactNode;
}

export const AppShell = memo(function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-space-black text-text-primary font-body flex flex-col">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-6 max-w-6xl">
        {children}
      </main>
      <Footer />
    </div>
  );
});
