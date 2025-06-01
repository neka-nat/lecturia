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
  };
};

function fitSlide(iframe: HTMLIFrameElement | null) {
  if (!iframe || !iframe.contentWindow) return;

  const doc = iframe.contentWindow.document;
  const slideW = doc.body.scrollWidth  || 1280; // fallback
  const slideH = doc.body.scrollHeight || 720;

  const parent = iframe.parentElement!;
  const cw = parent.clientWidth;
  const ch = parent.clientHeight;

  const scale = Math.min(cw / slideW, ch / slideH);

  iframe.style.width  = `${slideW}px`;
  iframe.style.height = `${slideH}px`;
  iframe.style.transformOrigin = 'top left';
  iframe.style.transform = `scale(${scale})`;
}

export const Player: React.FC<Props> = ({ manifest }) => {
  const slideRef = useRef<HTMLIFrameElement>(null);
  const audioRef = useRef<ReactPlayer>(null);
  const [ready, setReady] = useState(false);
  const slideWin = useRef<Window>();

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
    const onResize = () => fitSlide(slideWin.current?.document.body);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  /* -------- timeline -------- */
  useTimeline(
    audioRef.current?.getInternalPlayer() as HTMLAudioElement,
    manifest.events,
    playSignal,
  );

  /* -------- DOM -------- */
  return (
    <div className="relative w-full h-screen overflow-hidden">
      {/* slide */}
      <iframe
        src={`${process.env.NEXT_PUBLIC_LECTURIA_API_ORIGIN}${manifest.slideUrl}`}
        className="absolute border border-gray-400"
        style={{
          top: '5%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '80%',
          height: '90%'
        }}
        ref={(el) => {
          slideRef.current = el;
          slideWin.current = el?.contentWindow ?? undefined;
        }}
        onLoad={(el) => {
          setReady(true);
          fitSlide(el.currentTarget);
        }}
      />

      {/* characters */}
      {manifest.sprites.left  && (
        <CharacterCanvas side="left"  src={manifest.sprites.left}  />
      )}
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
