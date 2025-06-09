'use client';

import { useRouter } from 'next/navigation';
import { Header } from '../components/Header';
import { BackgroundDecorations } from '../components/BackgroundDecorations';
import { LectureForm } from '../components/LectureForm';
import { LectureList } from '../components/LectureList';
import { GlobalStyles } from '../components/GlobalStyles';

export default function HomePage() {
  const router = useRouter();

  const handleLectureClick = (lectureId: string) => {
    router.push(`/lectures/${lectureId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <BackgroundDecorations />
      
      <div className="relative max-w-6xl mx-auto px-4 py-12">
        <Header />
        
        <div className="grid lg:grid-cols-5 gap-8">
          <LectureForm />
          <LectureList onLectureClick={handleLectureClick} />
        </div>
      </div>

      <GlobalStyles />
    </div>
  );
}