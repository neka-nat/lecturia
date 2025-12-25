import { useEffect, useRef } from 'react';

export type Event = {
  type: 'slideNext' | 'slidePrev' | 'slideStep' | 'elementClick' | 'pose' | 'sprite' | 'quiz';
  time_sec: number;
  name?: string | null;
  target?: 'left' | 'right' | null;
  id?: string | null;
};

export const useTimeline = (
  audio: HTMLAudioElement | null,
  events: Event[],
  playSignal: (ev: Event) => void,
) => {
  const idx = useRef(0);              // 次に処理するイベント番号
  const rafId = useRef(0);            // rAF キャンセル用

  /** インデックスを 0 に戻す（外部呼び出し用） */
  const reset = () => {
    idx.current = 0;
  };

  /* audio / events が変わったら自動でリセット */
  useEffect(reset, [audio, events]);

  useEffect(() => {
    if (!audio) return;

    const step = () => {
      flush(audio.currentTime);
      if (!audio.paused && !audio.ended) {
        rafId.current = requestAnimationFrame(step);
      }
    };

    const onTimeUpdate = () => flush(audio.currentTime);

    const onPlay = () => {
      // Only start timeline processing when audio actually starts playing
      rafId.current = requestAnimationFrame(step);
    };

    const onPause = () => {
      // Stop timeline processing when audio is paused
      cancelAnimationFrame(rafId.current);
    };

    const flush = (t: number) => {
      while (idx.current < events.length && t >= events[idx.current].time_sec) {
        playSignal(events[idx.current]);
        idx.current += 1;
      }
    };

    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('play', onPlay);
    audio.addEventListener('pause', onPause);
    
    // Don't start timeline processing immediately - wait for play event

    return () => {
      audio.removeEventListener('timeupdate', onTimeUpdate);
      audio.removeEventListener('play', onPlay);
      audio.removeEventListener('pause', onPause);
      cancelAnimationFrame(rafId.current);
    };
  }, [audio, events, playSignal]);

  return { reset };
};
