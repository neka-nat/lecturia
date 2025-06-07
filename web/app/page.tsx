'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { BookOpen, Play, Calendar, Sparkles, Loader2, Plus, ArrowRight } from 'lucide-react';

interface Lecture {
  id: string;
  title: string;
  topic: string;
  created_at: string;
}

export default function HomePage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [topic, setTopic] = useState('');
  const [detail, setDetail] = useState('');
  const [existingLectures, setExistingLectures] = useState<Lecture[]>([]);

  // Fetch existing lectures on component mount
  useEffect(() => {
    const fetchLectures = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}/api/lectures`
        );
        if (response.ok) {
          const lectures = await response.json();
          setExistingLectures(lectures);
        }
      } catch (error) {
        console.error('Error fetching lectures:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLectures();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsSubmitting(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}/api/create-lecture`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            topic: topic.trim(),
            detail: detail.trim() || null,
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        alert(`講義作成タスクが開始されました。タスクID: ${result.task_id}`);
        setTopic('');
        setDetail('');
      } else {
        alert('講義作成に失敗しました。');
      }
    } catch (error) {
      console.error('Error creating lecture:', error);
      alert('講義作成中にエラーが発生しました。');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLectureClick = (lectureId: string) => {
    router.push(`/lectures/${lectureId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-gradient-to-br from-purple-400/20 to-pink-400/20 blur-3xl"></div>
        <div className="absolute top-40 -left-40 w-96 h-96 rounded-full bg-gradient-to-br from-blue-400/20 to-cyan-400/20 blur-3xl"></div>
        <div className="absolute bottom-40 right-40 w-64 h-64 rounded-full bg-gradient-to-br from-indigo-400/20 to-purple-400/20 blur-3xl"></div>
      </div>

      <div className="relative max-w-6xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-flex items-center gap-3 mb-6">
            <div className="relative">
              <BookOpen className="w-12 h-12 text-indigo-600" />
              <Sparkles className="w-5 h-5 text-yellow-500 absolute -top-1 -right-1 animate-pulse" />
            </div>
            <h1 className="text-5xl font-black bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Lecturia
            </h1>
          </div>
          <p className="text-xl text-slate-600 font-medium">
            AI で作る、あなただけの学び方
          </p>
          <div className="w-24 h-1 bg-gradient-to-r from-indigo-500 to-purple-500 mx-auto mt-4 rounded-full"></div>
        </div>

        <div className="grid lg:grid-cols-5 gap-8">
          {/* Create new lecture form */}
          <div className="lg:col-span-2">
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl blur-xl opacity-25 group-hover:opacity-40 transition-opacity duration-500"></div>
              <div className="relative bg-white/80 backdrop-blur-xl rounded-2xl p-8 border border-white/50 shadow-2xl">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                    <Plus className="w-5 h-5 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                    新しい講義を作成
                  </h2>
                </div>
                
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="space-y-2">
                    <label htmlFor="topic" className="block text-sm font-semibold text-slate-700">
                      講義のテーマ <span className="text-rose-500">*</span>
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        id="topic"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        className="w-full px-4 py-3 bg-white/70 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all duration-300 placeholder-slate-400"
                        placeholder="例: 機械学習の基礎"
                        required
                      />
                      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-indigo-500/5 to-purple-500/5 pointer-events-none opacity-0 focus-within:opacity-100 transition-opacity duration-300"></div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <label htmlFor="detail" className="block text-sm font-semibold text-slate-700">
                      詳細説明
                    </label>
                    <textarea
                      id="detail"
                      value={detail}
                      onChange={(e) => setDetail(e.target.value)}
                      rows={4}
                      className="w-full px-4 py-3 bg-white/70 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all duration-300 placeholder-slate-400 resize-none"
                      placeholder="講義の詳細内容を入力してください..."
                    />
                  </div>
                  
                  <button
                    type="submit"
                    disabled={!topic.trim() || isSubmitting}
                    className="w-full group relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white py-4 px-6 rounded-xl font-semibold transition-all duration-300 hover:scale-105 hover:shadow-2xl focus:outline-none focus:ring-4 focus:ring-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    <div className="relative flex items-center justify-center gap-2">
                      {isSubmitting ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <Sparkles className="w-5 h-5" />
                      )}
                      {isSubmitting ? '作成中...' : '講義を作成'}
                    </div>
                  </button>
                </form>
              </div>
            </div>
          </div>

          {/* Existing lectures list */}
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
              ) : existingLectures.length === 0 ? (
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
                  {existingLectures.map((lecture, index) => (
                    <div
                      key={lecture.id}
                      className="group relative overflow-hidden bg-gradient-to-r from-white to-slate-50 border-2 border-slate-100 rounded-xl p-6 hover:border-indigo-200 hover:shadow-xl cursor-pointer transition-all duration-300 hover:scale-[1.02]"
                      onClick={() => handleLectureClick(lecture.id)}
                      style={{
                        animationDelay: `${index * 100}ms`,
                        animation: 'slideInUp 0.6s ease-out forwards'
                      }}
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                      <div className="relative flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                              <Play className="w-4 h-4 text-white" />
                            </div>
                            <h3 className="font-bold text-slate-800 text-lg truncate group-hover:text-indigo-600 transition-colors">
                              {lecture.title}
                            </h3>
                          </div>
                          <p className="text-slate-600 mb-3 line-clamp-2">
                            {lecture.topic}
                          </p>
                          <div className="flex items-center gap-4">
                            <div className="flex items-center gap-1 text-sm text-slate-500">
                              <Calendar className="w-4 h-4" />
                              {lecture.created_at}
                            </div>
                            <div className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-emerald-100 to-teal-100 text-emerald-700 border border-emerald-200">
                              <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                              再生可能
                            </div>
                          </div>
                        </div>
                        <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-indigo-500 group-hover:translate-x-1 transition-all duration-300 flex-shrink-0 ml-4" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <style jsx global>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fade-in {
          animation: fade-in 0.8s ease-out;
        }
        
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </div>
  );
}