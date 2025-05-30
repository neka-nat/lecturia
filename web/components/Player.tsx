'use client';

import React, { useRef, useState, useCallback } from 'react';
import ReactPlayer from 'react-player';
import { useTimeline, Event } from '@/hooks/useTimeline';
import { CharacterCanvas } from './CharacterCanvas';

type Props = {
  manifest: {
    slideUrl: string;
    audioUrl: string;
    events: Event[];
    sprites: Record<'left' | 'right', string>;
  };
};

export const Player: React.FC<Props> = ({ manifest }) => {
  const audioRef = useRef<ReactPlayer>(null);
  const [iframeLoaded, setIframeLoaded] = useState(false);

  // slide iframe の postMessage 先を保持
  const slideWin = useRef<Window>();

  const playSignal = useCallback(
    (ev: Event) => {
      if (!slideWin.current) return;
      switch (ev.type) {
        case 'slideNext':
        case 'slidePrev':
        case 'slideStep':
          slideWin.current.postMessage(ev.type.replace('slide', 'slide-'), '*');
          break;
        case 'pose':
          window.dispatchEvent(new CustomEvent('pose', { detail: ev }));
          break;
        // quiz などは別途
      }
    },
    [],
  );

  useTimeline(
    audioRef.current?.getInternalPlayer() as HTMLAudioElement,
    manifest.events,
    playSignal,
  );

  return (
    <div className="relative w-full h-screen overflow-hidden">
      {/* slide */}
      <iframe
        src={manifest.slideUrl}
        className="absolute top-5 left-1/2 -translate-x-1/2 w-4/5 h-4/5 border"
        ref={(el) => (slideWin.current = el?.contentWindow ?? undefined)}
        onLoad={() => setIframeLoaded(true)}
      />

      {/* characters */}
      <CharacterCanvas side="left" />
      <CharacterCanvas side="right" />

      {/* audio (react-player) */}
      {iframeLoaded && (
        <ReactPlayer
          ref={audioRef}
          url={manifest.audioUrl}
          playing
          controls={false}
          height={0}
          width={0}
        />
      )}
    </div>
  );
};
