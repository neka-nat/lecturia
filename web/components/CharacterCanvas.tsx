'use client';

import { useEffect, useRef, useState } from 'react';

const COLS = 3;
const ROWS = 3;
const FPS  = 3; // ← 好みで
const POSES: Record<string, [number, number]> = {
  idle: [0, 2],
  talk: [3, 5],
  point: [6, 8],
};

type Props = {
  side: 'left' | 'right';
  src:  string;              // sprite シート (3×3)
};

export const CharacterCanvas = ({ side, src }: Props) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const spriteRef = useRef<HTMLImageElement | undefined>(undefined);
  const [pose, setPose] = useState<'idle' | 'talk' | 'point'>('idle');

  /* ---------- 画像ロード ---------- */
  useEffect(() => {
    const img = new Image();
    img.src = src;
    img.onload = () => (spriteRef.current = img);
  }, [src]);

  /* ---------- pose イベント ---------- */
  useEffect(() => {
    const listener = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail?.target === side && detail?.type === 'pose') {
        setPose(detail.name ?? 'idle');
      }
    };
    window.addEventListener('pose', listener as EventListener);
    return () => window.removeEventListener('pose', listener as EventListener);
  }, [side]);

  /* ---------- 描画ループ ---------- */
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx    = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    const fit = () => {
      const dpr = window.devicePixelRatio || 1;
      canvas.width  = canvas.clientWidth  * dpr;
      canvas.height = canvas.clientHeight * dpr;
      ctx.resetTransform();
      ctx.scale(dpr, dpr);
    };
    fit();
    window.addEventListener('resize', fit);

    let frame = 0;
    let last  = 0;
    const interval = 1000 / FPS;

    const loop = (t: number) => {
      requestAnimationFrame(loop);
      if (!spriteRef.current || t - last < interval) return;

      const [s, e] = POSES[pose] ?? POSES.idle;
      frame = frame < s || frame > e ? s : frame + 1 > e ? s : frame + 1;

      const sw = spriteRef.current.width  / COLS;
      const sh = spriteRef.current.height / ROWS;
      const sx = (frame % COLS) * sw;
      const sy = Math.floor(frame / COLS) * sh;

      ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
      ctx.drawImage(
        spriteRef.current,
        sx, sy, sw, sh,
        0, 0, canvas.clientWidth, canvas.clientHeight,
      );
      last = t;
    };
    requestAnimationFrame(loop);

    return () => window.removeEventListener('resize', fit);
  }, [pose]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute pointer-events-none"
      style={{ 
        bottom: '5%',
        ...(side === 'left' ? { left: '65%' } : { right: '5%' }),
        width: '20%',
        height: '20%',
        aspectRatio: '1/1',
        zIndex: 20
      }}
    />
  );
};