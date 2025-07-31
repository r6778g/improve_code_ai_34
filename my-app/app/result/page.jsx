'use client';

import { useSearchParams } from 'next/navigation';

export default function ResultPage() {
  const searchParams = useSearchParams();

  const inputType = searchParams.get("input_type");
  const input = searchParams.get("input");
  const modelResponse = searchParams.get("model_response");

  return (
    <div className="w-full min-h-screen px-6 py-10 bg-gray-50">
      <h1 className="text-3xl font-bold text-center mb-6">AI Code Review Output</h1>
      <p className="text-center text-gray-500 mb-10">Input type: <strong>{inputType}</strong></p>

      <div className="flex flex-col md:flex-row gap-6">
        
        <div className="w-full md:w-1/2 border rounded-xl shadow p-4 bg-white">
          <h2 className="text-xl font-semibold mb-3">Original code</h2>
          <pre className="whitespace-pre-wrap text-sm bg-gray-100 p-3 rounded h-[70vh] overflow-auto">
            {input}
          </pre>
        </div>

    
        <div className="w-full md:w-1/2 border rounded-xl shadow p-4 bg-white">
          <h2 className="text-xl font-semibold mb-3">Model Response</h2>
          <pre className="whitespace-pre-wrap text-sm bg-gray-100 p-3 rounded h-[70vh] overflow-auto">
            {modelResponse}
          </pre>
        </div>
      </div>
    </div>
  );
}
