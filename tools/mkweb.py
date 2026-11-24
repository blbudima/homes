"""Turn the satellite edition of the Home Hunt Map into the phone web version
(location dot, Directions, drive time, nearest-first), before it gets password-locked.
Usage: python3 mkweb.py <Home-Hunt-Map-Satellite.html> <out.html>"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PHONE_CSS = open(os.path.join(HERE, 'phone.css'), encoding='utf-8').read()
PHONE_JS = open(os.path.join(HERE, 'phone.js'), encoding='utf-8').read()

src, out = sys.argv[1], sys.argv[2]
t = open(src, encoding='utf-8').read()

def rep(old, new, count=1):
    global t
    n = t.count(old)
    if n != count:
        raise SystemExit('expected %d of %r, found %d' % (count, old[:80], n))
    t = t.replace(old, new)

asof = re.search(r'Sheet data as of ([^<]+?)\.</p>', t).group(1)

# ---- head
rep('<title>Home Hunt Map (Satellite)</title>', '''<title>Home Hunt Map</title>
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#f6f5f1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141716" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Home Hunt">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="apple-touch-icon" href="icon-180.png">
<script>try{if(matchMedia('(max-width: 759px)').matches)document.documentElement.classList.add('phone')}catch(e){}</script>''')

# ---- styles
CSS = '''
:root{--you:#1a73e8;--youRing:#ffffff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--you:#5b9cff;--youRing:#101312}}
:root[data-theme="dark"]{--you:#5b9cff;--youRing:#101312}
::selection{background:var(--red);color:#fff}
[hidden]{display:none!important}
.upd{font-size:13px;color:var(--muted);margin:6px 0 0;font-variant-numeric:tabular-nums}
.you{position:absolute;left:0;top:0;width:18px;height:18px;border-radius:50%;background:var(--you);border:3px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.45);transform:translate(-50%,-50%)}
.you::after{content:"";position:absolute;inset:-9px;border-radius:50%;border:2px solid var(--you);opacity:0;animation:youping 2.4s cubic-bezier(.16,1,.3,1) infinite}
@keyframes youping{0%{transform:scale(.4);opacity:.7}100%{transform:scale(1.5);opacity:0}}
.locctl{background:var(--panel);border:1px solid var(--line);border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.25);overflow:hidden}
.locctl button{display:grid;place-items:center;width:40px;height:40px;border:0;background:transparent;color:var(--ink);cursor:pointer;padding:0}
.locctl button svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round}
.locctl button[aria-pressed="true"]{color:var(--you)}
.locctl button[aria-pressed="true"] .dot{fill:var(--you);stroke:none}
.locctl button.busy svg{animation:locbusy 1.1s ease-in-out infinite alternate}
@keyframes locbusy{from{opacity:1}to{opacity:.35}}
.locctl button:focus-visible{outline:2px solid var(--you);outline-offset:-3px}
#map.pop-narrow .locctl,#map.pop-narrow .basectl{visibility:hidden}
.locnote{display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;font-size:14px;color:var(--muted);margin:-4px 0 0}
.locnote b{color:var(--ink)}
.locnote .err{color:var(--bad);font-weight:700}
.linkbtn{border:0;background:none;padding:0;font:700 14px/1.4 var(--body);color:var(--tB);text-decoration:underline;text-underline-offset:3px;cursor:pointer}
.pp-you{margin-top:12px;padding:10px 12px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg)}
.pp-dist{font-size:14px;color:var(--muted)}
.pp-dist b{color:var(--ink);font-variant-numeric:tabular-nums}
.pp-acts{display:flex;flex-wrap:wrap;gap:8px;margin-top:9px}
.btn{display:inline-flex;align-items:center;gap:6px;min-height:38px;padding:0 12px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--ink);font:700 14px/1 var(--body);text-decoration:none;cursor:pointer}
.leaflet-container a.btn{color:var(--ink)}
.leaflet-container a.btn.primary,.btn.primary{background:var(--chipOn);border-color:var(--chipOn);color:var(--chipOnInk)}
.btn svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}
.btn:hover{text-decoration:none;filter:brightness(1.08)}
.btn:focus-visible{outline:2px solid var(--you);outline-offset:2px}
.btn[disabled]{opacity:.6;cursor:progress}
.pp-drive{font-size:14px;margin-top:8px;color:var(--muted)}
.pp-drive:empty{display:none}
.pp-drive b{color:var(--ink);font-variant-numeric:tabular-nums}
.dist{font-size:12.5px;font-weight:700;color:var(--you);font-variant-numeric:tabular-nums}
'''
rep('.leaflet-control-attribution{font-size:10px}\n</style>', '.leaflet-control-attribution{font-size:10px}\n' + CSS + PHONE_CSS + '</style>')

# ---- markup
rep('or tap a marker or a row for details.',
    'or tap a marker or a row for details. Tap the target button on the map to see where you are; each home\'s pop-up has Directions and the drive time from you.')
rep('</p>\n  </header>', '</p>\n    <p class="upd">Sheet data as of ' + asof + '</p>\n  </header>')
rep('<div class="grp" id="f-zip"><span>Show</span></div>',
    '<div class="grp" id="f-zip"><span>Show</span></div>\n    <div class="grp" id="f-ord"><span>Order</span></div>')
rep('<div id="map" role="region" aria-label="Map of homes"></div>',
    '<div id="map" role="region" aria-label="Map of homes"></div>\n  <div class="locnote" id="locnote" aria-live="polite" hidden></div>')
rep('This is the satellite edition: use the Satellite / Simple map switch at the top right of the map.',
    'Use the Satellite / Simple map switch at the top right of the map.')
rep('Sheet data as of ' + asof + '.</p>',
    'Your location stays on your phone: the page only uses it to draw the blue dot and measure distances, and sends it to the OpenStreetMap routing service (OSRM) only when you tap Drive time. Drive times don\'t include traffic; Directions opens Google Maps, which does. Sheet data as of ' + asof + '.</p>')

# ---- pop-up: the "from you" block right under the price
rep("'<div class=\"pp-sub\">Monthly = loan, tax, insurance, upkeep and HOA ($450k down, fixed rate)</div>'+",
    "'<div class=\"pp-sub\">Monthly = loan, tax, insurance, upkeep and HOA ($450k down, fixed rate)</div>'+\n  youBlock(h)+")

# ---- table: distance under the address, and nearest-first order
rep("Satellite ↗</a></div>':'')+'</td>'+", "Satellite ↗</a></div>':'')+distTag(h)+'</td>'+")
rep("<b>'+esc(h.mo)+'</b> a month", "<b>'+esc(String(h.mo).replace(/\\/mo$/,''))+'</b> a month")
rep("const rows=vis.filter(h=>h.tab===t).sort((a,b)=>a.rank-b.rank);",
    "const rows=vis.filter(h=>h.tab===t).sort(rowSort);")

JS = r'''
// ---- you are here (location), directions and drive time
const ICON={
  loc:'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="6.5"/><circle class="dot" cx="12" cy="12" r="2.4"/><path d="M12 2v3.5M12 18.5V22M2 12h3.5M18.5 12H22"/></svg>',
  nav:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 11.2 20 4l-7.2 16.5-2-7.3z"/></svg>',
  car:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 16.5V13l2-5.2A2 2 0 0 1 7.9 6.5h8.2a2 2 0 0 1 1.9 1.3L20 13v3.5z"/><path d="M4 13h16"/><path d="M6 16.5V19M18 16.5V19"/><circle cx="7.5" cy="14.8" r=".6"/><circle cx="16.5" cy="14.8" r=".6"/></svg>'
};
state.order='rank';
const you={pos:null,watch:null,center:false,marker:null,circle:null,waiters:[],lastRender:null};
const lsGet=k=>{try{return localStorage.getItem(k)}catch(e){return null}};
const lsSet=(k,v)=>{try{v==null?localStorage.removeItem(k):localStorage.setItem(k,v)}catch(e){}};
function miles(a,b){const R=3958.8,r=Math.PI/180,dLat=(b.lat-a.lat)*r,dLng=(b.lng-a.lng)*r;
  const s=Math.sin(dLat/2)**2+Math.cos(a.lat*r)*Math.cos(b.lat*r)*Math.sin(dLng/2)**2;return 2*R*Math.asin(Math.sqrt(s))}
const fmtMi=m=>m<0.1?'under 0.1 mi':(m<10?m.toFixed(1):String(Math.round(m)))+' mi';
const fmtMin=n=>n<60?n+' min':Math.floor(n/60)+' hr'+(n%60?' '+(n%60)+' min':'');
const homeMi=h=>you.pos&&h.lat!=null?miles(you.pos,h):null;
const gUrl=h=>'https://www.google.com/maps/dir/?api=1&destination='+h.lat+','+h.lng+'&travelmode=driving';
const aUrl=h=>'https://maps.apple.com/?daddr='+h.lat+','+h.lng+'&dirflg=d';
function rowSort(a,b){if(state.order==='near'&&you.pos){const da=homeMi(a),db=homeMi(b);
  if(da!=null||db!=null)return (da==null?1e9:da)-(db==null?1e9:db)}return a.rank-b.rank}
function distTag(h){const m=homeMi(h);return m==null?'':'<div class="dist">'+fmtMi(m)+' away</div>'}
function distLine(h){const m=homeMi(h);
  return m!=null?'<b>'+fmtMi(m)+'</b> from you in a straight line':'Tap the target button on the map to see how far this is from you.'}
function youBlock(h){if(h.lat==null)return '';const i=H.indexOf(h);
  return '<div class="pp-you" data-i="'+i+'"><div class="pp-dist">'+distLine(h)+'</div><div class="pp-acts">'+
    '<a class="btn primary" href="'+esc(gUrl(h))+'" target="_blank" rel="noopener">'+ICON.nav+'Directions</a>'+
    '<button type="button" class="btn" data-drive="'+i+'">'+ICON.car+'Drive time</button>'+
    '<a class="btn" href="'+esc(aUrl(h))+'" target="_blank" rel="noopener">Apple Maps</a>'+
    '</div><div class="pp-drive" aria-live="polite">'+(driveShown[i]||'')+'</div></div>'}

const locNote=document.getElementById('locnote');
function note(html){locNote.innerHTML=html;locNote.hidden=!html;const s=locNote.querySelector('[data-stop]');if(s)s.addEventListener('click',stopLoc)}
let locBtn=null;
function btnState(){if(!locBtn)return;const on=!!you.watch;locBtn.setAttribute('aria-pressed',String(on&&!!you.pos));
  locBtn.classList.toggle('busy',on&&!you.pos);
  locBtn.setAttribute('aria-label',!on?'Show where I am':(you.pos?'Center the map on me':'Finding where you are'));locBtn.title=locBtn.getAttribute('aria-label')}
const LocCtl=L.Control.extend({options:{position:'topleft'},onAdd(){const d=L.DomUtil.create('div','locctl');
  d.innerHTML='<button type="button" aria-pressed="false" aria-label="Show where I am" title="Show where I am">'+ICON.loc+'</button>';
  locBtn=d.firstChild;L.DomEvent.disableClickPropagation(d);
  locBtn.addEventListener('click',()=>{if(!you.watch)startLoc(true);else if(you.pos)map.setView([you.pos.lat,you.pos.lng],Math.max(map.getZoom(),14));});return d}});
const locCtl=new LocCtl();map.addControl(locCtl);

function startLoc(center){
  if(!('geolocation' in navigator)||!window.isSecureContext){note('<span class="err">This browser can\'t share your location with this page.</span>');return}
  if(you.watch)return;
  you.center=!!center;
  note('Finding where you are… If your phone asks, tap Allow.');
  you.watch=navigator.geolocation.watchPosition(onPos,onErr,{enableHighAccuracy:true,maximumAge:15000,timeout:20000});
  btnState();
}
function onPos(p){
  const first=!you.pos;
  you.pos={lat:p.coords.latitude,lng:p.coords.longitude,acc:p.coords.accuracy,t:Date.now()};
  const ll=[you.pos.lat,you.pos.lng];
  if(!you.marker){
    const yc=getComputedStyle(document.documentElement).getPropertyValue('--you').trim()||'#1a73e8';
    you.circle=L.circle(ll,{radius:you.pos.acc,interactive:false,color:yc,weight:1,opacity:.6,fillColor:yc,fillOpacity:.1}).addTo(map);
    you.marker=L.marker(ll,{interactive:false,keyboard:false,zIndexOffset:5000,icon:L.divIcon({className:'',html:'<div class="you"></div>',iconSize:[0,0]})}).addTo(map);
  }else{you.marker.setLatLng(ll);you.circle.setLatLng(ll).setRadius(you.pos.acc)}
  if(you.center){you.center=false;map.setView(ll,Math.max(map.getZoom(),14))}
  lsSet('hh-loc','1');btnState();
  note('<span>You\'re the blue dot (accurate to about '+(you.pos.acc<1000?Math.max(5,Math.round(you.pos.acc/5)*5)+' m':(you.pos.acc/1609.344).toFixed(1)+' mi')+').</span><button type="button" class="linkbtn" data-stop>Stop showing my location</button>');
  you.waiters.splice(0).forEach(w=>w.ok(you.pos));
  const el=document.querySelector('.leaflet-popup .pp-you, #pane-home .pp-you');
  if(el){const d=el.querySelector('.pp-dist');if(d)d.innerHTML=distLine(H[+el.dataset.i])}
  if(first||!you.lastRender||miles(you.lastRender,you.pos)>0.1){for(const k in driveShown)delete driveShown[k];you.lastRender={lat:you.pos.lat,lng:you.pos.lng};render()}
}
function onErr(e){
  if(e.code===1){
    const msg='Location is turned off for this page. To turn it on: on an iPhone, go to Settings › Privacy & Security › Location Services › Safari Websites and choose "While Using"; on Android or a computer, tap the icon next to the address bar and allow Location. Then tap the target button again.';
    stopLoc();note('<span class="err">'+esc(msg)+'</span>');
    you.waiters.splice(0).forEach(w=>w.no(Object.assign(new Error(msg),{loc:true})));return}
  if(!you.pos)note('Still looking for your location… This can take a moment indoors.');
}
function stopLoc(){
  if(you.watch!=null)navigator.geolocation.clearWatch(you.watch);
  you.watch=null;you.pos=null;you.lastRender=null;
  if(you.marker){you.marker.remove();you.circle.remove();you.marker=you.circle=null}
  lsSet('hh-loc',null);note('');
  if(state.order==='near'){state.order='rank';ordBtns.forEach(([k,b])=>b.setAttribute('aria-pressed',String(k==='rank')))}
  btnState();render();
}
function getPos(){
  if(you.pos&&Date.now()-you.pos.t<120000)return Promise.resolve(you.pos);
  return new Promise((ok,no)=>{you.waiters.push({ok,no});startLoc(false);
    setTimeout(()=>no(Object.assign(new Error('Couldn\'t find where you are yet. Try again in a moment.'),{loc:true})),25000)});
}
const driveCache={},driveShown={};
async function driveTime(h){
  const p=await getPos();
  const k=h.lat+','+h.lng+'|'+p.lat.toFixed(3)+','+p.lng.toFixed(3);
  if(driveCache[k])return driveCache[k];
  const ctl=new AbortController(),tm=setTimeout(()=>ctl.abort(),10000);
  try{
    const r=await fetch('https://router.project-osrm.org/route/v1/driving/'+p.lng+','+p.lat+';'+h.lng+','+h.lat+'?overview=false',{signal:ctl.signal});
    const j=await r.json();
    if(j.code!=='Ok'||!j.routes||!j.routes.length)throw new Error('no route');
    return driveCache[k]={min:Math.max(1,Math.round(j.routes[0].duration/60)),mi:j.routes[0].distance/1609.344};
  }finally{clearTimeout(tm)}
}
async function runDrive(b){
  const box=b.closest('.pp-you'),out=box.querySelector('.pp-drive'),i=+box.dataset.i,h=H[i];
  b.disabled=true;out.textContent=you.pos?'Working out the drive…':'Finding where you are first…';
  try{const d=await driveTime(h);
    driveShown[i]='<b>About '+fmtMin(d.min)+'</b> by car, '+fmtMi(d.mi)+' on the roads. That\'s without traffic; Directions shows live traffic.';
  }catch(err){driveShown[i]=esc(err.loc?err.message:'Couldn\'t get a drive time right now. Directions still works.')}
  // re-draw the pop-up (it re-reads driveShown) so it resizes to fit
  const pop=map._popup;if(pop&&pop.isOpen())pop.update();else{out.innerHTML=driveShown[i];b.disabled=false}
}
// capture phase: Leaflet stops clicks inside pop-ups from bubbling up
document.addEventListener('click',e=>{const b=e.target.closest&&e.target.closest('[data-drive]');if(b&&!b.disabled)runDrive(b)},true);
try{if(lsGet('hh-loc')==='1'&&navigator.permissions)navigator.permissions.query({name:'geolocation'}).then(s=>{if(s.state==='granted')startLoc(false)}).catch(()=>{})}catch(e){}
'''
rep('// ---- filters', JS + '\n// ---- filters')

# order chips, after the other filter chips are built
rep("const ABBR={", '''const fo=document.getElementById('f-ord');const ordBtns=[];
[['rank','By rank'],['near','Nearest first']].forEach(([k,l])=>{ordBtns.push([k,chip(fo,l,k==='rank',()=>{state.order=k;ordBtns.forEach(([kk,bb])=>bb.setAttribute('aria-pressed',String(kk===k)));if(k==='near'&&!you.watch)startLoc(false);render()})])});
const ABBR={''')

rep('render();zipShow();', PHONE_JS + '\nrender();zipShow();')

open(out, 'w', encoding='utf-8').write(t)
print('ok', out, len(t), 'as of', asof)
