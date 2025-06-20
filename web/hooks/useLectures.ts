import { useState, useEffect, useCallback, useRef } from 'react';

export interface Lecture {
  id: string;
  topic: string;
  detail: string | null;
  created_at: string;
  status: string; // "completed", "failed", "running", "pending"
  progress_percentage?: number;
  current_phase?: string;
}

export function useLectures() {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  /** 多重リクエスト防止フラグ */
  const isFetching = useRef(false);

  const fetchLectures = useCallback(async () => {
    if (isFetching.current) return;
    isFetching.current = true;
    try {
      const r = await fetch(
        `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}/api/lectures`
      );
      if (r.ok) setLectures(await r.json());
    } finally {
      isFetching.current = false;
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLectures();
  }, [fetchLectures]);

  useEffect(() => {
    const hasRunning = lectures.some(l =>
      l.status === 'running' || l.status === 'pending'
    );
    if (!hasRunning) return;

    const id = setInterval(fetchLectures, 5000);
    return () => clearInterval(id);
  }, [lectures, fetchLectures]);

  const deleteLecture = async (lectureId: string, lectureTitle: string): Promise<boolean> => {
    if (!confirm(`「${lectureTitle}」を削除しますか？この操作は取り消せません。`)) {
      return false;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}/api/lectures/${lectureId}`,
        {
          method: 'DELETE',
        }
      );

      if (response.ok) {
        setLectures(prev => prev.filter(lecture => lecture.id !== lectureId));
        alert('講義が削除されました。');
        return true;
      } else {
        alert('講義の削除に失敗しました。');
        return false;
      }
    } catch (error) {
      console.error('Error deleting lecture:', error);
      alert('講義削除中にエラーが発生しました。');
      return false;
    }
  };

  const regenerateLecture = async (lectureId: string): Promise<string | null> => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}/api/lectures/${lectureId}/regenerate`,
        {
          method: 'POST',
        }
      );

      if (response.ok) {
        const result = await response.json();
        // Update the lecture status to pending in local state
        setLectures(prev => prev.map(lecture => 
          lecture.id === lectureId 
            ? { ...lecture, status: 'pending' }
            : lecture
        ));
        return result.task_id || lectureId;
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

  const addOptimisticLecture = useCallback(
    (lec: Omit<Lecture, 'created_at'> & { created_at?: string }) => {
      setLectures(prev => {
        if (prev.some(l => l.id === lec.id)) return prev;      // 二重防止
        return [
          {
            ...lec,
            created_at: lec.created_at ?? new Date().toISOString(),
          },
          ...prev,
        ];
      });
    },
    [],
  );

  return {
    lectures,
    isLoading,
    fetchLectures,
    deleteLecture,
    regenerateLecture,
    addOptimisticLecture,
  };
}