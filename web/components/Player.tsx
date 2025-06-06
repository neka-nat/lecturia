'use client';

import React, {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from 'react';
import { Event, useTimeline } from '@/hooks/useTimeline';
import { Character } from '@/utils/character';

export type Manifest = {
  slideUrl: string;
  audioUrl: string;
  events: Event[];
  sprites: Record<'left' | 'right', string>; // base64 data‑urls (may be empty strings)
  slideWidth: number;
  slideHeight: number;
};

interface Props {
  manifest: Manifest;
}

export const Player: React.FC<Props> = ({ manifest }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const leftCanvasRef = useRef<HTMLCanvasElement>(null);
  const rightCanvasRef = useRef<HTMLCanvasElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  const charLeft = useRef<Character | null>(null);
  const charRight = useRef<Character | null>(null);

  const [slideReady, setSlideReady] = useState(false);

  useLayoutEffect(() => {
    if (leftCanvasRef.current && !charLeft.current) {
      charLeft.current = new Character(leftCanvasRef.current);
    }
    if (rightCanvasRef.current && !charRight.current) {
      charRight.current = new Character(rightCanvasRef.current);
    }
  }, []);

  useEffect(() => {
    (async () => {
      if (manifest.sprites.right && charRight.current) {
        await charRight.current.setSprite(manifest.sprites.right);
      }
      if (manifest.sprites.left && charLeft.current) {
        await charLeft.current.setSprite(manifest.sprites.left);
      }
    })();
  }, [manifest.sprites]);

  const postToSlide = useCallback((msg: string) => {
    iframeRef.current?.contentWindow?.postMessage(msg, '*');
  }, []);

  const playSignal = useCallback(
    (ev: Event & { src?: string }) => {
      switch (ev.type) {
        case 'slideNext':
          postToSlide('slide-next');
          break;
        case 'slidePrev':
          postToSlide('slide-prev');
          break;
        case 'slideStep':
          postToSlide('slide-step');
          break;
        case 'pose':
          (ev.target === 'left' ? charLeft.current : charRight.current)?.setPose(
            (ev.name as any) ?? 'idle',
          );
          break;
        case 'sprite':
          if (ev.src) {
            (ev.target === 'left' ? charLeft.current : charRight.current)?.setSprite(ev.src);
          }
          break;
        default:
          break;
      }
    },
    [postToSlide],
  );

  const { reset: resetTimeline } = useTimeline(
    slideReady && audioRef.current ? audioRef.current : null,
    manifest.events,
    playSignal,
  );

  const handlePlay = () => {
    if (!slideReady) return; // safety
    audioRef.current?.play();
  };
  const handlePause = () => audioRef.current?.pause();
  const handleStop = () => {
    const a = audioRef.current;
    if (!a) return;
    a.pause();
    a.currentTime = 0;
    resetTimeline();
    charLeft.current?.setPose('idle');
    charRight.current?.setPose('idle');
    // reload slide to first page & reset ready flag
    if (iframeRef.current) {
      setSlideReady(false);
      iframeRef.current.src = manifest.slideUrl;
    }
  };

  return (
    <div
      id="root"
      style={{ position: 'relative', width: '100%', height: '100vh', overflow: 'hidden' }}
    >
      <iframe
        id="slide"
        ref={iframeRef}
        src={manifest.slideUrl}
        onLoad={() => setSlideReady(true)}
        style={{
          position: 'absolute',
          top: '5%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '80%',
          height: '90%',
          border: '1px solid gray',
          background: '#fff',
        }}
      />

      <canvas
        id="charLeft"
        ref={leftCanvasRef}
        style={{
          position: 'absolute',
          bottom: 0,
          left: '-4vw',
          width: '30vw',
          height: '30vw',
          pointerEvents: 'none',
          zIndex: 10,
        }}
      />

      <canvas
        id="charRight"
        ref={rightCanvasRef}
        style={{
          position: 'absolute',
          bottom: 0,
          right: '-4vw',
          width: '30vw',
          height: '30vw',
          pointerEvents: 'none',
          zIndex: 10,
        }}
      />

      <audio ref={audioRef} src={manifest.audioUrl} preload="auto" />

      <div style={{ position: 'absolute', top: 10, right: 10, zIndex: 20 }}>
        <button onClick={handlePlay} disabled={!slideReady}>
          ▶︎
        </button>{' '}
        <button onClick={handlePause}>⏸</button>{' '}
        <button onClick={handleStop}>◼︎</button>
      </div>
    </div>
  );
};
