'use client';

import { useSearchParams } from 'next/navigation';
import { Suspense, useState, memo } from 'react';
import dynamic from 'next/dynamic';
import 'highlight.js/styles/github-dark.css';

// Lazy load ReactMarkdown for better performance
const ReactMarkdown = dynamic(() => import('react-markdown'), {
  loading: () => (
    <div className="animate-pulse">
      <div className="bg-gray-300 h-64 rounded-lg mb-4"></div>
      <div className="bg-gray-200 h-8 rounded mb-2"></div>
      <div className="bg-gray-200 h-8 rounded w-3/4"></div>
    </div>
  ),
  ssr: false
});

const rehypeHighlight = dynamic(() => import('rehype-highlight'), {
  ssr: false
});

// Copy button component
const CopyButton = memo(({ text }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <button
      onClick={copyToClipboard}
      className="absolute top-2 right-2 px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-xs rounded transition-colors duration-200"
      aria-label="Copy to clipboard"
    >
      {copied ? '✓ Copied' : '📋 Copy'}
    </button>
  );
});

CopyButton.displayName = 'CopyButton';

// Main content component
const ResultContent = memo(() => {
  const searchParams = useSearchParams();
  const modelResponse = decodeURIComponent(searchParams.get("model_response") || "");
  const inputType = searchParams.get("input_type");

  // Error state - no model response
  if (!modelResponse || modelResponse === "null") {
    return (
      <div className="w-full min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto px-6">
          <div className="mb-6">
            <div className="w-16 h-16 mx-auto mb-4 bg-yellow-100 rounded-full flex items-center justify-center">
              <span className="text-2xl">⚠️</span>
            </div>
            <h2 className="text-2xl font-semibold mb-3 text-gray-900">No Results Found</h2>
            <p className="text-gray-600 mb-6">
              We couldn't find any code review results. Please go back and submit your code for analysis.
            </p>
          </div>
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200"
          >
            ← Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen px-4 sm:px-6 lg:px-8 py-10 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Code Review Results
          </h1>
        </header>

        {/* Main Content */}
        <main>
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gray-800 px-6 py-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white flex items-center">
                <span className="mr-2">📄</span>
                Analysis Report
              </h2>
              <CopyButton text={modelResponse} />
            </div>
            
            <div className="p-6">
              <div className="prose prose-lg max-w-none">
                <ReactMarkdown
                  rehypePlugins={[rehypeHighlight]}
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      const language = match ? match[1] : '';
                      
                      return inline ? (
                        <code className="bg-gray-100 text-red-600 px-2 py-1 rounded text-sm font-mono" {...props}>
                          {children}
                        </code>
                      ) : (
                        <div className="relative my-4">
                          {language && (
                            <div className="absolute top-3 right-3 text-xs text-gray-400 uppercase font-semibold bg-gray-800 px-2 py-1 rounded">
                              {language}
                            </div>
                          )}
                          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto border border-gray-200">
                            <code className={className} {...props}>
                              {children}
                            </code>
                          </pre>
                        </div>
                      );
                    },
                    h1({ children }) {
                      return (
                        <h1 className="text-3xl font-bold my-6 text-gray-900 border-b border-gray-200 pb-2">
                          {children}
                        </h1>
                      );
                    },
                    h2({ children }) {
                      return (
                        <h2 className="text-2xl font-semibold my-5 text-gray-800 flex items-center">
                          <span className="w-1 h-6 bg-blue-500 mr-3 rounded"></span>
                          {children}
                        </h2>
                      );
                    },
                    h3({ children }) {
                      return (
                        <h3 className="text-xl font-medium my-4 text-gray-700">
                          {children}
                        </h3>
                      );
                    },
                    p({ children }) {
                      return <p className="mb-4 text-gray-700 leading-relaxed">{children}</p>;
                    },
                    ul({ children }) {
                      return <ul className="mb-4 space-y-2">{children}</ul>;
                    },
                    ol({ children }) {
                      return <ol className="mb-4 space-y-2">{children}</ol>;
                    },
                    li({ children }) {
                      return (
                        <li className="flex items-start">
                          <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                          <span className="text-gray-700">{children}</span>
                        </li>
                      );
                    },
                    blockquote({ children }) {
                      return (
                        <blockquote className="border-l-4 border-blue-500 pl-4 py-2 my-4 bg-blue-50 text-gray-700 italic">
                          {children}
                        </blockquote>
                      );
                    },
                    table({ children }) {
                      return (
                        <div className="overflow-x-auto my-4">
                          <table className="min-w-full border border-gray-200 rounded-lg">
                            {children}
                          </table>
                        </div>
                      );
                    },
                    thead({ children }) {
                      return <thead className="bg-gray-50">{children}</thead>;
                    },
                    th({ children }) {
                      return (
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b border-gray-200">
                          {children}
                        </th>
                      );
                    },
                    td({ children }) {
                      return (
                        <td className="px-4 py-3 text-sm text-gray-700 border-b border-gray-200">
                          {children}
                        </td>
                      );
                    }
                  }}
                >
                  {modelResponse}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        </main>
          
        {/* Footer Actions */}
        <footer className="mt-10 text-center">
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={() => window.history.back()}
              className="inline-flex items-center px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded-lg transition-colors duration-200"
            >
              ← Back to Review
            </button>
            <button
              onClick={() => window.print()}
              className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200"
            >
              🖨️ Print Report
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
});

ResultContent.displayName = 'ResultContent';

// Main component with Suspense wrapper
export default function ResultPage() {
  return (
    <Suspense 
      fallback={
        <div className="w-full min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading results...</p>
          </div>
        </div>
      }
    >
      <ResultContent />
    </Suspense>
  );
}