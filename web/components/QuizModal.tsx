'use client';

import React, { useState } from 'react';

export type Quiz = { question: string; choices: string[]; answer_index: number };
export type QuizSection = { name: string; slide_no: number; quizzes: Quiz[] };

interface Props {
  section: QuizSection;
  onClose: () => void;
}

export const QuizModal: React.FC<Props> = ({ section, onClose }) => {
  const quiz = section.quizzes[0];      // 最小構成: セクション毎に 1 問だけ
  const [selected, setSelected] = useState<number | null>(null);
  const answered = selected !== null;

  const handleSelect = (idx: number) => {
    if (answered) return;
    setSelected(idx);
    setTimeout(onClose, 1200);          // 1.2 秒後に自動クローズ
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-40">
      <div className="bg-white rounded-xl shadow-2xl p-8 w-full max-w-md animate-fade-in">
        <h2 className="font-bold text-lg mb-4 text-indigo-700">📝 ここでクイズ！</h2>

        <p className="mb-6 text-slate-800 font-medium">{quiz.question}</p>

        <ul className="space-y-3">
          {quiz.choices.map((c, i) => {
            const isCorrect = answered && i === quiz.answer_index;
            const isWrong   = answered && i === selected && i !== quiz.answer_index;
            return (
              <li
                key={i}
                onClick={() => handleSelect(i)}
                className={`
                  px-4 py-2 border rounded-lg cursor-pointer
                  ${answered ? 'pointer-events-none' : 'hover:bg-slate-50'}
                  ${isCorrect ? 'border-emerald-500 bg-emerald-50' : ''}
                  ${isWrong   ? 'border-rose-500    bg-rose-50'    : ''}
                `}
              >
                {c}
              </li>
            );
          })}
        </ul>

        {answered && (
          <p className="mt-6 text-center font-semibold">
            {selected === quiz.answer_index ? '🎉 正解！' : '❌ 不正解...'}
          </p>
        )}
      </div>
    </div>
  );
};
