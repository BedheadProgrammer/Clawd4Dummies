import { Component, ReactNode, ErrorInfo } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  retryKey: number;
}

/**
 * Error Boundary component that catches JavaScript errors in child components,
 * logs them, and displays a fallback UI instead of a blank page.
 * 
 * This prevents the entire app from crashing when a component throws an error.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryKey: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render shows the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Only log detailed errors in development mode
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }
    this.setState({ errorInfo });
  }

  handleRetry = (): void => {
    // Increment retryKey to force remounting of children components
    this.setState((prevState) => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryKey: prevState.retryKey + 1,
    }));
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI with proper ARIA attributes for accessibility
      return (
        <div 
          className="flex flex-col items-center justify-center p-8 bg-elevated rounded-xl border border-critical/30"
          role="alert"
          aria-live="assertive"
        >
          <div className="p-4 bg-critical/10 rounded-full mb-4" aria-hidden="true">
            <AlertTriangle className="w-8 h-8 text-critical" />
          </div>
          <h2 className="text-xl font-semibold text-text-primary mb-2">
            Something went wrong
          </h2>
          <p className="text-text-secondary text-center mb-4 max-w-md">
            An unexpected error occurred. Please try again or restart the application.
          </p>
          {this.state.error && (
            <details className="w-full max-w-md mb-4">
              <summary className="text-sm text-text-secondary cursor-pointer hover:text-text-primary">
                Show error details
              </summary>
              <pre className="mt-2 p-3 bg-space-black rounded-lg text-xs text-critical overflow-auto max-h-32">
                {this.state.error.message}
                {this.state.errorInfo?.componentStack && (
                  <>
                    {'\n\nComponent Stack:'}
                    {this.state.errorInfo.componentStack}
                  </>
                )}
              </pre>
            </details>
          )}
          <button
            onClick={this.handleRetry}
            className="inline-flex items-center gap-2 px-4 py-2 bg-action-blue text-white rounded-lg hover:bg-action-blue/90 transition-colors"
            aria-label="Try again to reload the component"
          >
            <RefreshCw className="w-4 h-4" aria-hidden="true" />
            Try Again
          </button>
        </div>
      );
    }

    // Use key to force remount on retry
    return <div key={this.state.retryKey}>{this.props.children}</div>;
  }
}
