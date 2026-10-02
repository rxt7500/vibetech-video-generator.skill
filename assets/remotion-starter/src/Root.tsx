import React from 'react';
import {AbsoluteFill, Composition, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import board from '../storyboard.json';

// APIs: https://www.remotion.dev/docs/composition, /sequence, /use-current-frame, /interpolate
// Starter primitives only. Codex authors topic-specific images and illustrations per scene.
type Scene = {
  id: string; start_frame: number; duration_frames: number; kind: string;
  chapter: string; title: string; visual: string; animation: string;
  labels: string[]; image?: string; dark?: boolean;
  captions: {start_frame: number; end_frame: number; text: string}[];
};
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ink = '#302B26';
const red = '#A84737';
const serif = '"Noto Serif CJK SC", "Source Han Serif SC", "SimSun", serif';
const sans = '"Microsoft YaHei", "Noto Sans CJK SC", sans-serif';

const Diagram: React.FC<{scene: Scene; progress: number; color: string}> = ({scene, progress, color}) => {
  const labels = scene.labels;
  const tree = scene.kind === 'tree';
  const width = 1400;
  const spacing = labels.length > 1 ? (width - 260) / (labels.length - 1) : 0;
  return <svg viewBox="0 0 1400 460" style={{width: '100%', height: '100%', overflow: 'visible'}}>
    {tree ? <path d="M700 400 Q700 220 700 40" stroke={color} fill="none" strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1-progress}/> :
      <path d="M130 230 H1270" stroke={color} fill="none" strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={1-progress}/>}
    {labels.map((label, i) => {
      const x = tree ? (i % 2 ? 990 : 410) : 130 + i * spacing;
      const y = tree ? 85 + Math.floor(i / 2) * 110 : 230;
      const opacity = interpolate(progress, [i / Math.max(1, labels.length) * 0.6, i / Math.max(1, labels.length) * 0.6 + 0.15], [0, 1], clamp);
      return <g key={i} opacity={opacity}>
        {tree && <path d={`M700 ${y+55} Q${x} ${y+55} ${x} ${y}`} fill="none" stroke={color} strokeWidth="2"/>}
        <circle cx={x} cy={y} r={scene.kind === 'timeline' ? 9 : 30} fill={red}/>
        <text x={x} y={y+68} textAnchor="middle" fill={color} fontFamily={sans} fontSize="25">{label}</text>
        <text x={x} y={y-52} textAnchor="middle" fill={red} fontFamily="Georgia, serif" fontSize="22">{String(i+1).padStart(2,'0')}</text>
      </g>;
    })}
  </svg>;
};

export const ArchiveScene: React.FC<{scene: Scene}> = ({scene}) => {
  const frame = useCurrentFrame(); // Relative to this Sequence, not the whole film.
  const duration = scene.duration_frames;
  const progress = interpolate(frame, [0, Math.max(1,duration-1)], [0,1], clamp);
  const fade = interpolate(frame, [0,Math.max(1,Math.min(18,duration/4))], [0,1], clamp);
  const color = scene.dark ? '#F0E6CE' : ink;
  const caption = scene.captions.find(c => frame >= c.start_frame && frame < c.end_frame);
  return <AbsoluteFill style={{backgroundColor: scene.dark ? '#191713' : '#EDE3CA', color, fontFamily: serif, overflow:'hidden'}}>
    <AbsoluteFill style={{backgroundImage:'radial-gradient(ellipse at 35% 42%, transparent 22%, rgba(64,42,19,0.22) 100%), repeating-linear-gradient(7deg, rgba(109,84,47,0.025) 0px, rgba(109,84,47,0.025) 1px, transparent 1px, transparent 4px)', pointerEvents:'none'}}/>
    {scene.image && <AbsoluteFill style={{transform:`scale(${1+progress*0.035}) translateX(${progress*0.6}%)`}}>
      <Img src={staticFile(scene.image)} style={{width:'100%',height:'100%',objectFit:'cover'}}/>
      <AbsoluteFill style={{background:'linear-gradient(transparent 52%, rgba(20,15,10,.78))'}}/>
    </AbsoluteFill>}
    <div style={{position:'absolute', top:'7%',left:'7%', fontSize:22,letterSpacing:4,opacity:.8}}>{scene.chapter}</div>
    <div style={{position:'absolute', top:'12%',left:'7%',width:'86%',fontSize:24,letterSpacing:6,opacity:.5}}>VIBETECH · {board.topic}</div>
    <AbsoluteFill style={{alignItems:'center',justifyContent:'center',padding:'16% 8% 18%',boxSizing:'border-box',opacity:fade,transform:`translateY(${(1-fade)*15}px)`}}>
      {['diagram','timeline','tree'].includes(scene.kind) ? <Diagram scene={scene} progress={interpolate(frame,[0,Math.max(1,duration*.55)],[0,1],clamp)} color={color}/> :
        <div style={{borderTop:`1px solid ${color}`,borderBottom:`1px solid ${color}`,padding:'32px 50px',maxWidth:'90%',textAlign:'center',background: scene.image ? 'rgba(237,227,202,.82)' : 'transparent',color:scene.image?ink:color}}>
          <div style={{fontSize:64,letterSpacing:6,lineHeight:1.5}}>{scene.title}</div>
          {scene.labels.map((label,i)=><div key={i} style={{fontFamily:sans,fontSize:26,marginTop:16,opacity:.72}}>{label}</div>)}
        </div>}
    </AbsoluteFill>
    {['diagram','timeline','tree'].includes(scene.kind) && <div style={{position:'absolute',top:'21%',width:'100%',textAlign:'center',fontSize:46,opacity:fade}}>{scene.title}</div>}
    {caption && <div style={{position:'absolute',bottom:'8%',width:'84%',left:'8%',textAlign:'center',fontSize:32,lineHeight:1.6,whiteSpace:'pre-line',color:scene.image?'#FFF4DB':color,textShadow:scene.image?'0 2px 7px #000':'none'}}>{caption.text}</div>}
    <div style={{position:'absolute',bottom:'3%',left:'7%',fontSize:15,letterSpacing:3,opacity:.55}}>知识的形状 · {scene.id.toUpperCase()}</div>
  </AbsoluteFill>;
};

const Film = () => <AbsoluteFill>{(board.scenes as Scene[]).map(scene =>
  <Sequence key={scene.id} from={scene.start_frame} durationInFrames={scene.duration_frames}>
    <ArchiveScene scene={scene}/>
  </Sequence>)}</AbsoluteFill>;

export const Root = () => {
  if (board.status !== 'ready') throw new Error('storyboard is draft; author and validate it before rendering');
  return <Composition id="VibeTech" component={Film} durationInFrames={board.total_frames} fps={board.fps} width={board.width} height={board.height}/>;
};
