'use client';

import React, { useRef, useState, useCallback } from 'react';
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

export const Player: React.FC<Props> = ({ manifest }) => {
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

  /* -------- timeline -------- */
  useTimeline(
    audioRef.current?.getInternalPlayer() as HTMLAudioElement,
    manifest.events,
    playSignal,
  );

  /* -------- DOM -------- */
  return (
    <div className="relative w-full h-screen overflow-hidden">
      <iframe
        src={`${process.env.LECTURIA_API_ORIGIN}${manifest.slideUrl}`}
        className="absolute top-5 left-1/2 -translate-x-1/2 w-4/5 h-4/5 border"
        ref={(el) => {
          slideWin.current = el?.contentWindow ?? undefined;
        }}
        onLoad={() => setReady(true)}
      />

      {/* characters */}
      {manifest.sprites.left && <CharacterCanvas side="left"  src={manifest.sprites.left}  />}
      {manifest.sprites.right && <CharacterCanvas side="right" src={manifest.sprites.right} />}

      {/* audio */}
      {ready && (
        <ReactPlayer
          ref={audioRef}
          url={`${process.env.LECTURIA_API_ORIGIN}${manifest.audioUrl}`}
          playing
          controls={false}
          height={0}
          width={0}
        />
      )}
    </div>
  );
};
