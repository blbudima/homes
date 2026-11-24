// ---- phone layout: map fills the screen; list, filters and home details open in a bottom sheet
const PHONE=document.documentElement.classList.contains('phone');
if(PHONE){
  const pad=n=>String(n).padStart(2,'0');
  const SVG={
    list:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1.1"/><circle cx="4.5" cy="12" r="1.1"/><circle cx="4.5" cy="18" r="1.1"/></svg>',
    filt:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2.2"/><circle cx="9" cy="17" r="2.2"/></svg>',
    x:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
  };
  const mapEl=document.getElementById('map'), wrap=document.querySelector('.wrap');

  // top bar with the search field
  const top=document.createElement('div');top.className='topbar';
  top.appendChild(document.querySelector('.find-wrap'));
  qIn.placeholder='Search address, street or ZIP';
  document.body.appendChild(top);

  // bottom bar
  const bar=document.createElement('nav');bar.className='tabbar';bar.setAttribute('aria-label','Map views');
  bar.innerHTML='<button type="button" id="b-list" aria-expanded="false" aria-controls="sheet">'+SVG.list+'List <span class="n" id="b-n">0</span></button>'+
    '<button type="button" id="b-filt" aria-expanded="false" aria-controls="sheet">'+SVG.filt+'Filters<span class="dot" id="b-dot" hidden></span></button>';
  document.body.appendChild(bar);

  // the sheet
  const scrim=document.createElement('div');scrim.className='scrim';
  const sheet=document.createElement('section');sheet.className='sheet';sheet.id='sheet';sheet.setAttribute('role','dialog');sheet.setAttribute('aria-modal','false');sheet.setAttribute('aria-labelledby','sh-t');
  sheet.innerHTML='<div class="sh-head"><h2 id="sh-t"></h2><button type="button" class="sh-x" aria-label="Close">'+SVG.x+'</button></div>'+
    '<div class="sh-body"><div class="pane" id="pane-home" hidden></div><div class="pane lst" id="pane-list" hidden></div><div class="pane" id="pane-filters" hidden></div></div>';
  document.body.append(scrim,sheet);
  const shT=sheet.querySelector('#sh-t'), shBody=sheet.querySelector('.sh-body');
  const panes={home:sheet.querySelector('#pane-home'),list:sheet.querySelector('#pane-list'),filters:sheet.querySelector('#pane-filters')};

  // filters pane: the existing controls, moved (their listeners come along)
  const pf=panes.filters;
  pf.appendChild(document.getElementById('counts'));
  pf.appendChild(document.querySelector('.bar'));
  const locGrp=document.createElement('div');locGrp.className='grp';locGrp.innerHTML='<span>Your location</span>';
  const locChip=chip(locGrp,'Show where I am',false,()=>{you.watch?stopLoc():startLoc(true)});
  document.querySelector('.bar').appendChild(locGrp);
  pf.appendChild(document.getElementById('legend'));
  const about=document.createElement('details');about.className='about';
  about.innerHTML='<summary>About this map</summary>';
  wrap.querySelectorAll('header .sub, header .upd, .wrap>.note').forEach(n=>{const p=document.createElement('p');p.innerHTML=n.innerHTML;about.appendChild(p)});
  pf.appendChild(about);
  const reset=document.createElement('button');reset.type='button';reset.className='f-reset';reset.textContent='Back to the default view';
  pf.appendChild(reset);

  // which chips count as "default": Detached, tiers A and B, everything else on
  const RADIO={'f-tab':'All tabs','f-red':'Everywhere','f-ord':'By rank'};
  const KDEF=new Set(DEFAULTS.kind.map(k=>KS[k])), TDEF=new Set(DEFAULTS.tier);
  const wantOn=(g,b)=>g==='f-typ'?KDEF.has(b.textContent):g==='f-tier'?TDEF.has(b.textContent[0]):true;
  function changedGroups(){let n=0;
    Object.entries(RADIO).forEach(([g,l])=>{const b=[...document.querySelectorAll('#'+g+' .chip')].find(x=>x.textContent===l);if(b&&b.getAttribute('aria-pressed')!=='true')n++});
    ['f-typ','f-nb','f-tier','f-zip'].forEach(g=>{if([...document.querySelectorAll('#'+g+' .chip')].some(b=>(b.getAttribute('aria-pressed')==='true')!==wantOn(g,b)))n++});
    return n}
  reset.addEventListener('click',()=>{
    Object.entries(RADIO).forEach(([g,l])=>{const b=[...document.querySelectorAll('#'+g+' .chip')].find(x=>x.textContent===l);if(b&&b.getAttribute('aria-pressed')!=='true')b.click()});
    ['f-typ','f-nb','f-tier','f-zip'].forEach(g=>document.querySelectorAll('#'+g+' .chip').forEach(b=>{if((b.getAttribute('aria-pressed')==='true')!==wantOn(g,b))b.click()}));
  });

  // map controls for thumbs: locate button bottom right, no zoom buttons (pinch instead)
  if(map.zoomControl)map.zoomControl.remove();
  locCtl.setPosition('bottomright');
  if(map.attributionControl)map.attributionControl.setPosition('bottomleft');
  map.invalidateSize();

  // location: short status toast, chip in Filters mirrors it
  let noteT=null;
  const _note=note;
  note=function(html){_note(html);clearTimeout(noteT);if(html&&!/class="err"/.test(html)&&/blue dot/.test(html))noteT=setTimeout(()=>{locNote.hidden=true},4500)};
  locNote.addEventListener('click',e=>{if(!e.target.closest('button'))locNote.hidden=true});
  const _btnState=btnState;
  btnState=function(){_btnState();locChip.setAttribute('aria-pressed',String(!!you.watch))};

  // sheet open / close, with the phone's Back button closing it
  let mode=null, curI=null;
  function show(m){
    mode=m;Object.entries(panes).forEach(([k,p])=>p.hidden=k!==m);
    sheet.classList.toggle('home',m==='home');sheet.classList.add('open');
    scrim.classList.toggle('on',m!=='home');
    document.getElementById('b-list').setAttribute('aria-expanded',String(m==='list'));
    document.getElementById('b-filt').setAttribute('aria-expanded',String(m==='filters'));
    shBody.scrollTop=0;
    if(!(history.state&&history.state.hh))try{history.pushState({hh:1},'')}catch(e){}
  }
  function hide(){
    if(!mode)return;mode=null;sheet.classList.remove('open');scrim.classList.remove('on');
    document.getElementById('b-list').setAttribute('aria-expanded','false');
    document.getElementById('b-filt').setAttribute('aria-expanded','false');
    if(hl){hl.classList.remove('hl');hl=null}curI=null;
  }
  function close(){if(history.state&&history.state.hh){try{history.back();return}catch(e){}}hide()}
  addEventListener('popstate',hide);
  sheet.querySelector('.sh-x').addEventListener('click',close);
  scrim.addEventListener('click',close);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&mode)close()});
  document.getElementById('b-list').addEventListener('click',()=>mode==='list'?close():openList());
  document.getElementById('b-filt').addEventListener('click',()=>mode==='filters'?close():openFilters());
  map.on('click',()=>{if(mode==='home')close()});

  // drag the sheet down by its handle to close it
  (function(){const h=sheet.querySelector('.sh-head');let y0=null,dy=0;
    h.addEventListener('pointerdown',e=>{if(e.target.closest('button'))return;y0=e.clientY;dy=0;sheet.classList.add('dragging');h.setPointerCapture(e.pointerId)});
    h.addEventListener('pointermove',e=>{if(y0==null)return;dy=Math.max(0,e.clientY-y0);sheet.style.transform='translateY('+dy+'px)'});
    const end=()=>{if(y0==null)return;y0=null;sheet.classList.remove('dragging');sheet.style.transform='';if(dy>80)close()};
    h.addEventListener('pointerup',end);h.addEventListener('pointercancel',end)})();

  function openFilters(){shT.innerHTML='Filters';show('filters')}
  function openList(){renderCards();show('list')}

  // a home in the sheet, with the map moved so its marker sits in the open space above
  function openHome(i){
    const h=H[i];curI=i;shT.textContent='';
    panes.home.innerHTML=popupHtml(h);
    show('home');
    if(hl)hl.classList.remove('hl');
    const m=markers.get(i);
    if(m){if(!map.hasLayer(m))m.addTo(map);
      requestAnimationFrame(()=>{
        const el=m.getElement()&&m.getElement().querySelector('.mk');if(el){el.classList.add('hl');hl=el}
        const z=Math.max(map.getZoom(),15),mh=mapEl.clientHeight,sTop=sheet.getBoundingClientRect().top-mapEl.getBoundingClientRect().top;
        const ty=Math.max(90,(68+Math.min(mh,sTop))/2);
        const p=map.project(m.getLatLng(),z);
        map.setView(map.unproject(p.add([0,mh/2-ty]),z),z,{animate:!matchMedia('(prefers-reduced-motion: reduce)').matches});
      })}
  }
  focusHome=function(i){openHome(i)};
  markers.forEach((m,i)=>{m.unbindPopup();m.on('click',()=>openHome(i))});

  // list as cards
  function cardHTML(h){const i=H.indexOf(h),mi=homeMi(h),c=h.comp;
    const comp=c?'<span class="tag '+(c.d<=5?'ok':'bad')+'">'+(c.d<=-5?Math.round(-c.d)+'% below comps':c.d<=5?'In line with comps':Math.round(c.d)+'% above comps')+'</span>':'';
    const red=h.red==='in'?'<span class="tag red">Red area</span>':h.red==='line'?'<span class="tag red">On the red line</span>':'';
    return '<button type="button" class="hc" data-i="'+i+'"><span class="hc-top"><span class="pill" style="--c:'+tierVar(h.tier)+'">'+esc(h.tier)+' #'+pad(h.rank)+'</span><span class="hc-price">'+esc(h.price)+'</span></span>'+
      '<span class="hc-a">'+esc(short(h.a))+'</span>'+
      '<span class="hc-meta">'+esc(KS[h.kind])+(h.nb!=='0'?', '+esc(NBT[h.nb].toLowerCase()):'')+' · '+esc(h.beds)+' bd / '+esc(h.baths)+' ba · HOA '+esc(h.hoa)+'</span>'+
      (h.why?'<span class="hc-why">'+esc(h.why)+'</span>':'')+
      '<span class="hc-tags">'+(mi!=null?'<span class="tag near">'+fmtMi(mi)+' away</span>':'')+comp+red+(h.lat==null?'<span class="tag">No map pin</span>':'')+'</span></button>'}
  function renderCards(){
    const vis=H.filter(visible);
    document.getElementById('b-n').textContent=vis.length;
    const n=changedGroups();document.getElementById('b-dot').hidden=!n;reset.disabled=!n;
    if(mode==='list'||!mode)shT.innerHTML='Homes<small>'+vis.length+' of '+H.length+'</small>';
    let html='<div class="lst-sort grp" id="l-ord"></div>';
    ['H','A','E'].forEach(t=>{const rows=vis.filter(h=>h.tab===t).sort(rowSort);if(!rows.length)return;
      html+='<h3>'+esc(TABS[t])+'<small>'+rows.length+'</small></h3>'+rows.map(cardHTML).join('')});
    if(!vis.length)html+='<p class="lst-empty">'+(state.q.length?'No homes match this search with your filters. Clear the search or open Filters.':'No homes match your filters. Open Filters to turn some back on.')+'</p>';
    panes.list.innerHTML=html;
    const lo=panes.list.querySelector('#l-ord');
    [['rank','By rank'],['near','Nearest first']].forEach(([k,l])=>chip(lo,l,state.order===k,()=>{
      const b=[...document.querySelectorAll('#f-ord .chip')].find(x=>x.textContent===l);if(b)b.click()}));
  }
  panes.list.addEventListener('click',e=>{const c=e.target.closest('.hc');if(c)openHome(+c.dataset.i)});
  const _render=render;
  render=function(){_render();renderCards();if(mode==='home'&&curI!=null){const d=panes.home.querySelector('.pp-dist');if(d)d.innerHTML=distLine(H[curI])}};
  qIn.addEventListener('focus',()=>{if(mode)close()});
}
