import { useState, useEffect, useCallback } from 'react';

export type TaskStatus = 'not_started' | 'pending' | 'running' | 'completed' | 'failed';

export interface TaskStatusData {
  status: TaskStatus;
  error?: string;
  created_at: string;
  updated_at: string;
}

export function useTaskStatus(taskId: string | null) {
  const [taskStatus, setTaskStatus] = useState<TaskStatusData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTaskStatus = useCallback(async () => {
    if (!taskId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}/api/tasks/${taskId}/status`
      );

      if (response.ok) {
        const statusData = await response.json();
        setTaskStatus(statusData);
      } else if (response.status === 404) {
        setError('タスクが見つかりません');
      } else {
        setError('タスクステータスの取得に失敗しました');
      }
    } catch (err) {
      console.error('Error fetching task status:', err);
      setError('タスクステータスの取得中にエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    if (taskId) {
      fetchTaskStatus();
      
      // Poll for status updates every 3 seconds for incomplete tasks
      const interval = setInterval(() => {
        if (taskStatus?.status !== 'completed' && taskStatus?.status !== 'failed') {
          fetchTaskStatus();
        }
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [taskId, fetchTaskStatus, taskStatus?.status]);

  const getStatusDisplay = (status: TaskStatus): { text: string; color: string } => {
    switch (status) {
      case 'not_started':
        return { text: '未開始', color: 'text-gray-500' };
      case 'pending':
        return { text: '待機中', color: 'text-yellow-500' };
      case 'running':
        return { text: '実行中', color: 'text-blue-500' };
      case 'completed':
        return { text: '完了', color: 'text-green-500' };
      case 'failed':
        return { text: '失敗', color: 'text-red-500' };
      default:
        return { text: '不明', color: 'text-gray-500' };
    }
  };

  return {
    taskStatus,
    isLoading,
    error,
    fetchTaskStatus,
    getStatusDisplay,
  };
}