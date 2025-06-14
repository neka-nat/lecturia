'use client';

import { useRouter } from 'next/navigation';
import { useRef, useState } from 'react';
import { Header } from '../components/Header';
import { BackgroundDecorations } from '../components/BackgroundDecorations';
import { LectureForm } from '../components/LectureForm';
import { LectureList } from '../components/LectureList';
import { GlobalStyles } from '../components/GlobalStyles';
import { useTaskStatus } from '../hooks/useTaskStatus';

export default function HomePage() {
  const router = useRouter();
  const lectureListRef = useRef<{ refreshLectures: () => void } | null>(null);
  const [regeneratingTasks, setRegeneratingTasks] = useState<Set<string>>(new Set());

  const handleLectureClick = (lectureId: string) => {
    router.push(`/lectures/${lectureId}`);
  };

  const handleTaskComplete = () => {
    // Refresh the lecture list when a task completes
    if (lectureListRef.current) {
      lectureListRef.current.refreshLectures();
    }
  };

  const handleRegenerateLecture = async (lectureId: string): Promise<string | null> => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}/api/lectures/${lectureId}/regenerate`,
        {
          method: 'POST',
        }
      );

      if (response.ok) {
        const result = await response.json();
        const taskId = result.task_id || lectureId;
        
        // Add to regenerating tasks
        setRegeneratingTasks(prev => new Set(prev).add(taskId));
        
        // Store the task ID in localStorage for persistence
        const currentTasks = JSON.parse(localStorage.getItem('regenerating_tasks') || '[]');
        const updatedTasks = [...currentTasks, taskId];
        localStorage.setItem('regenerating_tasks', JSON.stringify(updatedTasks));
        
        return taskId;
      } else {
        alert('講義の再生成に失敗しました。');
        return null;
      }
    } catch (error) {
      console.error('Error regenerating lecture:', error);
      alert('講義再生成中にエラーが発生しました。');
      return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <BackgroundDecorations />
      
      <div className="relative max-w-6xl mx-auto px-4 py-12">
        <Header />
        
        <div className="grid lg:grid-cols-5 gap-8">
          <LectureForm onTaskComplete={handleTaskComplete} />
          <LectureList 
            ref={lectureListRef} 
            onLectureClick={handleLectureClick}
            onRegenerateLecture={handleRegenerateLecture}
          />
        </div>
      </div>

      <GlobalStyles />
    </div>
  );
}