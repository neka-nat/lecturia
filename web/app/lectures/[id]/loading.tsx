'use client';

import { Loader2 } from 'lucide-react';

export default function LoadingLecture() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <Loader2 className="w-10 h-10 text-indigo-600 animate-spin mb-4" />
      <p className="text-slate-600 font-medium">講義を読み込み中...</p>
    </div>
  );
}
