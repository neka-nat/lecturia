import { useState, useEffect, useCallback, useRef } from 'react';

export type TaskStatus = 'not_started' | 'pending' | 'running' | 'completed' | 'failed';

const TASK_ID_STORAGE_KEY = 'lecturia-current-task-id';

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
  const currentStatusRef = useRef<TaskStatus | null>(null);

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
        currentStatusRef.current = statusData.status;
        
        // Auto-clear from localStorage after completion/failure with a delay
        if (statusData.status === 'completed' || statusData.status === 'failed') {
          setTimeout(() => {
            const currentStoredTaskId = localStorage.getItem(TASK_ID_STORAGE_KEY);
            if (currentStoredTaskId === taskId) {
              localStorage.removeItem(TASK_ID_STORAGE_KEY);
            }
          }, 30000); // Clear after 30 seconds to let user see the final status
        }
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
      // Reset status ref when task changes
      currentStatusRef.current = null;
      
      // Initial fetch
      fetchTaskStatus();
      
      // Poll for status updates every 3 seconds for incomplete tasks
      const interval = setInterval(() => {
        // Check current status using ref to avoid stale closure
        const currentStatus = currentStatusRef.current;
        if (currentStatus !== 'completed' && currentStatus !== 'failed') {
          fetchTaskStatus();
        }
      }, 3000);

      return () => clearInterval(interval);
    } else {
      // Clear status when no taskId
      setTaskStatus(null);
      setError(null);
      currentStatusRef.current = null;
    }
  }, [taskId, fetchTaskStatus]);

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