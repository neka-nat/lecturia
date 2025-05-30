'use client';

import React, {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
} from 'react';
import { Event, useTimeline } from '@/hooks/useTimeline';
import { Character } from '@/utils/character';

export type Manifest = {
  slideUrl: string;
  audioUrl: string;
  events: Event[];
  sprites: Record<'left' | 'right', string>; // base64 data-urls (may be empty strings)
  slideWidth: number; // not used yet but kept for future scaling
  slideHeight: number;
};

interface Props {
  manifest: Manifest;
}

export const Player: React.FC<Props> = ({ manifest }) => {
  /* refs to DOM elements */
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const leftCanvasRef = useRef<HTMLCanvasElement>(null);
  const rightCanvasRef = useRef<HTMLCanvasElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  /* character instances (lazy-created) */
  const charLeft = useRef<Character | null>(null);
  const charRight = useRef<Character | null>(null);

  /* Initialise Character objects once the canvases exist */
  useLayoutEffect(() => {
    if (leftCanvasRef.current && !charLeft.current) {
      charLeft.current = new Character(leftCanvasRef.current);
    }
    if (rightCanvasRef.current && !charRight.current) {
      charRight.current = new Character(rightCanvasRef.current);
    }
  }, []);

  /* Load initial sprites from the manifest */
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

  /* Helper to post messages to the slide */
  const postToSlide = useCallback(
    (msg: string) => {
      const win = iframeRef.current?.contentWindow;
      if (win) win.postMessage(msg, '*');
    },
    [],
  );

  /* playSignal replicates the global function from player.html */
  const playSignal = useCallback(
    (ev: Event) => {
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
        case 'pose': {
          const actor = ev.target === 'left' ? charLeft.current : charRight.current;
          actor?.setPose((ev.name as any) ?? 'idle');
          break;
        }
        default:
          break;
      }
    },
    [postToSlide],
  );

  /* Expose helpers on window for external debug / parity with old player.html */
  useEffect(() => {
    (window as any).playSignal = (p: any) => playSignal(p);
    (window as any).setSprite = async (src: string, target: 'left' | 'right' = 'right') => {
      const actor = target === 'left' ? charLeft.current : charRight.current;
      await actor?.setSprite(src);
    };
  }, [playSignal]);

  useTimeline(audioRef.current ?? null, manifest.events, playSignal);

  /* Guarantee user interaction before audio play (autoplay policies) */
  const handlePlay = () => {
    audioRef.current?.play();
  };

  return (
    <div
      id="root"
      style={{ position: 'relative', width: '100%', height: '100vh', overflow: 'hidden' }}
    >
      {/* Slide iframe */}
      <iframe
        id="slide"
        ref={iframeRef}
        src={manifest.slideUrl}
        // faithful to original default centre layout; could be toggled later
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

      {/* Character canvases */}
      <canvas
        id="charLeft"
        ref={leftCanvasRef}
        style={{
          position: 'absolute',
          bottom: 0,
          left: '-4vw',
          width: '30vw',
          aspectRatio: '1 / 1',
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
          aspectRatio: '1 / 1',
          pointerEvents: 'none',
          zIndex: 10,
        }}
      />

      {/* Hidden audio element (controls shown for debug) */}
      <audio ref={audioRef} src={manifest.audioUrl} preload="auto" />

      {/* Simple overlay button to start playback (optional) */}
      <button
        onClick={handlePlay}
        style={{ position: 'absolute', top: 10, right: 10, zIndex: 20 }}
      >
        ▶︎ Play
      </button>
    </div>
  );
};
