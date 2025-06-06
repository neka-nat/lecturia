'use client';

import React, {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { Event, useTimeline } from '@/hooks/useTimeline';
import { Character } from '@/utils/character';

export type Manifest = {
  slideUrl: string;
  audioUrls: string[];
  events: Event[];
  sprites: Record<'left' | 'right', string>; // base64 data‑urls (may be empty strings)
  slideWidth: number;
  slideHeight: number;
};

interface Props {
  manifest: Manifest;
}

export const Player: React.FC<Props> = ({ manifest }) => {
  /* ---------------- refs ---------------- */
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const leftCanvasRef = useRef<HTMLCanvasElement>(null);
  const rightCanvasRef = useRef<HTMLCanvasElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  /* ---------------- characters ---------------- */
  const charLeft = useRef<Character | null>(null);
  const charRight = useRef<Character | null>(null);

  /* ---------------- state ---------------- */
  const [slideReady, setSlideReady] = useState(false);
  const [pageIdx, setPageIdx] = useState(0); // 0‑based

  /**
   * イベントをスライド単位に分割 => [ [slide1 events ...], [slide2 events ...], ... ]
   */
  const slideEvents = useMemo(() => {
    const arr: Event[][] = [];
    let cur: Event[] = [];
    manifest.events.forEach((ev) => {
      if (ev.type === "slideNext") {
        arr.push(cur);
        cur = [];
      } else {
        cur.push(ev);
      }
    });
    arr.push(cur); // last slide
    return arr;
  }, [manifest.events]);

  const postToSlide = useCallback((msg: string) => {
    iframeRef.current?.contentWindow?.postMessage(msg, "*");
  }, []);

  /**
   * audio ソースを page に合わせて切替
   */
  const changeAudio = useCallback(
    (newPage: number) => {
      const a = audioRef.current;
      if (!a) return;

      // 範囲ガード
      if (newPage < 0 || newPage >= manifest.audioUrls.length) return;

      a.pause();
      a.src = manifest.audioUrls[newPage];
      a.load();
      a.currentTime = 0;
      setPageIdx(newPage);
    },
    [manifest.audioUrls]
  );

  const { reset: resetTimeline } = useTimeline(
    slideReady && audioRef.current ? audioRef.current : null,
    slideEvents[pageIdx] ?? [],
    (ev) => {
      playSignal(ev);
    }
  );

  useLayoutEffect(() => {
    if (leftCanvasRef.current && !charLeft.current) {
      charLeft.current = new Character(leftCanvasRef.current);
    }
    if (rightCanvasRef.current && !charRight.current) {
      charRight.current = new Character(rightCanvasRef.current);
    }
  }, []);

  /* load initial sprites */
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

  const handlePlay = () => {
    if (!slideReady) return;
    audioRef.current?.play();
  };
  const handlePause = () => audioRef.current?.pause();
  const handleStop = () => {
    const a = audioRef.current;
    if (!a) return;
    a.pause();
    a.currentTime = 0;
    resetTimeline();
    charLeft.current?.setPose("idle");
    charRight.current?.setPose("idle");
    changeAudio(0); // reset to first audio
    setSlideReady(false);
    iframeRef.current!.src = manifest.slideUrl; // reload slide 1
  };

  const playSignal = useCallback(
    (ev: Event & { src?: string }) => {
      switch (ev.type) {
        case "slideNext": {
          postToSlide("slide-next");
          const next = Math.min(pageIdx + 1, manifest.audioUrls.length - 1);
          if (next !== pageIdx) {
            changeAudio(next);
            resetTimeline();
            // 自動再生を維持
            audioRef.current?.play();
          }
          break;
        }
        case "slidePrev": {
          postToSlide("slide-prev");
          const prev = Math.max(pageIdx - 1, 0);
          if (prev !== pageIdx) {
            changeAudio(prev);
            resetTimeline();
            audioRef.current?.play();
          }
          break;
        }
        case "slideStep":
          postToSlide("slide-step");
          break;
        case "pose": {
          const actor = ev.target === "left" ? charLeft.current : charRight.current;
          actor?.setPose((ev.name as any) ?? "idle");
          break;
        }
        case "sprite": {
          if (ev.src) {
            const actor = ev.target === "left" ? charLeft.current : charRight.current;
            actor?.setSprite(ev.src);
          }
          break;
        }
        default:
          break;
      }
    },
    [pageIdx, postToSlide, changeAudio, resetTimeline, manifest.audioUrls.length]
  );

  useEffect(() => {
    const a = audioRef.current;
    if (!a) return;
    const onEnded = () => playSignal({ type: "slideNext", time_sec: 0 });
    a.addEventListener("ended", onEnded);
    return () => a.removeEventListener("ended", onEnded);
  }, [playSignal]);

  return (
    <div
      id="root"
      style={{ position: "relative", width: "100%", height: "100vh", overflow: "hidden" }}
    >
      {/* slide */}
      <iframe
        id="slide"
        ref={iframeRef}
        src={manifest.slideUrl}
        onLoad={() => setSlideReady(true)}
        style={{
          position: "absolute",
          top: "5%",
          left: "50%",
          transform: "translateX(-50%)",
          width: "80%",
          height: "90%",
          border: "1px solid gray",
          background: "#fff",
        }}
      />

      {/* character canvases */}
      <canvas
        id="charLeft"
        ref={leftCanvasRef}
        style={{
          position: "absolute",
          bottom: 0,
          left: "-4vw",
          width: "30vw",
          height: "30vw",
          pointerEvents: "none",
          zIndex: 10,
        }}
      />
      <canvas
        id="charRight"
        ref={rightCanvasRef}
        style={{
          position: "absolute",
          bottom: 0,
          right: "-4vw",
          width: "30vw",
          height: "30vw",
          pointerEvents: "none",
          zIndex: 10,
        }}
      />

      {/* audio element (src is managed dynamically) */}
      <audio ref={audioRef} src={manifest.audioUrls[0]} preload="auto" />

      {/* controls */}
      <div style={{ position: "absolute", top: 10, right: 10, zIndex: 20 }}>
        <button onClick={handlePlay} disabled={!slideReady}>
          ▶︎
        </button>{" "}
        <button onClick={handlePause}>⏸</button>{" "}
        <button onClick={handleStop}>◼︎</button>
      </div>
    </div>
  );
};
