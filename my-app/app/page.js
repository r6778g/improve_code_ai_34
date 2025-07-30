'use client';
import * as React from 'react';
import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';

export default function Page() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0] ?? null;
    setFile(selectedFile);
    if (selectedFile) {
      setMessage(''); 
    }
  };

  const handleMessageChange = (e) => {
    const msg = e.target.value;
    setMessage(msg);
    if (msg.trim()) {
      setFile(null); 
    }
  };

  const handleSubmit = () => {
    if (file) {
      console.log('Submitted file:', file);
    } else if (message.trim()) {
      console.log('Submitted message:', message);
    } else {
      alert('Please fill either the file or message input.');
    }

   
    setFile(null);
    setMessage('');
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 border rounded-xl shadow-md space-y-4">
      <h2 className="text-2xl font-semibold text-center">IMPROVE CODE AI</h2>

      <Input
        type="file"
        disabled={!!message.trim()}
        onChange={handleFileChange}
      />

      <Textarea
        value={message}
        disabled={!!file}
        onChange={handleMessageChange}
        placeholder="Your message"
      />

      <Button onClick={handleSubmit}>Submit</Button>
    </div>
  );
}
