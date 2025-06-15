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
import { QuizModal } from '@/components/QuizModal';

export type Manifest = {
  slideUrl: string;
  audioUrls: string[];        // page‑wise audios
  events: Event[];            // timeline (absolute)
  sprites: Record<'left'|'right', string>;
  slideWidth: number;
  slideHeight: number;
  quizSections: {
    name: string;
    slide_no: number;
    quizzes: {
      question: string;
      choices: string[];
      answer_index: number;
    }[];
  }[];
};

interface Props { manifest: Manifest; }

export const Player: React.FC<Props> = ({ manifest }) => {
  /* refs & state */
  const iframeRef      = useRef<HTMLIFrameElement>(null);
  const leftCanvasRef  = useRef<HTMLCanvasElement>(null);
  const rightCanvasRef = useRef<HTMLCanvasElement>(null);
  const audioRef       = useRef<HTMLAudioElement>(null);

  const charLeft  = useRef<Character|null>(null);
  const charRight = useRef<Character|null>(null);

  const [pageIdx, setPageIdx]   = useState(0);   // current page (0‑based)
  const [slideReady, setReady]  = useState(false);
  const [jumpToSlide, setJumpToSlide] = useState(''); // input for slide navigation
  const [quizOpen, setQuizOpen] = useState<Manifest['quizSections'][number] | null>(null);
  const hasInteracted           = useRef(false); // ▶︎ pressed once?

  /* -------------------------------------------------------------
     Helper: postMessage to iframe
  ------------------------------------------------------------- */
  const postToSlide = useCallback((msg:string)=>{
    iframeRef.current?.contentWindow?.postMessage(msg,'*');
  },[]);

  /* -------------------------------------------------------------
     Split events by slideNext  +  🌟 re‑base time_sec 🌟
  ------------------------------------------------------------- */
  const eventsPages = useMemo<Event[][]>(()=>{
    const pages: Event[][] = [];
    let buf: Event[] = [];
    let base = 0;                       // start time of current page

    manifest.events.forEach(ev=>{
      if (ev.type === 'slideNext') {
        pages.push(buf);
        buf = [];
        base = ev.time_sec;             // next page start
      } else {
        buf.push({ ...ev, time_sec: ev.time_sec - base }); // ⏱️ relative
      }
    });
    pages.push(buf);                    // last page
    return pages;
  },[manifest.events]);

  /* -------------------------------------------------------------
     Character canvas bootstrap
  ------------------------------------------------------------- */
  useLayoutEffect(()=>{
    if (leftCanvasRef.current && !charLeft.current){
      charLeft.current = new Character(leftCanvasRef.current);
    }
    if (rightCanvasRef.current && !charRight.current){
      charRight.current = new Character(rightCanvasRef.current);
    }
  },[]);

  /* load default sprites */
  useEffect(()=>{
    (async()=>{
      if (manifest.sprites.right && charRight.current){
        await charRight.current.setSprite(manifest.sprites.right);
        // Initialize to idle pose to prevent early event states from showing
        charRight.current.setPose('idle');
      }
      if (manifest.sprites.left && charLeft.current){
        await charLeft.current.setSprite(manifest.sprites.left);
        // Initialize to idle pose to prevent early event states from showing
        charLeft.current.setPose('idle');
      }
    })();
  },[manifest.sprites]);

  /* -------------------------------------------------------------
     Timeline hook (per page)
  ------------------------------------------------------------- */
  const { reset: resetTimeline } = useTimeline(
    slideReady && audioRef.current ? audioRef.current : null,
    eventsPages[pageIdx] ?? [],
    (ev)=> playSignal(ev as any),
  );

  /* audio source swap on page change */
  useEffect(()=>{
    const a = audioRef.current; if(!a) return;
    a.pause();
    a.src = manifest.audioUrls[pageIdx] ?? '';
    a.currentTime = 0;
    resetTimeline();
    // Reset characters to idle when changing pages/resetting timeline
    charLeft.current?.setPose('idle');
    charRight.current?.setPose('idle');
    if (hasInteracted.current){ a.play().catch(()=>{}); }
  },[pageIdx, resetTimeline]);

  /* auto‑advance when audio ends */
  useEffect(()=>{
    const a = audioRef.current; if(!a) return;
    const onEnd = ()=>{ if(pageIdx < eventsPages.length-1) goTo(pageIdx+1); };
    a.addEventListener('ended', onEnd);
    return ()=> a.removeEventListener('ended', onEnd);
  },[pageIdx, eventsPages.length]);

  /* -------------------------------------------------------------
     Navigation
  ------------------------------------------------------------- */
  const goTo = (idx:number)=>{
    idx = Math.max(0, Math.min(idx, eventsPages.length-1));
    if(idx===pageIdx) return;
    postToSlide(idx>pageIdx ? 'slide-next' : 'slide-prev');
    setPageIdx(idx);
    charLeft.current?.setPose('idle');
    charRight.current?.setPose('idle');
  };

  /* -------------------------------------------------------------
     Event → action
  ------------------------------------------------------------- */
  const playSignal = useCallback((ev: Event & {src?:string})=>{
    switch(ev.type){
      case 'slideNext': goTo(pageIdx+1); break;
      case 'slidePrev': goTo(pageIdx-1); break;
      case 'slideStep': postToSlide('slide-step'); break;
      case 'pose':{
        const actor = ev.target==='left' ? charLeft.current : charRight.current;
        actor?.setPose((ev.name as any)||'idle');
        break;
      }
      case 'sprite':{
        const actor = ev.target==='left' ? charLeft.current : charRight.current;
        if(ev.src) actor?.setSprite(ev.src);
        break;
      }
      case 'quiz': {       
        audioRef.current?.pause();  // 講義音声ストップ
        // キャラをポイントポーズにしておく
        charRight.current?.setPose('idle');
        const section = manifest.quizSections.find(s => s.name === ev.name);
        if (section) setQuizOpen(section);
        break;
      }
      default: break;
    }
  },[pageIdx, postToSlide]);

  /* -------------------------------------------------------------
     Controls
  ------------------------------------------------------------- */
  const handlePlay = ()=>{ if(!slideReady) return; hasInteracted.current = true; audioRef.current?.play(); };
  const handlePause = ()=> audioRef.current?.pause();
  const handleStop = ()=>{ audioRef.current?.pause(); if(audioRef.current) audioRef.current.currentTime = 0; hasInteracted.current=false; goTo(0); };

  /* slide navigation handlers */
  const handlePrevSlide = ()=> goTo(pageIdx - 1);
  const handleNextSlide = ()=> goTo(pageIdx + 1);
  const handleJumpToSlide = ()=>{
    const slideNum = parseInt(jumpToSlide);
    if(isNaN(slideNum) || slideNum < 1 || slideNum > eventsPages.length) return;
    goTo(slideNum - 1); // convert 1-based to 0-based
    setJumpToSlide('');
  };
  const handleQuizClose = () => {
    setQuizOpen(null);
    charLeft.current?.setPose('idle');
    charRight.current?.setPose('idle');
    audioRef.current?.play().catch(()=>{});
  };

  /* -------------------------------------------------------------
     Render
  ------------------------------------------------------------- */
  return (
    <div id="root" style={{position:'relative',width:'100%',height:'100vh',overflow:'hidden'}}>
      <iframe
        id="slide"
        ref={iframeRef}
        src={manifest.slideUrl}
        onLoad={()=>setReady(true)}
        style={{position:'absolute',top:'5%',left:'50%',transform:'translateX(-50%)',width:'80%',height:'90%',border:'1px solid gray',background:'#fff'}}
      />

      <canvas id="charLeft" ref={leftCanvasRef} style={{position:'absolute',bottom:0,left:'-4vw',width:'30vw',height:'30vw',pointerEvents:'none',zIndex:10}} />
      <canvas id="charRight" ref={rightCanvasRef} style={{position:'absolute',bottom:0,right:'-4vw',width:'30vw',height:'30vw',pointerEvents:'none',zIndex:10}} />

      <audio ref={audioRef} preload="auto" />

      {/* Integrated Controls - Slide Navigation + Playback */}
      <div style={{position:'absolute',top:10,right:10,zIndex:20,background:'rgba(255,255,255,0.9)',padding:'10px',borderRadius:'8px',display:'flex',alignItems:'center',gap:'12px'}}>
        {/* Slide Navigation */}
        <div style={{display:'flex',alignItems:'center',gap:'8px',borderRight:'1px solid #ddd',paddingRight:'12px'}}>
          <div style={{fontWeight:'bold',color:'#333',fontSize:'14px'}}>
            スライド {pageIdx + 1} / {eventsPages.length}
          </div>
          <button 
            onClick={handlePrevSlide} 
            disabled={pageIdx === 0}
            style={{padding:'4px 8px',cursor:pageIdx === 0 ? 'not-allowed' : 'pointer',opacity:pageIdx === 0 ? 0.5 : 1,border:'1px solid #ccc',borderRadius:'4px',background:'#f8f9fa',color:'#333'}}
          >
            ◀
          </button>
          <button 
            onClick={handleNextSlide} 
            disabled={pageIdx >= eventsPages.length - 1}
            style={{padding:'4px 8px',cursor:pageIdx >= eventsPages.length - 1 ? 'not-allowed' : 'pointer',opacity:pageIdx >= eventsPages.length - 1 ? 0.5 : 1,border:'1px solid #ccc',borderRadius:'4px',background:'#f8f9fa',color:'#333'}}
          >
            ▶
          </button>
          <input 
            type="number" 
            min="1" 
            max={eventsPages.length}
            value={jumpToSlide}
            onChange={(e)=>setJumpToSlide(e.target.value)}
            onKeyDown={(e)=>e.key==='Enter' && handleJumpToSlide()}
            placeholder="番号"
            style={{width:'50px',padding:'4px',textAlign:'center',border:'1px solid #ccc',borderRadius:'4px',fontSize:'12px',color:'#333'}}
          />
          <button onClick={handleJumpToSlide} style={{padding:'4px 6px',border:'1px solid #ccc',borderRadius:'4px',background:'#f8f9fa',fontSize:'12px',color:'#333'}}>
            移動
          </button>
        </div>
        
        {/* Playback Controls */}
        <div style={{display:'flex',alignItems:'center',gap:'4px'}}>
          <button onClick={handlePlay} style={{padding:'6px 10px',border:'1px solid #ccc',borderRadius:'4px',background:'#f8f9fa',fontSize:'16px',cursor:'pointer',color:'#333'}}>▶︎</button>
          <button onClick={handlePause} style={{padding:'6px 10px',border:'1px solid #ccc',borderRadius:'4px',background:'#f8f9fa',fontSize:'16px',cursor:'pointer',color:'#333'}}>⏸</button>
          <button onClick={handleStop} style={{padding:'6px 10px',border:'1px solid #ccc',borderRadius:'4px',background:'#f8f9fa',fontSize:'16px',cursor:'pointer',color:'#333'}}>◼︎</button>
        </div>
      </div>
      {quizOpen && (
        <QuizModal section={quizOpen} onClose={handleQuizClose} />
      )}
    </div>
  );
};
