import { useState, useEffect } from 'react';
import { Character, AVAILABLE_CHARACTERS } from '../types/character';

const TASK_ID_STORAGE_KEY = 'lecturia-current-task-id';

export interface CreateLectureResult { taskId: string }

export function useLectureForm() {
  const [topic, setTopic] = useState('');
  const [detail, setDetail] = useState('');
  const [selectedCharacter, setSelectedCharacter] = useState<Character>(AVAILABLE_CHARACTERS[0]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);

  // Restore task ID from localStorage on component mount
  useEffect(() => {
    const savedTaskId = localStorage.getItem(TASK_ID_STORAGE_KEY);
    if (savedTaskId) {
      setCurrentTaskId(savedTaskId);
    }
  }, []);

  const createLecture = async (): Promise<CreateLectureResult | null> => {
    if (!topic.trim()) return null;

    setIsSubmitting(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}/api/create-lecture`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            topic: topic.trim(),
            detail: detail.trim() || null,
            characters: [selectedCharacter],
          }),
        },
      );

      if (!res.ok) {
        alert('講義作成に失敗しました。');
        return null;
      }

      const { task_id: taskId } = await res.json();
      setCurrentTaskId(taskId);
      localStorage.setItem(TASK_ID_STORAGE_KEY, taskId);
      resetForm();

      return { taskId };
    } catch (e) {
      console.error(e);
      alert('講義作成中にエラーが発生しました。');
      return null;
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setTopic('');
    setDetail('');
  };

  const clearTaskId = () => {
    setCurrentTaskId(null);
    // Remove task ID from localStorage
    localStorage.removeItem(TASK_ID_STORAGE_KEY);
  };

  return {
    topic,
    setTopic,
    detail,
    setDetail,
    selectedCharacter,
    setSelectedCharacter,
    isSubmitting,
    createLecture,
    resetForm,
    currentTaskId,
    clearTaskId,
  };
}