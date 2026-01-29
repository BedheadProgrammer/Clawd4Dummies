import { memo } from 'react';
import { ShieldCheck } from 'lucide-react';

export const Footer = memo(function Footer() {
  return (
    <footer className="bg-elevated border-t border-text-secondary/20 mt-auto">
      <div className="container mx-auto px-4 py-4 max-w-6xl">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Privacy Notice */}
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <ShieldCheck className="w-4 h-4 text-low" />
            <span>
              This tool ONLY scans your local computer. No data is sent externally.
            </span>
          </div>

          {/* Version */}
          <div className="text-sm text-text-secondary">
            Version 1.0.0
          </div>
        </div>
      </div>
    </footer>
  );
});
