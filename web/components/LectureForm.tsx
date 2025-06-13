import { Plus, Sparkles, Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';
import { useLectureForm } from '../hooks/useLectureForm';
import { useTaskStatus } from '../hooks/useTaskStatus';
import { CharacterSelector } from './CharacterSelector';

interface LectureFormProps {
  onTaskComplete?: () => void;
}

export function LectureForm({ onTaskComplete }: LectureFormProps) {
  const {
    topic,
    setTopic,
    detail,
    setDetail,
    selectedCharacter,
    setSelectedCharacter,
    isSubmitting,
    createLecture,
    currentTaskId,
    clearTaskId,
  } = useLectureForm();

  const { taskStatus, isLoading: isStatusLoading, error: statusError, getStatusDisplay } = useTaskStatus(currentTaskId, onTaskComplete);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createLecture();
  };

  return (
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
                  className="w-full px-4 py-3 bg-white/70 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all duration-300"
                  placeholder="例: 大化の改新について、AWSの基礎、など"
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
                className="w-full px-4 py-3 bg-white/70 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all duration-300 resize-none"
                placeholder="講義の詳細内容を入力してください..."
              />
            </div>

            <CharacterSelector
              selectedCharacter={selectedCharacter}
              onCharacterChange={setSelectedCharacter}
            />
            
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

          {/* Task Status Display */}
          {currentTaskId && (
            <div className="mt-6 p-4 bg-slate-50/80 rounded-xl border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-slate-700">タスク状況</h3>
                <button
                  onClick={clearTaskId}
                  className="text-xs text-slate-400 hover:text-slate-600 transition-colors"
                >
                  閉じる
                </button>
              </div>
              
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs text-slate-500">タスクID:</span>
                <code className="text-xs bg-slate-200 px-2 py-1 rounded font-mono">{currentTaskId}</code>
              </div>

              {statusError ? (
                <div className="flex items-center gap-2 text-red-600">
                  <XCircle className="w-4 h-4" />
                  <span className="text-sm">{statusError}</span>
                </div>
              ) : isStatusLoading ? (
                <div className="flex items-center gap-2 text-slate-500">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">ステータス確認中...</span>
                </div>
              ) : taskStatus ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    {taskStatus.status === 'completed' && <CheckCircle className="w-4 h-4 text-green-500" />}
                    {taskStatus.status === 'failed' && <XCircle className="w-4 h-4 text-red-500" />}
                    {(taskStatus.status === 'pending' || taskStatus.status === 'running') && <Clock className="w-4 h-4 text-blue-500" />}
                    {taskStatus.status === 'not_started' && <Clock className="w-4 h-4 text-gray-500" />}
                    <span className={`text-sm font-medium ${getStatusDisplay(taskStatus.status).color}`}>
                      {getStatusDisplay(taskStatus.status).text}
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500">
                        {taskStatus.current_phase || '待機中'}
                      </span>
                      <span className="text-slate-500">
                        {taskStatus.progress_percentage}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full transition-all duration-300 ease-out"
                        style={{ width: `${taskStatus.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  {taskStatus.error && (
                    <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                      エラー: {taskStatus.error}
                    </div>
                  )}
                  
                  <div className="text-xs text-slate-400">
                    最終更新: {new Date(taskStatus.updated_at).toLocaleString('ja-JP')}
                  </div>

                  {taskStatus.status === 'completed' && (
                    <div className="text-xs text-green-600 bg-green-50 p-2 rounded">
                      講義の作成が完了しました。講義一覧に追加されました。
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}