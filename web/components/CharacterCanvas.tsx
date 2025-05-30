import { useEffect, useRef } from 'react';

export const CharacterCanvas = ({ side }: { side: 'left' | 'right' }) => {
  const ref = useRef<HTMLCanvasElement>(null);

  /* 既存 player.html の Character クラスを転記しても良い */

  useEffect(() => {
    // TODO: sprite 読込＆アニメ開始
  }, []);

  return (
    <canvas
      ref={ref}
      className="absolute bottom-0 aspect-square pointer-events-none"
      style={{ [side === 'left' ? 'left' : 'right']: '-4vw', width: '30vw' }}
    />
  );
};
