'use client';

import { useRouter } from 'next/navigation';
import { useRef } from 'react';
import { Header } from '../components/Header';
import { BackgroundDecorations } from '../components/BackgroundDecorations';
import { LectureForm } from '../components/LectureForm';
import { LectureList } from '../components/LectureList';
import { GlobalStyles } from '../components/GlobalStyles';

export default function HomePage() {
  const router = useRouter();
  const lectureListRef = useRef<{ refreshLectures: () => void } | null>(null);

  const handleLectureClick = (lectureId: string) => {
    router.push(`/lectures/${lectureId}`);
  };

  const handleTaskComplete = () => {
    // Refresh the lecture list when a task completes
    if (lectureListRef.current) {
      lectureListRef.current.refreshLectures();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <BackgroundDecorations />
      
      <div className="relative max-w-6xl mx-auto px-4 py-12">
        <Header />
        
        <div className="grid lg:grid-cols-5 gap-8">
          <LectureForm onTaskComplete={handleTaskComplete} />
          <LectureList ref={lectureListRef} onLectureClick={handleLectureClick} />
        </div>
      </div>

      <GlobalStyles />
    </div>
  );
}