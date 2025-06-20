import { Play, Calendar, ArrowRight, Trash2, RefreshCw, AlertCircle, Loader2 } from 'lucide-react';
import { Lecture } from '../hooks/useLectures';

interface LectureCardProps {
  lecture: Lecture;
  index: number;
  onLectureClick: (lectureId: string) => void;
  onDeleteLecture: (lectureId: string, lectureTitle: string) => void;
  onRegenerateLecture?: (lectureId: string) => void;
  isRegenerating?: boolean;
}

export function LectureCard({ lecture, index, onLectureClick, onDeleteLecture, onRegenerateLecture, isRegenerating }: LectureCardProps) {
  const getStatusInfo = () => {
    switch (lecture.status) {
      case 'failed':
        return {
          icon: <AlertCircle className="w-4 h-4" />,
          label: '生成失敗',
          color: 'from-red-100 to-red-100 text-red-700 border-red-200',
          bgColor: 'bg-red-500',
          canPlay: false,
        };
      case 'running':
        return {
          icon: <Loader2 className="w-4 h-4 animate-spin" />,
          label: '生成中',
          color: 'from-blue-100 to-blue-100 text-blue-700 border-blue-200',
          bgColor: 'bg-blue-500',
          canPlay: false,
        };
      case 'pending':
        return {
          icon: <Loader2 className="w-4 h-4 animate-spin" />,
          label: '待機中',
          color: 'from-yellow-100 to-yellow-100 text-yellow-700 border-yellow-200',
          bgColor: 'bg-yellow-500',
          canPlay: false,
        };
      default: // completed
        return {
          icon: <div className="w-2 h-2 rounded-full bg-emerald-500"></div>,
          label: '再生可能',
          color: 'from-emerald-100 to-teal-100 text-emerald-700 border-emerald-200',
          bgColor: 'bg-emerald-500',
          canPlay: true,
        };
    }
  };

  const statusInfo = getStatusInfo();
  return (
    <div
      className={`group relative overflow-hidden bg-gradient-to-r from-white to-slate-50 border-2 border-slate-100 rounded-xl p-6 hover:border-indigo-200 hover:shadow-xl transition-all duration-300 ${
        statusInfo.canPlay ? 'cursor-pointer hover:scale-[1.02]' : 'cursor-default'
      }`}
      onClick={() => statusInfo.canPlay && onLectureClick(lecture.id)}
      style={{
        animationDelay: `${index * 100}ms`,
        animation: 'slideInUp 0.6s ease-out forwards'
      }}
    >
      <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      <div className="relative flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <div className={`w-8 h-8 rounded-lg ${statusInfo.canPlay ? 'bg-gradient-to-br from-indigo-500 to-purple-600' : statusInfo.bgColor} flex items-center justify-center flex-shrink-0`}>
              {statusInfo.canPlay ? <Play className="w-4 h-4 text-white" /> : <div className="text-white">{statusInfo.icon}</div>}
            </div>
            <h3 className="font-bold text-slate-800 text-lg truncate group-hover:text-indigo-600 transition-colors">
              {lecture.topic}
            </h3>
          </div>
          <p className="text-slate-600 mb-3 line-clamp-2">
            {lecture.detail}
          </p>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1 text-sm text-slate-500">
              <Calendar className="w-4 h-4" />
              {lecture.created_at}
            </div>
            <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r ${statusInfo.color}`}>
              {statusInfo.icon}
              {statusInfo.label}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0 ml-4">
          {lecture.status === 'failed' && onRegenerateLecture && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (!isRegenerating) {
                  onRegenerateLecture(lecture.id);
                }
              }}
              disabled={isRegenerating}
              className={`p-2 rounded-lg transition-all duration-200 ${
                isRegenerating 
                  ? 'text-blue-500 bg-blue-50 cursor-not-allowed opacity-100' 
                  : 'text-slate-400 hover:text-blue-500 hover:bg-blue-50 opacity-0 group-hover:opacity-100'
              }`}
              title={isRegenerating ? '再生成中...' : '講義を再生成'}
            >
              {isRegenerating ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4" />
              )}
            </button>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDeleteLecture(lecture.id, lecture.topic);
            }}
            className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100"
            title="講義を削除"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          {statusInfo.canPlay && (
            <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-indigo-500 group-hover:translate-x-1 transition-all duration-300" />
          )}
        </div>
      </div>
    </div>
  );
}