'use client';

import React, { useState } from 'react';

export type Quiz = { question: string; choices: string[]; answer_index: number };
export type QuizSection = { name: string; slide_no: number; quizzes: Quiz[] };

interface Props {
  section: QuizSection;
  onClose: (correct: boolean) => void;
}

export const QuizModal: React.FC<Props> = ({ section, onClose }) => {
  const [curIdx, setCurIdx] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [anyWrong, setAnyWrong] = useState(false);
  const quiz = section.quizzes[curIdx];
  const answered = selected !== null;
  const progress = ((curIdx + 1) / section.quizzes.length) * 100;

  const handleSelect = (idx: number) => {
    if (answered) return;
    const correct = idx === quiz.answer_index;
    setSelected(idx);
    if (!correct) setAnyWrong(true);

    const isLast = curIdx === section.quizzes.length - 1;
    setTimeout(() => {
      if (isLast) {
        onClose(!anyWrong && correct);
      } else {
        setCurIdx((i) => i + 1);
        setSelected(null);
      }
    }, 1200);
  };

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-indigo-900/80 via-purple-900/80 to-pink-900/80 backdrop-blur-sm flex items-center justify-center z-40 p-4">
      <div className="relative bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8 w-full max-w-lg transform animate-in slide-in-from-bottom-4 duration-500">
        {/* Progress Bar */}
        {section.quizzes.length > 1 && (
          <div className="absolute top-0 left-0 right-0 h-1 bg-gray-200/50 rounded-t-3xl overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-600 transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}

        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full mb-4 shadow-lg">
            <span className="text-2xl">🧠</span>
          </div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
            クイズタイム！
          </h2>
          {section.quizzes.length > 1 && (
            <p className="text-sm text-gray-600 font-medium">
              問題 {curIdx + 1} / {section.quizzes.length}
            </p>
          )}
        </div>

        {/* Question */}
        <div className="mb-8">
          <p className="text-lg text-gray-800 font-semibold leading-relaxed text-center">
            {quiz.question}
          </p>
        </div>

        {/* Choices */}
        <div className="space-y-3 mb-6">
          {quiz.choices.map((c, i) => {
            const isCorrect = answered && i === quiz.answer_index;
            const isWrong = answered && i === selected && i !== quiz.answer_index;
            const isSelected = answered && i === selected;
            
            return (
              <button
                key={i}
                onClick={() => handleSelect(i)}
                disabled={answered}
                className={`
                  w-full px-6 py-4 rounded-2xl font-medium text-left transition-all duration-300 transform
                  ${answered ? 'cursor-default' : 'cursor-pointer hover:scale-[1.02] hover:shadow-md active:scale-[0.98]'}
                  ${!answered ? 'bg-gray-50 hover:bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50 border-2 border-gray-200 hover:border-indigo-300' : ''}
                  ${isCorrect ? 'bg-gradient-to-r from-emerald-100 to-green-100 border-2 border-emerald-400 shadow-lg' : ''}
                  ${isWrong ? 'bg-gradient-to-r from-red-100 to-rose-100 border-2 border-red-400 shadow-lg' : ''}
                  ${!isSelected && answered && i === quiz.answer_index ? 'bg-gradient-to-r from-emerald-100 to-green-100 border-2 border-emerald-400 shadow-lg' : ''}
                `}
              >
                <div className="flex items-center justify-between">
                  <span className={`${isCorrect || (!isSelected && answered && i === quiz.answer_index) ? 'text-emerald-800' : isWrong ? 'text-red-800' : 'text-gray-800'}`}>
                    {c}
                  </span>
                  {isCorrect && (
                    <span className="text-emerald-600 text-xl animate-in zoom-in duration-300">✓</span>
                  )}
                  {isWrong && (
                    <span className="text-red-600 text-xl animate-in zoom-in duration-300">✗</span>
                  )}
                  {!isSelected && answered && i === quiz.answer_index && (
                    <span className="text-emerald-600 text-xl animate-in zoom-in duration-300">✓</span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Feedback */}
        {answered && (
          <div className="text-center">
            <div className={`inline-flex items-center px-6 py-3 rounded-full font-bold text-lg shadow-lg animate-in zoom-in duration-500 ${
              selected === quiz.answer_index 
                ? 'bg-gradient-to-r from-emerald-500 to-green-500 text-white' 
                : 'bg-gradient-to-r from-red-500 to-rose-500 text-white'
            }`}>
              {selected === quiz.answer_index ? (
                <>
                  <span className="mr-2">🎉</span>
                  正解です！
                </>
              ) : (
                <>
                  <span className="mr-2">💭</span>
                  もう一度考えてみよう
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
