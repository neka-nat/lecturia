'use client';

import { Plus, Sparkles, Loader2 } from 'lucide-react';
import { CharacterSelector } from './CharacterSelector';
import { useLectureForm } from '../hooks/useLectureForm';
import { Lecture } from '../hooks/useLectures';

interface LectureFormProps {
  onLectureCreated?: (l: Lecture) => void;
}

export function LectureForm({ onLectureCreated }: LectureFormProps) {
  const {
    topic,
    setTopic,
    detail,
    setDetail,
    selectedCharacter,
    setSelectedCharacter,
    isSubmitting,
    createLecture,
  } = useLectureForm();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await createLecture();
    if (!result) return;

    onLectureCreated?.({
      id: result.taskId,
      topic,
      detail,
      created_at: new Date().toISOString(),
      status: 'pending',
    });
  };

  return (
    <div className="lg:col-span-2">
      <div className="group relative">
        {/* 背景グラデーションの飾り */}
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl blur-xl opacity-25 group-hover:opacity-40 transition-opacity duration-500" />
        
        <div className="relative bg-white/80 backdrop-blur-xl rounded-2xl p-8 border border-white/50 shadow-2xl">
          {/* ヘッダー */}
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Plus className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
              新しい講義を作成
            </h2>
          </div>

          {/* フォーム本体 */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* テーマ入力 */}
            <div className="space-y-2">
              <label htmlFor="topic" className="block text-sm font-semibold text-slate-700">
                講義のテーマ <span className="text-rose-500">*</span>
              </label>
              <div className="relative">
                <input
                  id="topic"
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  required
                  placeholder="例: 大化の改新について、AWSの基礎、など"
                  className="w-full px-4 py-3 bg-white/70 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all duration-300"
                />
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-indigo-500/5 to-purple-500/5 pointer-events-none opacity-0 focus-within:opacity-100 transition-opacity duration-300" />
              </div>
            </div>

            {/* 詳細説明 */}
            <div className="space-y-2">
              <label htmlFor="detail" className="block text-sm font-semibold text-slate-700">
                詳細説明
              </label>
              <textarea
                id="detail"
                rows={4}
                value={detail}
                onChange={(e) => setDetail(e.target.value)}
                placeholder="講義の詳細内容を入力してください..."
                className="w-full px-4 py-3 bg-white/70 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all duration-300 resize-none"
              />
            </div>

            {/* キャラクター選択 */}
            <CharacterSelector
              selectedCharacter={selectedCharacter}
              onCharacterChange={setSelectedCharacter}
            />

            {/* 送信ボタン */}
            <button
              type="submit"
              disabled={!topic.trim() || isSubmitting}
              className="w-full group relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white py-4 px-6 rounded-xl font-semibold transition-all duration-300 hover:scale-105 hover:shadow-2xl focus:outline-none focus:ring-4 focus:ring-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="relative flex items-center justify-center gap-2">
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    作成中...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    講義を作成
                  </>
                )}
              </div>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
