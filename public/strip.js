/* Tekeningen van de strip. Afkomstig uit het prototype. */
/* ---------- anime character drawing (SVG) ---------- */
const LOOKS = [
  {hair:"#2b2d6e", hairHi:"#5a5fc4", eye:"#2f7bd8", skin:"#ffe2cf", outfit:"#3aa676", style:"long"},
  {hair:"#7a3b1d", hairHi:"#c06a3a", eye:"#8a4b22", skin:"#f6d3b8", outfit:"#c9463d", style:"spiky"},
  {hair:"#161616", hairHi:"#555",    eye:"#5b3a1e", skin:"#d9a67e", outfit:"#38405e", style:"short"},
  {hair:"#e8c34a", hairHi:"#fff0a0", eye:"#3c9a6a", skin:"#ffe6d6", outfit:"#7a52b3", style:"bob"},
  {hair:"#c94f7c", hairHi:"#f59fbe", eye:"#a13c6b", skin:"#ffe0cc", outfit:"#2c8a9e", style:"tails"},
  {hair:"#9aa0a8", hairHi:"#dde1e6", eye:"#4a5a70", skin:"#f2cfb3", outfit:"#565656", style:"short"}
];
function hairShape(L){
  const c=L.hair;
  switch(L.style){
    case "long": return `<path d="M24 52 C18 20 82 14 78 52 L82 96 L66 90 L64 56 L36 56 L34 90 L18 96 Z" fill="${c}"/>`;
    case "spiky": return `<path d="M22 50 L18 30 L32 36 L30 16 L44 28 L50 10 L56 28 L70 16 L68 36 L82 30 L78 50 Z" fill="${c}"/>`;
    case "bob": return `<path d="M22 54 C16 18 84 18 78 54 L80 74 L68 72 L66 50 L34 50 L32 72 L20 74 Z" fill="${c}"/>`;
    case "tails": return `<path d="M24 50 C20 20 80 20 76 50 Z" fill="${c}"/><path d="M22 44 C6 50 6 80 14 92 C18 76 20 62 26 54Z M78 44 C94 50 94 80 86 92 C82 76 80 62 74 54Z" fill="${c}"/>`;
    default: return `<path d="M24 50 C20 18 80 18 76 50 L72 40 L60 44 L50 34 L40 44 L28 40 Z" fill="${c}"/>`;
  }
}
function fringe(L){
  return `<path d="M26 46 C30 24 70 24 74 46 L66 40 L60 48 L52 36 L44 48 L38 38 L32 48 Z" fill="${L.hair}"/>
  <path d="M40 28 C46 24 56 24 62 28" stroke="${L.hairHi}" stroke-width="3" fill="none" stroke-linecap="round"/>`;
}
function eyes(L,emo){
  const ink="#1d1b2e";
  if(emo==="blij") return `<path d="M34 58 Q40 50 46 58" stroke="${ink}" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M54 58 Q60 50 66 58" stroke="${ink}" stroke-width="3" fill="none" stroke-linecap="round"/>`+
    (L.brow?`<path d="M34 46 Q40 42.5 46 45.5 M54 45.5 Q60 42.5 66 46" stroke="${L.brow.c}" stroke-width="${L.brow.w}" fill="none" stroke-linecap="round"/>`:"");
  const big = emo==="verbaasd" ? 1.15 : 1;
  const eye = (cx)=>`<ellipse cx="${cx}" cy="58" rx="${6*big}" ry="${8*big}" fill="#fff" stroke="${ink}" stroke-width="2"/>
    <ellipse cx="${cx}" cy="59" rx="${4.4*big}" ry="${6.2*big}" fill="${L.eye}"/>
    <ellipse cx="${cx}" cy="60" rx="${2.2*big}" ry="${3.4*big}" fill="${ink}"/>
    <circle cx="${cx-1.8}" cy="55.5" r="1.8" fill="#fff"/><circle cx="${cx+1.6}" cy="62" r=".9" fill="#fff"/>`;
  /* L.brow (optioneel): {c: kleur, w: dikte} voor figuren met eigen wenkbrauwen; zonder blijft alles zoals het was */
  const bc=L.brow?L.brow.c:ink, bw=(w)=>L.brow?L.brow.w*(w/2.5):w;
  let brows="";
  if(emo==="boos"||emo==="vastberaden") brows=`<path d="M33 46 L46 50 M67 46 L54 50" stroke="${bc}" stroke-width="${bw(3)}" stroke-linecap="round"/>`;
  else if(emo==="bezorgd") brows=`<path d="M34 50 L45 46 M66 50 L55 46" stroke="${bc}" stroke-width="${bw(2.5)}" stroke-linecap="round"/>`;
  else if(emo==="denkend") brows=`<path d="M34 48 L45 48 M55 46 L66 49" stroke="${bc}" stroke-width="${bw(2.5)}" stroke-linecap="round"/>`;
  else if(L.brow) brows=`<path d="M34 46.5 Q40 43.5 46 46 M54 46 Q60 43.5 66 46.5" stroke="${bc}" stroke-width="${L.brow.w}" fill="none" stroke-linecap="round"/>`;
  return eye(40)+eye(60)+brows;
}
function mouth(emo){
  const ink="#1d1b2e";
  return {
    blij:`<path d="M42 74 Q50 84 58 74 Z" fill="#c8434f" stroke="${ink}" stroke-width="2"/>`,
    boos:`<path d="M43 78 Q50 72 57 78" stroke="${ink}" stroke-width="2.5" fill="none"/>`,
    bezorgd:`<path d="M44 77 Q47 74 50 77 Q53 80 56 77" stroke="${ink}" stroke-width="2" fill="none"/>`,
    verbaasd:`<ellipse cx="50" cy="77" rx="4" ry="5" fill="#c8434f" stroke="${ink}" stroke-width="2"/>`,
    denkend:`<path d="M45 77 L55 76" stroke="${ink}" stroke-width="2.5" stroke-linecap="round"/>`,
    vastberaden:`<path d="M42 75 L58 75 L56 79 L44 79 Z" fill="#fff" stroke="${ink}" stroke-width="2"/>`
  }[emo] || `<path d="M45 76 Q50 79 55 76" stroke="${ink}" stroke-width="2.5" fill="none" stroke-linecap="round"/>`;
}
function extras(emo){
  if(emo==="bezorgd") return `<path d="M76 40 Q80 48 76 52 Q72 48 76 40Z" fill="#7cc4f2" stroke="#1d1b2e" stroke-width="1.5"/>`;
  if(emo==="boos") return `<path d="M72 30 l6 4 l-4 2 l6 4 M80 26 l4 6" stroke="#d33" stroke-width="2.5" fill="none"/>`;
  if(emo==="blij") return `<ellipse cx="32" cy="68" rx="5" ry="2.5" fill="#ff9aa8" opacity=".7"/><ellipse cx="68" cy="68" rx="5" ry="2.5" fill="#ff9aa8" opacity=".7"/>`;
  if(emo==="denkend") return `<circle cx="84" cy="30" r="2" fill="#1d1b2e"/><circle cx="90" cy="22" r="3" fill="#1d1b2e"/>`;
  return "";
}
/* character in a 100x120 box */
function character(L,emo){
  if(L.u)return portraitCharacter(L.u,L.outfit,emo,L.accent);
  return `${hairShape(L)}
  <path d="M30 96 Q50 88 70 96 L80 120 L20 120 Z" fill="${L.outfit}" stroke="#1d1b2e" stroke-width="2"/>
  <path d="M44 88 L50 98 L56 88" fill="#fff" stroke="#1d1b2e" stroke-width="1.5"/>
  <path d="M28 52 C28 30 72 30 72 52 C72 74 60 88 50 88 C40 88 28 74 28 52Z" fill="${L.skin}" stroke="#1d1b2e" stroke-width="2"/>
  ${fringe(L)}${eyes(L,emo)}${mouth(emo)}${extras(emo)}`;
}
function avatar(L){return `<svg viewBox="10 10 80 90" aria-hidden="true">${character(L,"neutraal")}</svg>`;}

