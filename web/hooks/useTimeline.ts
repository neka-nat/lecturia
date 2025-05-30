import { useEffect, useRef } from 'react';

export type Event = {
  type: 'slideNext' | 'slidePrev' | 'slideStep' | 'pose' | 'quiz';
  time_sec: number;
  name?: string;
  target?: 'left' | 'right';
};

export const useTimeline = (
  audio: HTMLAudioElement | null,
  events: Event[],
  playSignal: (ev: Event) => void,
) => {
  const idx = useRef(0);

  useEffect(() => {
    if (!audio) return;
    const tick = () => {
      const t = audio.currentTime;
      while (idx.current < events.length && t >= events[idx.current].time_sec) {
        playSignal(events[idx.current]);
        idx.current += 1;
      }
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [audio, events, playSignal]);
};
