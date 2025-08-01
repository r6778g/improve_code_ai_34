'use client';

import { useSearchParams } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css'; // ✅ pick theme

export default function ResultPage() {
  const searchParams = useSearchParams();
  const modelResponse = searchParams.get("model_response");

  return (
    <div className="w-full min-h-screen px-6 py-10 bg-gray-50">
      <h1 className="text-3xl font-bold text-center mb-6">AI Code Review Output</h1>
      <p className="text-center text-gray-500 mb-10">
        Input type: <strong>{}</strong>
      </p>

      <div className="flex flex-col gap-6">
        <h2 className="text-xl font-semibold mb-2">Model Response</h2>
        <div className="bg-black text-green-200 font-mono text-sm p-4 rounded-lg overflow-auto max-h-[70vh] whitespace-pre-wrap">
          <ReactMarkdown
            rehypePlugins={[rehypeHighlight]}
            components={{
              code({ node, inline, className, children, ...props }) {
                return inline ? (
                  <code className="bg-gray-800 px-1 py-0.5 rounded text-green-300" {...props}>
                    {children}
                  </code>
                ) : (
                  <pre className="p-3 rounded overflow-x-auto">
                    <code className={`${className} text-sm`} {...props}>
                      {children}
                    </code>
                  </pre>
                );
              },
              h1({ children }) {
                return <h1 className="text-2xl font-bold my-4">{children}</h1>;
              },
              h2({ children }) {
                return <h2 className="text-xl font-semibold my-3">{children}</h2>;
              },
              p({ children }) {
                return <p className="mb-2">{children}</p>;
              },
              li({ children }) {
                return <li className="list-disc list-inside">{children}</li>;
              }
            }}
          >
            {modelResponse || "*No response found.*"}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