function esc(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function wrapText(t,max){
  const words=String(t).split(/\s+/);const lines=[];let cur="";
  for(const w of words){ if((cur+" "+w).trim().length>max && cur){lines.push(cur);cur=w;} else cur=(cur+" "+w).trim(); }
  if(cur)lines.push(cur);return lines;
}
const BG = {
  blij:(id)=>`<g stroke="#1d1b2e" stroke-width="1" opacity=".18">${Array.from({length:18},(_,i)=>{const a=i/18*Math.PI*2;return `<line x1="${200+Math.cos(a)*60}" y1="${190+Math.sin(a)*60}" x2="${200+Math.cos(a)*260}" y2="${190+Math.sin(a)*260}"/>`}).join("")}</g>`,
  vastberaden:(id)=>`<g stroke="#1d1b2e" stroke-width="2" opacity=".22">${Array.from({length:24},(_,i)=>{const a=i/24*Math.PI*2;return `<line x1="${200+Math.cos(a)*90}" y1="${190+Math.sin(a)*90}" x2="${200+Math.cos(a)*300}" y2="${190+Math.sin(a)*300}"/>`}).join("")}</g>`,
  bezorgd:(id)=>`<rect width="400" height="300" fill="url(#tone${id})"/>`,
  boos:(id)=>`<rect width="400" height="300" fill="#ffe3e0"/><path d="M0 300 L60 220 L110 260 L170 200 L230 250 L290 190 L350 240 L400 200 L400 300Z" fill="#ffb9b0"/>`,
  denkend:(id)=>`<rect width="400" height="300" fill="url(#tone${id})" opacity=".6"/>`,
  verbaasd:(id)=>BG.vastberaden(id),
  neutraal:(id)=>`<rect width="400" height="300" fill="#f7f6fb"/>`
};
function panelSVG(p,i,lookOf){
  const emo=(p.emotie||"neutraal").toLowerCase();
  const narr=/verteller|voorzitter/i.test(p.spreker||"");
  const L=lookOf(p.spreker);
  const flip=i%2===1;
  /* Tekst altijd volledig in de ballon: kies de grootste letter waarbij het past.
     Tekens per regel zijn ruim geschat (0,62 x lettergrootte), zodat ook een andere
     lettersoort (als de webfont niet laadt) binnen de rand blijft. */
  const fit=(inner,sizes,maxLines)=>{for(const fs of sizes){const ls=wrapText(p.tekst,Math.floor(inner/(fs*0.62)));
      if(ls.length<=maxLines||fs===sizes[sizes.length-1])return {fs,lh:Math.round(fs*1.3),lines:ls};}};
  const bw=250, bx=flip?12:138, by=14;
  const B=narr?fit(336,[18,16,14,13],4):fit(bw-26,[16,15,14,13],4);
  const lines=B.lines, bh=24+lines.length*B.lh;
  const text=lines.map((l,k)=>`<tspan x="${bx+bw/2}" dy="${k?B.lh:0}">${esc(l)}</tspan>`).join("");
  const tailX=flip?bx+bw-44:bx+44;
  const charX=flip?250:40, charY=Math.max(110,Math.min(168,by+bh+40));
  let fig="";
  if(narr){
    fig=`<g transform="translate(140 ${Math.max(150,16+bh+14)}) scale(1.1)"><rect x="0" y="40" width="110" height="60" fill="#c9b48a" stroke="#1d1b2e" stroke-width="2"/><rect x="10" y="20" width="90" height="24" fill="#e7d9b8" stroke="#1d1b2e" stroke-width="2"/><circle cx="55" cy="10" r="10" fill="#e7c34a" stroke="#1d1b2e" stroke-width="2"/></g>`;
  } else {
    fig=`<g transform="translate(${charX} ${charY}) scale(1.55)${flip?" translate(100 0) scale(-1 1)":""}">${character(L,emo)}</g>`;
  }
  const bubble = narr
    ? `<rect x="20" y="16" width="360" height="${bh}" fill="#fff8d6" stroke="#1d1b2e" stroke-width="2.5"/>
       <text x="200" y="${16+12+B.fs}" text-anchor="middle" font-family="Atkinson Hyperlegible,system-ui,sans-serif" font-size="${B.fs}" font-weight="700" fill="#1d1b2e">${lines.map((l,k)=>`<tspan x="200" dy="${k?B.lh:0}">${esc(l)}</tspan>`).join("")}</text>`
    : `<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="${Math.min(36,bh/2)}" fill="#fff" stroke="#1d1b2e" stroke-width="2.5"/>
       <path d="M${tailX-10} ${by+bh-2} L${flip?tailX+28:tailX-28} ${by+bh+30} L${tailX+12} ${by+bh-2}" fill="#fff" stroke="#1d1b2e" stroke-width="2.5" stroke-linejoin="round"/>
       <path d="M${tailX-8} ${by+bh-2} L${tailX+10} ${by+bh-2}" stroke="#fff" stroke-width="4"/>
       <text x="${bx+bw/2}" y="${by+10+B.fs}" text-anchor="middle" font-family="Atkinson Hyperlegible,system-ui,sans-serif" font-size="${B.fs}" font-weight="700" fill="#1d1b2e">${text}</text>`;
  const name = narr?"":`<g><rect x="${flip?240:10}" y="266" width="150" height="24" fill="#1d1b2e"/><text x="${flip?315:85}" y="283" text-anchor="middle" font-family="Zen Maru Gothic,system-ui,sans-serif" font-size="14" font-weight="900" fill="#fff">${esc(p.spreker).slice(0,20)}</text></g>`;
  return `<svg viewBox="0 0 400 300" role="img" aria-label="${esc((p.spreker||"")+": "+p.tekst)}">
    <defs><pattern id="tone${i}" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.4" fill="#1d1b2e" opacity=".25"/></pattern>
    <clipPath id="clip${i}"><rect width="400" height="300"/></clipPath></defs>
    <g clip-path="url(#clip${i})"><rect width="400" height="300" fill="#fff"/>${(BG[emo]||BG.neutraal)(i)}${fig}</g>
    ${bubble}${name}
    <rect x="1.5" y="1.5" width="397" height="297" fill="none" stroke="#1d1b2e" stroke-width="3"/>
  </svg>`;
}


/* Vast figuurtje per persoon: kleding volgt de partij, haar en ogen de persoon. */
const PARTY_COLORS=["#3aa676","#c9463d","#38405e","#7a52b3","#2c8a9e","#d08a1f","#565656","#b04a86","#3b6fd1","#8a6d3b"];
/* Partijkleuren: [kleding, accent (das, sjaal)]. Uit de huisstijl van de partij waar die bekend is
   (PRO, ChristenUnie, Groep Markuszower/DNA); de overige zijn benaderingen van logo en campagnekleur. */
const PARTIJ_KLEUR={
  "D66":["#00a640","#0b5e2e"], "VVD":["#1a3f9e","#ff7a00"], "PRO":["#01a747","#d81f27"],
  "PVV":["#12306f","#d11f2e"], "CDA":["#007b5f","#9bc31f"], "JA21":["#1d2a5a","#2aa8e0"],
  "FVD":["#7d1a1f","#e8d9b5"], "Groep Markuszower":["#25abe3","#c01718"], "BBB":["#8db82a","#0f5a35"],
  "DENK":["#00a9a5","#ffffff"], "SGP":["#e8691e","#ffffff"], "SP":["#e3001b","#ffffff"],
  "PvdD":["#0b6b34","#ffffff"], "ChristenUnie":["#3e8bd5","#eaab00"], "50PLUS":["#8e2a8c","#ffffff"],
  "Volt":["#502379","#fdc220"], "Lid Keijzer":["#5b5f6b","#c9ccd3"]
};
const KABINET_KLEUR=["#2b2b3a","#8a90a0"];
function hash(s){let h=2166136261;for(const c of String(s)){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}return h>>>0;}
function makeLook(id,fractie,u){
  const [outfit,accent]=fractie?(PARTIJ_KLEUR[fractie]||[PARTY_COLORS[hash(fractie)%PARTY_COLORS.length],"#ffffff"]):KABINET_KLEUR;
  if(u)return {u,outfit,accent};
  return {...LOOKS[hash(id)%LOOKS.length],outfit,accent};
}
function renderStrip(d){
  const looks={};for(const s of d.sprekers)looks[s.label]=makeLook(s.id,s.fractie,s.uiterlijk);
  const lookOf=n=>looks[n]||LOOKS[0];
  document.querySelectorAll("[data-avatar]").forEach(el=>{const s=d.sprekers.find(x=>x.id===el.dataset.avatar);el.innerHTML=avatar(makeLook(el.dataset.avatar,el.dataset.fractie,s&&s.uiterlijk));});
  const taal=document.documentElement.dataset.taal==="makkelijk"?"makkelijk":"normaal";
  document.getElementById("strip").innerHTML=d.strip.map(p0=>({...p0,tekst:typeof p0.tekst==="object"?(p0.tekst[taal]||p0.tekst.normaal||p0.tekst.makkelijk):p0.tekst})).map((p,i)=>`<figure class="panel" style="margin:0">${panelSVG(p,i,lookOf)}<figcaption class="src"><b>Echt gezegd${p.spreker==="Verteller"?"":" door "+esc(p.wie)}:</b> “${esc(p.citaat)}”</figcaption></figure>`).join("");
}

/* Figuur getekend naar kenmerken uit het officiële portret (data/uiterlijk.json).
   Bewust eenvoudig: kapsel, haarkleur, bril, baard, huid en leeftijd. Geen karikatuur. */
const HAIR={platinablond:"#f2e6b6",zwart:"#1c1a1f",donkerbruin:"#3b2a20",bruin:"#6b4630",lichtbruin:"#9c6f45",blond:"#e2bd6b",rood:"#a8482a",grijs:"#9a9ca3",wit:"#e4e4e8",
  donkerblond:"#b89258",rossig:"#b5653a","peper-zout":"#6e6c70",zilver:"#c3c6cd"};
const SKIN={licht:"#ffe2cf",middel:"#e3b08a",donker:"#9c6a46"};
const HS='stroke="#1d1b2e" stroke-width="1.5" stroke-linejoin="round"';
const SHINE=(d)=>`<path d="${d}" stroke="#fff" stroke-opacity=".35" stroke-width="2.5" fill="none" stroke-linecap="round"/>`;
const curls=(pts,r,c)=>pts.map(([x,y])=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${c}"/>`).join("");
function hairBack(k,c){
  switch(k){
    case "half-lang": return `<path d="M23 54 C17 16 83 16 77 54 L79 84 L65 82 L64 54 L36 54 L35 82 L21 84Z" fill="${c}"/>`;
    case "half-lang-krul": return `<path d="M23 54 C17 16 83 16 77 54 L78 80 L64 80 L64 54 L36 54 L36 80 L22 80Z" fill="${c}"/>`+curls([[21,58],[19,72],[24,82],[79,58],[81,72],[76,82]],8,c);
    case "half-lang-golf": return `<path d="M23 54 C17 16 83 16 77 54 C81 62 76 68 80 76 C82 80 78 84 72 84 L64 82 L64 54 L36 54 L36 82 L28 84 C22 84 18 80 20 76 C24 68 19 62 23 54Z" fill="${c}" ${HS}/>`;
    case "lang": return `<path d="M22 54 C15 14 85 14 78 54 L83 104 L64 100 L64 56 L36 56 L36 100 L17 104Z" fill="${c}"/>`;
    case "lang-krul": return `<path d="M22 54 C15 14 85 14 78 54 L82 100 L64 98 L64 56 L36 56 L36 98 L18 100Z" fill="${c}"/>`+curls([[20,58],[17,74],[19,90],[80,58],[83,74],[81,90],[26,98],[74,98]],8,c);
    case "vlechten": return `<path d="M22 54 C15 14 85 14 78 54 L82 104 L64 100 L64 56 L36 56 L36 100 L18 104Z" fill="${c}"/>`+
      [22,28,72,78].map(x=>`<path d="M${x} 60 l3 6 l-3 6 l3 6 l-3 6 l3 6 l-3 6" stroke="#000" stroke-opacity=".35" stroke-width="1.4" fill="none"/>`).join("");
    case "staart": return `<path d="M68 40 C88 44 90 72 80 88 C78 72 76 58 68 48Z" fill="${c}" ${HS}/>`;
    case "lang-golf": return `<path d="M22 54 C15 14 85 14 78 54 C84 62 77 70 83 80 C88 90 79 96 84 106 L64 100 L64 56 L36 56 L36 100 L16 106 C21 96 12 90 17 80 C23 70 16 62 22 54Z" fill="${c}" ${HS}/>`;
    case "bob": return `<path d="M22 54 C16 18 84 18 78 54 L80 76 C74 80 69 79 66 76 L64 54 L36 54 L34 76 C31 79 26 80 20 76Z" fill="${c}" ${HS}/>`;
    case "staart-hoog": return `<path d="M60 22 C76 17 85 36 80 60 C76 47 70 36 61 31Z" fill="${c}" ${HS}/>`;
    default: return "";
  }
}
function hairFront(k,c){
  switch(k){
    case "kort": return `<path d="M26 56 C18 12 82 12 74 56 L72 46 C70 40 67 37 63 35 C52 39 41 39 35 35 C31 38 29 44 28 48 Z" fill="${c}" ${HS}/>`+SHINE("M38 24 C46 20 58 20 64 25");
    case "kort-scheiding": return `<path d="M26 56 C18 12 82 12 74 56 L72 44 C66 36 54 33 41 35 C46 31 49 27 51 24 C42 27 34 33 30 41 L28 48 Z" fill="${c}" ${HS}/><path d="M51 24 C49 27 46 31 41 35" stroke="#1d1b2e" stroke-width="1.2" fill="none"/>`+SHINE("M56 21 C62 22 68 26 70 32");
    case "kort-kuif": return `<path d="M26 56 C19 20 36 12 54 13 C72 14 82 26 74 56 L72 46 C70 40 66 37 60 37 C50 39 40 37 34 37 C30 40 29 44 28 48 Z" fill="${c}" ${HS}/>`+SHINE("M40 20 C48 16 60 16 66 21");
    case "kort-kort": return `<path d="M27 54 C22 20 78 20 73 54 L71 45 C68 41 62 39 50 40 C38 39 32 41 29 45 Z" fill="${c}" ${HS}/>`+SHINE("M40 26 C46 23 56 23 62 26");
    case "kort-inham": return `<path d="M26 56 C18 12 82 12 74 56 L72 44 C70 36 66 31 62 32 C58 36 54 38 50 38 C46 38 42 36 38 32 C34 31 30 36 28 44 Z" fill="${c}" ${HS}/>`+SHINE("M40 22 C46 19 56 19 62 22");
    case "kaal-krul": return curls([[26,46],[24,58],[25,70],[28,82],[74,46],[76,58],[75,70],[72,82]],7.5,c);
    case "knot": return `<circle cx="50" cy="20" r="10" fill="${c}" ${HS}/><path d="M27 50 C26 24 74 24 73 50 C70 40 62 35 50 34 C38 35 30 40 27 50Z" fill="${c}" ${HS}/>`+SHINE("M42 28 C47 26 55 26 60 28");
    case "kort-stekels": return `<path d="M26 56 L24 34 L32 31 L33 19 L42 25 L47 12 L54 23 L62 14 L64 27 L74 24 L76 38 L74 56 L72 46 C68 39 60 37 50 39 C42 37 34 37 30 42 L28 48 Z" fill="${c}" ${HS}/>`;
    case "kort-golf": return `<path d="M26 56 C16 12 84 10 74 56 L72 46 C71 39 67 34 62 33 C59 40 52 34 47 39 C42 33 36 38 33 36 C30 40 29 44 28 48 Z" fill="${c}" ${HS}/>`+SHINE("M36 25 C44 18 58 18 66 24");
    case "kort-krul": return curls([[29,46],[30,35],[38,26],[49,22],[60,24],[69,31],[72,43],[42,35],[56,34]],8,c);
    case "opgeschoren": return `<path d="M27 54 C23 22 77 22 73 54 L71 45 C66 39 34 39 29 45 Z" fill="${c}" fill-opacity=".85" ${HS}/>`;
    case "kort-dun": return `<path d="M26 58 C24 44 26 36 31 32 L33 60 L28 60Z M74 58 C76 44 74 36 69 32 L67 60 L72 60Z" fill="${c}"/><path d="M30 42 C32 24 68 24 70 42 C64 36 56 34 50 35 C44 34 36 36 30 42Z" fill="${c}" fill-opacity=".85" ${HS}/>`;
    case "half-lang-golf": return `<path d="M27 50 C26 30 34 22 44 22 C40 30 46 34 52 30 C56 24 70 24 73 50 C68 42 62 36 56 36 C48 42 36 42 27 50Z" fill="${c}"/>`;
    case "half-lang": case "lang": return `<path d="M27 50 C28 22 72 22 73 50 C66 40 58 36 54 32 C48 40 36 44 27 50Z" fill="${c}"/>`;
    case "vlechten": return `<path d="M27 50 C28 24 72 24 73 50 C66 40 54 34 50 32 C46 34 34 40 27 50Z" fill="${c}"/>`;
    case "staart": return `<path d="M27 50 C26 22 74 22 73 50 C70 40 62 34 50 33 C38 34 30 40 27 50Z" fill="${c}" ${HS}/>`+SHINE("M40 27 C46 24 56 24 62 27");
    case "lang-krul": case "half-lang-krul": return curls([[30,44],[34,33],[43,27],[54,26],[64,30],[70,40]],7.5,c);
    case "kaal-rand": return `<path d="M27 56 C26 46 28 42 31 41 L33 62 L28 62Z M73 56 C74 46 72 42 69 41 L67 62 L72 62Z" fill="${c}"/>`;
    case "achterover": return `<path d="M26 56 C21 26 35 20 52 20 C69 20 80 28 74 56 L72 46 C70 41 66 39 61 39 C55 38 45 38 39 39 C34 39 30 41 28 46 Z" fill="${c}" ${HS}/><path d="M40 38 C42 32 46 27 53 24 M50 38 C52 32 56 28 62 26 M60 38 C62 34 65 31 69 30" stroke="#1d1b2e" stroke-opacity=".3" stroke-width="1.1" fill="none" stroke-linecap="round"/>`;
    case "kort-middenscheiding": return `<path d="M26 56 C18 12 82 12 74 56 L72 45 C68 40 58 37 50 38 C42 37 32 40 28 45 Z" fill="${c}" ${HS}/><path d="M50 38 C50 32 50 27 50 22" stroke="#1d1b2e" stroke-width="1.2" fill="none"/>`+SHINE("M56 22 C62 23 67 27 69 32");
    case "pixie": return `<path d="M26 56 C18 14 82 12 74 56 L72 44 C68 40 62 39 56 40 C48 42 38 44 30 52 L28 50 Z" fill="${c}" ${HS}/>`+SHINE("M38 24 C46 19 58 19 64 24");
    case "afro-kort": return curls([[28,48],[27,38],[33,29],[42,23],[52,21],[62,24],[69,31],[73,40],[72,49],[38,32],[50,29],[61,32]],6.5,c);
    case "bob": return `<path d="M26 54 C20 16 80 16 74 54 L72 44 C66 37 57 35 47 37 C40 39 33 43 28 50 Z" fill="${c}" ${HS}/>`+SHINE("M40 25 C46 22 56 22 62 25");
    case "lang-golf": return `<path d="M27 50 C28 22 72 22 73 50 C67 40 60 36 54 32 C48 40 36 44 27 50Z" fill="${c}"/>`;
    case "staart-hoog": return `<path d="M26 54 C20 16 80 16 74 54 L72 45 C68 40 60 38 50 38 C40 38 32 40 28 45 Z" fill="${c}" ${HS}/>`+SHINE("M40 25 C46 22 56 22 62 25");
    default: return ""; /* kaal */
  }
}
function beard(b,c){
  const d="M29 64 C31 84 42 91 50 91 C58 91 69 84 71 64 C68 75 60 80 50 80 C40 80 32 75 29 64Z";
  if(b==="kort")return `<path d="${d}" fill="${c}"/><path d="M42 73 Q50 70 58 73 L58 75 Q50 73 42 75Z" fill="${c}"/>`;
  if(b==="stoppel")return `<path d="${d}" fill="${c}" opacity=".3"/>`;
  return "";
}
/* Pony vervangt het voorhaar (alleen bij halflang/lang haar). */
function pony(k,c){
  switch(k){
    case "recht": return `<path d="M26 52 C23 19 77 19 74 52 L73 45 C64 47 36 47 27 45 Z" fill="${c}" ${HS}/>`+SHINE("M40 26 C46 23 56 23 62 26");
    case "schuin": return `<path d="M26 54 C23 19 77 19 74 54 L73 44 C64 42 50 44 40 46 C34 47 29 50 26 54Z" fill="${c}" ${HS}/>`+SHINE("M40 26 C46 23 56 23 62 26");
    case "gordijn": return `<path d="M26 54 C23 19 77 19 74 54 C72 47 66 43 58 43 C54 43 51 41 50 38 C49 41 46 43 42 43 C34 43 28 47 26 54Z" fill="${c}" ${HS}/>`+SHINE("M40 26 C46 23 56 23 62 26");
    default: return "";
  }
}
const MONTUUR={zwart:"#1d1b2e",bruin:"#6b4630",goud:"#b8922e",zilver:"#8e949c",randloos:"#9aa3ad"};
function glasses(g,m){
  const col=MONTUUR[m]||MONTUUR.zwart, w=m==="randloos"?1.1:2.2, br=m==="randloos"?1.4:2;
  const st=`stroke="${col}" stroke-width="${w}" fill="#fff" fill-opacity=".15"`;
  const brug=(y)=>`<path d="M48.5 ${y} L51.5 ${y}" stroke="${col}" stroke-width="${br}"/>`;
  if(g==="rechthoek")return `<rect x="31.5" y="51" width="17" height="14" rx="3" ${st}/><rect x="51.5" y="51" width="17" height="14" rx="3" ${st}/>`+brug(56);
  if(g==="rond")return `<circle cx="40" cy="58" r="8.8" ${st}/><circle cx="60" cy="58" r="8.8" ${st}/>`+brug(57);
  if(g==="ovaal")return `<ellipse cx="40" cy="58" rx="9" ry="7.2" ${st}/><ellipse cx="60" cy="58" rx="9" ry="7.2" ${st}/>`+brug(57);
  return "";
}
function shade(hex,f){const n=parseInt(hex.slice(1),16);const ch=(v)=>Math.max(0,Math.min(255,Math.round(v*f)));
  return "#"+[ch(n>>16&255),ch(n>>8&255),ch(n&255)].map(v=>v.toString(16).padStart(2,"0")).join("");}
/* Kleding. "shirt" is het oorspronkelijke figuur. Partijkleur = kleding, accent = das. */
const ONDER={wit:"#ffffff",licht:"#e6d8c3",donker:"#2e3142"};
function clothes(k,outfit,accent,onder,skin){
  const ink="#1d1b2e", body=`<path d="M30 96 Q50 88 70 96 L80 120 L20 120 Z" fill="${outfit}" stroke="${ink}" stroke-width="2"/>`;
  const rev=shade(outfit,.78), ond=ONDER[onder]||ONDER.wit;
  const revers=`<path d="M41 90 L50 112 L45 101 L36 96 Z M59 90 L50 112 L55 101 L64 96 Z" fill="${rev}" stroke="${ink}" stroke-width="1.3" stroke-linejoin="round"/>`;
  switch(k){
    case "colbert-das": return body+`<path d="M41 90 L50 112 L59 90 Z" fill="#fff" stroke="${ink}" stroke-width="1.3"/>
      <path d="M48.3 93.5 L51.7 93.5 L53 105 L50 109 L47 105 Z" fill="${accent}" stroke="${ink}" stroke-width="1"/><path d="M47.6 89.5 L52.4 89.5 L51.6 93.8 L48.4 93.8 Z" fill="${accent}" stroke="${ink}" stroke-width="1"/>`+revers;
    case "colbert-open": return body+`<path d="M41 90 L50 108 L59 90 Z" fill="#fff" stroke="${ink}" stroke-width="1.3"/><path d="M44 88 L50 99 L56 88" fill="${skin}" stroke="${ink}" stroke-width="1.2"/>
      <path d="M43 88 L47 96 L42 93 Z M57 88 L53 96 L58 93 Z" fill="#fff" stroke="${ink}" stroke-width="1"/>`+revers;
    case "colbert-top": return body+`<path d="M41 90 L50 112 L59 90 Z" fill="${ond}" stroke="${ink}" stroke-width="1.3"/><path d="M43 89 Q50 95 57 89" fill="${skin}" stroke="${ink}" stroke-width="1.1"/>`+revers;
    case "blouse": return body+`<path d="M42 89 Q50 99 58 89 Z" fill="${skin}" stroke="${ink}" stroke-width="1.3"/><path d="M42 89 Q50 99 58 89" stroke="${shade(outfit,1.25)}" stroke-width="2" fill="none"/>`;
    case "trui": return body+`<path d="M42 89 Q50 95 58 89" stroke="${rev}" stroke-width="3" fill="none"/>`;
    case "coltrui": return body;
    default: return body+`<path d="M44 88 L50 98 L56 88" fill="#fff" stroke="${ink}" stroke-width="1.5"/>`;
  }
}
/* Col van de coltrui komt over de kin heen; daarom apart, na het gezicht getekend. */
function colKraag(k,outfit){
  if(k!=="coltrui")return "";
  return `<path d="M40 86 Q50 92 60 86 L61 95 Q50 101 39 95 Z" fill="${outfit}" stroke="#1d1b2e" stroke-width="1.5"/><path d="M41 91 Q50 96 59 91" stroke="${shade(outfit,.75)}" stroke-width="1.2" fill="none"/>`;
}
function earrings(k){
  if(k==="knopje")return `<circle cx="28.6" cy="68" r="1.7" fill="#e9d38a" stroke="#1d1b2e" stroke-width=".8"/><circle cx="71.4" cy="68" r="1.7" fill="#e9d38a" stroke="#1d1b2e" stroke-width=".8"/>`;
  if(k==="ring")return `<circle cx="28.4" cy="71" r="2.6" fill="none" stroke="#c9a640" stroke-width="1.3"/><circle cx="71.6" cy="71" r="2.6" fill="none" stroke="#c9a640" stroke-width="1.3"/>`;
  return "";
}
const OOG={bruin:"#5a4636",blauw:"#4f7fb0",groen:"#5d8a5a",grijs:"#7a8794"};
const JAW={
  smal:"M30 52 C30 30 70 30 70 52 C70 74 60 89 50 89 C40 89 30 74 30 52Z",
  rond:"M27 53 C27 30 73 30 73 53 C73 76 62 87 50 87 C38 87 27 76 27 53Z",
  hoekig:"M28 52 C28 30 72 30 72 52 C72 68 70 77 63 83 C58 87 54 88 50 88 C46 88 42 87 37 83 C30 77 28 68 28 52Z"
};
const BROW_W={dun:1.6,normaal:2.3,dik:3.2};
/* Figuur getekend naar kenmerken. Nieuwe velden zijn optioneel; zonder die velden ziet het figuur er uit zoals voorheen
   (alleen de kledingkleur volgt nu de echte partijkleur). */
function portraitCharacter(u,outfit,emo,accent){
  const c=HAIR[u.haarkleur]||HAIR.bruin, skin=SKIN[u.huid]||SKIN.licht, ink="#1d1b2e";
  const L={eye:OOG[u.oogkleur]||OOG.bruin};
  if(u.wenkbrauw&&BROW_W[u.wenkbrauw])L.brow={c:["blond","platinablond","wit","zilver","grijs","donkerblond"].includes(u.haarkleur)?shade(c,.7):shade(c,.85),w:BROW_W[u.wenkbrauw]};
  const lashes=u.gezicht==="v"?`<path d="M33 52 l-3 -2 M35 50.5 l-2 -3 M67 52 l3 -2 M65 50.5 l2 -3" stroke="${ink}" stroke-width="1.8" stroke-linecap="round"/>`:"";
  const age=u.leeftijd==="ouder"?`<path d="M34 68 q6 2 11 0 M55 68 q6 2 11 0" stroke="#b88a72" stroke-width="1.3" fill="none"/>`:"";
  const jaw=JAW[u.gezichtsvorm]||(u.gezicht==="m"?"M28 52 C28 30 72 30 72 52 C72 72 62 88 50 88 C38 88 28 72 28 52Z":"M28 52 C28 30 72 30 72 52 C72 74 60 87 50 87 C40 87 28 74 28 52Z");
  const back=u.volume==="vol"?`<g transform="translate(50 0) scale(1.1 1) translate(-50 0)">${hairBack(u.kapsel,c)}</g>`:hairBack(u.kapsel,c);
  const front=u.pony&&u.pony!=="geen"?pony(u.pony,c):hairFront(u.kapsel,c);
  /* volume "plat": voorhaar lager (bovenkant zakt, haarlijn blijft); smal gezicht: voorhaar iets smaller */
  const fit=(x)=>{const sy={plat:.86,"extra-plat":.76}[u.volume];if(sy)x=`<g transform="translate(0 56) scale(1 ${sy}) translate(0 -56)">${x}</g>`;
    return u.gezichtsvorm==="smal"?`<g transform="translate(50 0) scale(.95 1) translate(-50 0)">${x}</g>`:x;};
  /* slapen "bedekt": laag haar achter het gezicht, zodat er bij de slapen geen wit tussen haar en gezicht valt */
  const cap=u.slapen==="bedekt"?`<path d="M26 58 C18 12 82 12 74 58 Z" fill="${c}"/>`:"";
  return `${back}${cap}
  ${clothes(u.kleding,outfit,accent||"#ffffff",u.onder,skin)}
  <path d="${jaw}" fill="${skin}" stroke="${ink}" stroke-width="2"/>
  ${colKraag(u.kleding,outfit)}${age}${beard(u.baard,c)}${earrings(u.oorbel)}${fit(u.spiegel?`<g transform="translate(100 0) scale(-1 1)">${front}</g>`:front)}${eyes(L,emo)}${lashes}${glasses(u.bril,u.montuur)}${mouth(emo)}${extras(emo)}`;
}
