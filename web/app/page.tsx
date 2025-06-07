'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

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
        // Note: In a real implementation, we would need to poll for task completion
        // and refresh the lecture list when the lecture is ready
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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          Lecturia - 講義作成システム
        </h1>

        {/* 新しい講義を作成 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            新しい講義を作成
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-1">
                講義のテーマ <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例: 機械学習の基礎"
                required
              />
            </div>
            <div>
              <label htmlFor="detail" className="block text-sm font-medium text-gray-700 mb-1">
                詳細説明
              </label>
              <textarea
                id="detail"
                value={detail}
                onChange={(e) => setDetail(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="講義の詳細内容を入力してください..."
              />
            </div>
            <button
              type="submit"
              disabled={!topic.trim() || isSubmitting}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isSubmitting ? '作成中...' : '講義を作成'}
            </button>
          </form>
        </div>

        {/* 既存の講義一覧 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            作成済みの講義
          </h2>
          {isLoading ? (
            <p className="text-gray-500 text-center py-8">
              講義一覧を読み込み中...
            </p>
          ) : existingLectures.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              まだ講義が作成されていません。
            </p>
          ) : (
            <div className="space-y-3">
              {existingLectures.map((lecture) => (
                <div
                  key={lecture.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => handleLectureClick(lecture.id)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-gray-900">{lecture.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">{lecture.topic}</p>
                    </div>
                    <span className="text-sm text-gray-500">{lecture.created_at}</span>
                  </div>
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      再生可能
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}