import { BookOpen, Sparkles } from 'lucide-react';

export function Header() {
  return (
    <div className="text-center mb-12 animate-fade-in">
      <div className="inline-flex items-center gap-3 mb-6">
        <div className="relative">
          <BookOpen className="w-12 h-12 text-indigo-600" />
          <Sparkles className="w-5 h-5 text-yellow-500 absolute -top-1 -right-1 animate-pulse" />
        </div>
        <h1 className="text-5xl font-black bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
          Lecturia
        </h1>
      </div>
      <p className="text-xl text-slate-600 font-medium">
        AI で作る、あなただけの学び方
      </p>
      <div className="w-24 h-1 bg-gradient-to-r from-indigo-500 to-purple-500 mx-auto mt-4 rounded-full"></div>
    </div>
  );
}