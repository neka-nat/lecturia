import { useState } from 'react';

export function useLectureForm() {
  const [topic, setTopic] = useState('');
  const [detail, setDetail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);

  const createLecture = async (): Promise<boolean> => {
    if (!topic.trim()) return false;

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
        setCurrentTaskId(result.task_id);
        resetForm();
        return true;
      } else {
        alert('講義作成に失敗しました。');
        return false;
      }
    } catch (error) {
      console.error('Error creating lecture:', error);
      alert('講義作成中にエラーが発生しました。');
      return false;
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
  };

  return {
    topic,
    setTopic,
    detail,
    setDetail,
    isSubmitting,
    createLecture,
    resetForm,
    currentTaskId,
    clearTaskId,
  };
}