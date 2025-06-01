'use client';

import React, { useRef, useState, useCallback, useEffect } from 'react';
import ReactPlayer from 'react-player';
import { useTimeline, Event } from '@/hooks/useTimeline';
import { CharacterCanvas } from './CharacterCanvas';

type Props = {
  manifest: {
    slideUrl:  string;
    audioUrl:  string;
    events:    Event[];
    sprites:   Record<'left' | 'right', string>;
    slideWidth: number;
    slideHeight: number;
  };
};

function fitSlide(iframe: HTMLIFrameElement | null, w: number, h: number) {
  if (!iframe) return;
  const container = iframe.parentElement;
  if (!container) return;

  const cw = container.clientWidth;
  const ch = container.clientHeight;
  const scale = Math.min(cw / w, ch / h);

  iframe.style.transformOrigin = 'center';
  iframe.style.transform = `scale(${scale})`;
  iframe.style.width  = `${w}px`;
  iframe.style.height = `${h}px`;
}

export const Player: React.FC<Props> = ({ manifest }) => {
  const slideRef = useRef<HTMLIFrameElement>(null);
  const audioRef = useRef<ReactPlayer>(null);
  const [ready, setReady] = useState(false);
  const slideWin = useRef<Window | undefined>(undefined);

  /* -------- playSignal -------- */
  const playSignal = useCallback((ev: Event) => {
    if (!slideWin.current) return;
    if (ev.type.startsWith('slide')) {
      // slideNext → slide-next
      slideWin.current.postMessage(ev.type.replace(/[A-Z]/, (c) => '-' + c.toLowerCase()), '*');
    } else if (ev.type === 'pose') {
      window.dispatchEvent(new CustomEvent('pose', { detail: ev }));
    }
  }, []);


  useEffect(() => {
    const onResize = () => fitSlide(slideRef.current, manifest.slideWidth, manifest.slideHeight);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, [manifest.slideWidth, manifest.slideHeight]);

  /* -------- timeline -------- */
  useTimeline(
    audioRef.current?.getInternalPlayer() as HTMLAudioElement,
    manifest.events,
    playSignal,
  );

  /* -------- DOM -------- */
  return (
    <div className="relative w-full h-screen overflow-hidden bg-gray-100">
      {/* スライドコンテナ */}
      <div 
        className="absolute flex items-center justify-center"
        style={{
          top: '5%',
          left: '5%',
          width: '70%',
          height: '90%'
        }}
      >
        <iframe
          src={`${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}${manifest.slideUrl}`}
          className="w-full h-full border border-gray-400 bg-white"
          ref={(el) => {
            slideRef.current = el;
            slideWin.current = el?.contentWindow ?? undefined;
          }}
          onLoad={(el) => {
            setReady(true);
            fitSlide(el.currentTarget, manifest.slideWidth, manifest.slideHeight);
          }}
        />
      </div>

      {/* characters */}
      {manifest.sprites.right && (
        <CharacterCanvas side="right" src={manifest.sprites.right} />
      )}

      {/* audio */}
      {ready && (
        <ReactPlayer
          ref={audioRef}
          url={`${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}${manifest.audioUrl}`}
          playing
          controls={false}
          height={0}
          width={0}
        />
      )}
    </div>
  );
};
