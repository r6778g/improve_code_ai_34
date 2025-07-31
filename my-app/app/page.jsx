'use client';

import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

export default function Page() {
  const [file, setFile] = useState(null);
  const [fileText, setFileText] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const reader = new FileReader();
      reader.onload = () => {
        setFileText(reader.result);
        setFile(selectedFile);
        setMessage('');
      };
      reader.onerror = () => {
        alert("Failed to read file.");
      };
      reader.readAsText(selectedFile);
    }
  };

  const handleMessageChange = (e) => {
    setMessage(e.target.value);
    setFile(null);
    setFileText('');
  };

  const handleSubmit = async () => {
    const finalText = message.trim() || fileText.trim();

    if (!finalText) {
      alert("Please provide some text or upload a file.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("text", finalText);

      const res = await fetch("http://localhost:8000/process/", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Request failed");

      const data = await res.json();


      const query = new URLSearchParams({
        input: data.input,
        input_type: data.input_type,
        model_response: data.model_response,
      });

      router.push(`/result?${query.toString()}`);
    } catch (err) {
      alert("Something went wrong.");
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto mt-10 p-6 border rounded-xl shadow-md space-y-4">
      <h2 className="text-3xl font-bold text-center">IMPROVE CODE AI</h2>

      <Input
        type="file"
        onChange={handleFileChange}
        className="file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:bg-blue-50 file:text-blue-700"
      />

      <Textarea
        value={message}
        onChange={handleMessageChange}
        placeholder="Paste your code or type a message..."
        className="h-32"
      />

      <Button onClick={handleSubmit} disabled={loading} className="w-full">
        {loading ? 'Submitting...' : 'Submit'}
      </Button>
    </div>
  );
}
