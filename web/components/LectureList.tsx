import { BookOpen, Loader2 } from 'lucide-react';
import { useLectures } from '../hooks/useLectures';
import { LectureCard } from './LectureCard';

interface LectureListProps {
  onLectureClick: (lectureId: string) => void;
}

export function LectureList({ onLectureClick }: LectureListProps) {
  const { lectures, isLoading, deleteLecture } = useLectures();

  return (
    <div className="lg:col-span-3">
      <div className="bg-white/80 backdrop-blur-xl rounded-2xl p-8 border border-white/50 shadow-2xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
            作成済みの講義
          </h2>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <Loader2 className="w-8 h-8 text-indigo-500 animate-spin mb-4" />
            <p className="text-slate-500 font-medium">
              講義一覧を読み込み中...
            </p>
          </div>
        ) : lectures.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center mx-auto mb-4">
              <BookOpen className="w-8 h-8 text-slate-400" />
            </div>
            <p className="text-slate-500 font-medium text-lg mb-2">
              まだ講義が作成されていません
            </p>
            <p className="text-slate-400 text-sm">
              左のフォームから新しい講義を作成してみましょう
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {lectures.map((lecture, index) => (
              <LectureCard
                key={lecture.id}
                lecture={lecture}
                index={index}
                onLectureClick={onLectureClick}
                onDeleteLecture={deleteLecture}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}