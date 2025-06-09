import { useState, useEffect } from 'react';

export interface Lecture {
  id: string;
  title: string;
  topic: string;
  created_at: string;
}

export function useLectures() {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchLectures = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}/api/lectures`
      );
      if (response.ok) {
        const lecturesData = await response.json();
        setLectures(lecturesData);
      }
    } catch (error) {
      console.error('Error fetching lectures:', error);
    } finally {
      setIsLoading(false);
    }
  };

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

  useEffect(() => {
    fetchLectures();
  }, []);

  return {
    lectures,
    isLoading,
    fetchLectures,
    deleteLecture,
  };
}