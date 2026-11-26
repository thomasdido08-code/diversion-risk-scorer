const COMP = [
  {k:"governance", c:"gov_risk", label:"Governance", col:"--c-gov", src:"WGI 2025 · RL, CC, GE", hint:"Rule of law, corruption, state effectiveness"},
  {k:"conflict", c:"conflict_risk", label:"Conflict at home", col:"--c-conf", src:"UCDP 2020–24 · WGI PV", hint:"Battle deaths + political instability"},
  {k:"embargo", c:"embargo_risk", label:"Arms embargo", col:"--c-emb", src:"UN / EU / OSCE · Oct 2026", hint:"Full 1 · partial 0.5 · OSCE 0.25"},
  {k:"neighbourhood", c:"neighbourhood_risk", label:"Neighbourhood", col:"--c-nb", src:"Land borders · UCDP", hint:"Worst conflict among land neighbours"},
  {k:"att", c:"att_risk", label:"Outside the ATT", col:"--c-att", src:"ATT Secretariat · Feb 2026", hint:"Party 0 · signatory 0.5 · outside 1 (incl. signatories that said they will not join)"}
];
const BASE = {...DATA.weights};
let W = {...BASE}, view = "map", metric = "risk", sortKey = null, sortDir = 1, sel = DATA.countries[0].iso3, lvlFilter = new Set();
const byIso = Object.fromEntries(DATA.countries.map(d=>[d.iso3,d]));
const N = DATA.countries.length;
const $ = s => document.querySelector(s);
const cssv = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const fmt = n => n==null ? "–" : Math.round(n).toLocaleString("en-GB");
const pct = r => Math.round(100*(1-(r-1)/N));
const LV = [["Critical",70,"--red-d"],["High",55,"--red"],["Elevated",40,"--orange"],["Lower",-1,"--t3"]];
const level = s => LV.find(l=>s>=l[1]);
const nbrs = iso => (BORDERS[iso]||[]).filter(n=>byIso[n]);

function norm(){ const s=Object.values(W).reduce((a,b)=>a+b,0)||1; const o={}; for(const k in W) o[k]=W[k]/s; return o; }
function compute(){
  const w=norm();
  for(const d of DATA.countries){ d.parts=COMP.map(p=>100*w[p.k]*d[p.c]); d.s=d.parts.reduce((a,b)=>a+b,0); d.e=d.s/100*d.arms_imp_tiv_m_2015on; }
  [...DATA.countries].sort((a,b)=>b.s-a.s).forEach((d,i)=>d.r=i+1);
  [...DATA.countries].sort((a,b)=>b.e-a.e).forEach((d,i)=>d.er=i+1);
}
const mval = d => metric==="exp" ? Math.log10(1+d.e) : d.s;
let color;
function makeColor(){
  const v=DATA.countries.map(mval), lo=d3.min(v), hi=d3.max(v);
  color=d3.scaleLinear().domain([lo,lo+(hi-lo)*.5,lo+(hi-lo)*.75,hi]).range([cssv("--lo"),"#7a5a3a",cssv("--orange"),cssv("--red-d")]).clamp(true);
}
const tagv = s => { const l=level(s); return `<span class="tagv" style="background:color-mix(in srgb,var(${l[2]}) 22%,transparent);color:${l[0]==="Lower"?"var(--t2)":`var(${l[2]==="--red-d"?"--red":l[2]})`}">${s.toFixed(1)}</span>`; };

/* ---------- sidebar */
function renderWeights(){
  $("#weights").innerHTML=COMP.map(p=>`<div class="w">
    <label for="w-${p.k}"><span><i class="sw" style="background:var(${p.col})"></i>${p.label}</span><output id="o-${p.k}"></output></label>
    <input type="range" id="w-${p.k}" min="0" max="60" step="1" value="${Math.round(W[p.k]*100)}">
    <small>${p.hint} · ${p.src}</small></div>`).join("");
  COMP.forEach(p=>$("#w-"+p.k).addEventListener("input",e=>{W[p.k]=+e.target.value/100;update();}));
}
function syncWeights(){
  const w=norm(); COMP.forEach(p=>{$("#w-"+p.k).value=Math.round(W[p.k]*100);$("#o-"+p.k).textContent=(w[p.k]*100).toFixed(0)+"%";});
  const custom=COMP.some(p=>Math.abs(w[p.k]-BASE[p.k])>.005);
  $("#wsum").textContent=(custom?"Custom weights active. ":"Base weights. ")+"Weights rescale to 100%. Rank ranges (5–95%) always come from base weights ±10 pts, 2,000 draws.";
}
function renderChips(){
  $("#lvlchips").innerHTML=LV.map(l=>`<button class="chip" type="button" aria-pressed="${lvlFilter.has(l[0])}" data-l="${l[0]}">${l[0]} <span class="mono">${DATA.countries.filter(d=>level(d.s)[0]===l[0]).length}</span></button>`).join("");
  document.querySelectorAll("#lvlchips .chip").forEach(b=>b.addEventListener("click",()=>{const l=b.dataset.l; lvlFilter.has(l)?lvlFilter.delete(l):lvlFilter.add(l); renderChips(); renderList(); if(view==="table") renderTable();}));
}
function filtered(){
  const q=$("#omni").value.trim().toLowerCase(), rg=$("#region").value, at=$("#att").value;
  return DATA.countries.filter(d=>(!q||d.name.toLowerCase().includes(q)||d.iso3.toLowerCase()===q)&&(!rg||d.region===rg)&&(!at||d.att_status===at||(at==="none"&&d.att_status==="not_intending"))&&(!lvlFilter.size||lvlFilter.has(level(d.s)[0])));
}
function renderList(){
  const k=metric==="exp"?"er":"r";
  const r=filtered().sort((a,b)=>a[k]-b[k]);
  $("#list").innerHTML=r.map(d=>`<button class="li ${d.iso3===sel?"on":""}" data-i="${d.iso3}" type="button"><span class="r">${d[k]}</span><span class="n">${d.name}<small>${d.iso3} · ${d.region.split(/[ ,&]/)[0]}</small></span>${metric==="exp"?`<span class="mono" style="font-size:11.5px;color:var(--t2)">${fmt(d.e)}</span>`:tagv(d.s)}</button>`).join("");
  $("#lcount").textContent=`${r.length} of ${N} objects`;
  document.querySelectorAll("#list .li").forEach(b=>b.addEventListener("click",()=>select(b.dataset.i)));
}

/* ---------- KPIs + histogram */
function renderKpis(){
  const L=DATA.validation.filter(v=>v.mode==="leakage"), R=DATA.validation.filter(v=>v.mode==="re-transfer");
  const avg=l=>Math.round(l.reduce((a,v)=>a+pct(byIso[v.iso3].r),0)/l.length);
  $("#kpis").innerHTML=[[N,"States scored"],[DATA.countries.filter(d=>d.s>=70).length,"Critical, score ≥ 70"],[Math.round(DATA.top10_overlap_avg*10)+"%","Top 10 stable under weight shocks"],[`p${avg(L)} · p${avg(R)}`,"Known cases: leakage · re-transfer"]]
    .map(([b,s])=>`<div class="kpi"><b>${b}</b><small>${s}</small></div>`).join("");
}
function renderHist(){
  const w=760,h=110,m={l:28,r:8,t:8,b:22};
  const vals=DATA.countries.map(d=>d.s);
  const x=d3.scaleLinear().domain([0,100]).range([m.l,w-m.r]);
  const bins=d3.bin().domain([0,100]).thresholds(d3.range(0,101,4))(vals);
  const y=d3.scaleLinear().domain([0,d3.max(bins,b=>b.length)]).nice().range([h-m.b,m.t]);
  const d=byIso[sel];
  const svg=d3.create("svg").attr("viewBox",`0 0 ${w} ${h}`).attr("role","img").attr("aria-label","Distribution of risk scores");
  svg.append("g").selectAll("line").data(y.ticks(3)).join("line").attr("x1",m.l).attr("x2",w-m.r).attr("y1",y).attr("y2",y).attr("stroke",cssv("--line"));
  svg.append("g").selectAll("text").data(y.ticks(3)).join("text").attr("x",m.l-6).attr("y",v=>y(v)+3).attr("text-anchor","end").attr("font-size",10).attr("font-family","IBM Plex Mono, monospace").attr("fill",cssv("--t3")).text(v=>v);
  svg.append("g").selectAll("rect").data(bins).join("rect").attr("x",b=>x(b.x0)+1).attr("width",b=>Math.max(0,x(b.x1)-x(b.x0)-2)).attr("y",b=>y(b.length)).attr("height",b=>y(0)-y(b.length))
    .attr("fill",b=>color && metric==="risk"?color((b.x0+b.x1)/2):cssv("--s3")).attr("opacity",b=>d.s>=b.x0&&d.s<b.x1?1:.75);
  svg.append("g").selectAll("text").data([0,20,40,55,70,100]).join("text").attr("x",x).attr("y",h-6).attr("text-anchor","middle").attr("font-size",10).attr("font-family","IBM Plex Mono, monospace").attr("fill",cssv("--t3")).text(v=>v);
  svg.append("line").attr("x1",x(d.s)).attr("x2",x(d.s)).attr("y1",m.t-2).attr("y2",h-m.b).attr("stroke",cssv("--blue")).attr("stroke-width",1.5);
  svg.append("text").attr("x",Math.min(x(d.s)+5,w-140)).attr("y",m.t+8).attr("font-size",11).attr("fill",cssv("--ink")).text(`${d.name} ${d.s.toFixed(1)}`);
  $("#hist").replaceChildren(svg.node());
  $("#histNote").textContent="Score, 4-point bins · states per bin";
}

/* ---------- map */
let paths;
function initMap(){
  const el=$("#map"), w=980, h=478;
  const feats=topojson.feature(TOPO,TOPO.objects.countries).features.filter(f=>f.properties.name!=="Antarctica");
  feats.forEach(f=>{ f.iso=CCN[String(f.id).padStart(3,"0")]||(f.properties.name==="Kosovo"?"XKX":null); });
  const proj=d3.geoNaturalEarth1().fitExtent([[4,4],[w-4,h-4]],{type:"Sphere"}), gp=d3.geoPath(proj);
  const svg=d3.select(el).append("svg").attr("viewBox",`0 0 ${w} ${h}`).attr("role","img").attr("aria-label","World map of diversion risk");
  svg.append("path").attr("d",gp({type:"Sphere"})).attr("fill","#0d1014");
  svg.append("path").attr("class","grat").attr("d",gp(d3.geoGraticule10()));
  const tip=$("#tip");
  paths=svg.append("g").selectAll("path").data(feats).join("path").attr("d",gp).attr("class",f=>"c"+(byIso[f.iso]?"":" nod"))
    .on("mousemove",(ev,f)=>{const d=byIso[f.iso]; if(!d) return; const r=el.getBoundingClientRect(); tip.hidden=false; tip.style.left=(ev.clientX-r.left)+"px"; tip.style.top=(ev.clientY-r.top)+"px";
      tip.innerHTML=`<b>${d.name}</b> <span class="mono" style="color:var(--t2)">${metric==="exp"?"exp #"+d.er+" · "+fmt(d.e):"#"+d.r+" · "+d.s.toFixed(1)}</span>`;})
    .on("mouseleave",()=>tip.hidden=true).on("click",(ev,f)=>{ if(byIso[f.iso]) select(f.iso); });
}
function paintMap(){
  if(!paths) return;
  const nb=new Set(nbrs(sel));
  paths.attr("fill",f=>byIso[f.iso]?color(mval(byIso[f.iso])):null).classed("sel",f=>f.iso===sel).classed("nb",f=>nb.has(f.iso));
  paths.filter(f=>nb.has(f.iso)).raise(); paths.filter(f=>f.iso===sel).raise();
  $("#mapTitle").textContent=metric==="exp"?"Exposure · risk × arms imports 2015–25 (log)":"Diversion risk score · selected state outlined, land neighbours dashed";
}

/* ---------- table */
const COLS=[{h:"Rank",k:"r",n:1},{h:"State",k:"name"},{h:"ISO",k:"iso3"},{h:"Score",k:"s",n:1},{h:"Δ base",k:null},{h:"Composition",k:null},{h:"Rank 5–95%",k:"rank_p05",n:1},{h:"ATT",k:"att_status"},{h:"Embargo",k:"embargo_risk"},{h:"Imports TIV m",k:"arms_imp_tiv_m_2015on",n:1},{h:"Exposure",k:"e",n:1}];
function renderTable(){
  $("#thead").innerHTML=COLS.map(c=>`<th class="${c.n?"n":""}" ${c.k?`data-k="${c.k}"`:""} scope="col">${c.h}${c.k&&sortKey===c.k?(sortDir>0?" ▲":" ▼"):""}</th>`).join("");
  document.querySelectorAll("#thead th[data-k]").forEach(th=>th.addEventListener("click",()=>{const k=th.dataset.k; if(sortKey===k) sortDir*=-1; else {sortKey=k; sortDir=["name","iso3","r","rank_p05","att_status"].includes(k)?1:-1;} renderTable();}));
  const k=sortKey||(metric==="exp"?"e":"r"), dir=sortKey?sortDir:(metric==="exp"?-1:1);
  const r=filtered().sort((a,b)=>{const x=a[k],y=b[k];return (typeof x==="string"?x.localeCompare(y):(x??-1e9)-(y??-1e9))*dir;});
  $("#tbody").innerHTML=r.map(d=>{const m=d.rank-d.r; return `<tr data-i="${d.iso3}" tabindex="0" class="${d.iso3===sel?"on":""}">
    <td class="n">${d.r}</td><td>${d.name}</td><td class="mono" style="color:var(--t3)">${d.iso3}</td><td class="n">${tagv(d.s)}</td>
    <td class="n">${m?`<span class="d ${m>0?"up":"dn"}">${m>0?"▲":"▼"}${Math.abs(m)}</span>`:`<span class="d" style="color:var(--t3)">–</span>`}</td>
    <td><div class="bars">${COMP.map((p,i)=>`<i style="width:${d.parts[i]}%;background:var(${p.col})"></i>`).join("")}</div></td>
    <td class="n" style="color:var(--t2)">${d.rank_p05}–${d.rank_p95}</td>
    <td><span class="pill ${d.att_status==="none"||d.att_status==="not_intending"?"r":d.att_status==="party"?"g":""}"${d.att_status==="not_intending"?' title="Signed, then notified the UN it will not become a party"':""}>${d.att_status==="none"?"OUTSIDE":d.att_status==="not_intending"?"OUTSIDE*":d.att_status.toUpperCase()}</span></td>
    <td>${d.embargo_risk?`<span class="pill v">${d.embargo_bodies.replace(/;/g,"+")}${d.embargo_risk<1?" · PARTIAL":""}</span>`:""}</td>
    <td class="n">${fmt(d.arms_imp_tiv_m_2015on)}</td><td class="n">${fmt(d.e)}</td></tr>`;}).join("");
  document.querySelectorAll("#tbody tr").forEach(tr=>{const go=()=>select(tr.dataset.i);tr.addEventListener("click",go);tr.addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();go();}});});
}

/* ---------- link graph */
function renderGraph(){
  const d=byIso[sel], ns=nbrs(sel).map(i=>byIso[i]);
  const w=760,h=480,cx=w/2,cy=h/2,R=Math.min(190,70+ns.length*14);
  const rad=v=>5+Math.sqrt(Math.max(0,v))/6;
  const pos={}; pos[d.iso3]=[cx,cy];
  ns.forEach((n,i)=>{const a=-Math.PI/2+i*2*Math.PI/Math.max(1,ns.length); pos[n.iso3]=[cx+R*Math.cos(a),cy+R*Math.sin(a)];});
  const svg=d3.create("svg").attr("viewBox",`0 0 ${w} ${h}`).attr("role","img").attr("aria-label",`Land neighbours of ${d.name}`);
  const g=svg.append("g");
  const nset=new Set(ns.map(n=>n.iso3));
  ns.forEach(a=>nbrs(a.iso3).forEach(b=>{ if(nset.has(b)&&a.iso3<b){ g.append("line").attr("x1",pos[a.iso3][0]).attr("y1",pos[a.iso3][1]).attr("x2",pos[b][0]).attr("y2",pos[b][1]).attr("stroke",cssv("--line2")).attr("stroke-dasharray","3 3"); } }));
  ns.forEach(n=>g.append("line").attr("x1",cx).attr("y1",cy).attr("x2",pos[n.iso3][0]).attr("y2",pos[n.iso3][1]).attr("stroke",color(n.conflict_risk*100*.6+20)).attr("stroke-width",1+n.conflict_risk*4).attr("opacity",.8));
  const all=[d,...ns];
  const node=g.selectAll("g.node").data(all).join("g").attr("class","node").attr("transform",n=>`translate(${pos[n.iso3]})`).on("click",(ev,n)=>select(n.iso3));
  node.append("circle").attr("r",n=>rad(n.arms_imp_tiv_m_2015on)+(n===d?6:0)).attr("fill",n=>color(n.s)).attr("stroke",n=>n===d?"#fff":cssv("--bg")).attr("stroke-width",n=>n===d?2:1.5);
  node.append("text").attr("y",n=>-(rad(n.arms_imp_tiv_m_2015on)+(n===d?12:8))).attr("text-anchor","middle").attr("font-size",n=>n===d?14:12).attr("font-weight",n=>n===d?600:500).attr("fill",cssv("--ink")).text(n=>n.name.replace(/,.*$/,""));
  node.append("text").attr("y",n=>rad(n.arms_imp_tiv_m_2015on)+(n===d?20:16)).attr("text-anchor","middle").attr("font-size",10.5).attr("font-family","IBM Plex Mono, monospace").attr("fill",cssv("--t2")).text(n=>`${n.s.toFixed(1)} · #${n.r}`);
  if(!ns.length) svg.append("text").attr("x",cx).attr("y",cy+70).attr("text-anchor","middle").attr("fill",cssv("--t3")).attr("font-size",12).text("No land neighbours in the dataset");
  $("#graph").replaceChildren(svg.node());
  $("#graphTitle").textContent=`Land neighbours of ${d.name} · ${ns.length} linked · edge weight = neighbour's conflict score`;
}

/* ---------- object view */
function renderObj(){
  const d=byIso[sel], l=level(d.s), lc=l[2]==="--red-d"?"--red":l[2];
  const x=r=>(100*(r-1)/(N-1));
  const ns=nbrs(sel).map(i=>byIso[i]).sort((a,b)=>a.r-b.r);
  $("#obj").innerHTML=`
    <div class="oh">
      <div class="otype"><svg class="i"><use href="#i-flag"/></svg><span class="cap">Sovereign state</span></div>
      <h2>${d.name}</h2>
      <div class="oid">${d.iso3} · ${d.region} · ${d.income}</div>
      <div class="ostat"><span class="big" style="color:var(${lc})">${d.s.toFixed(1)}</span>
        <div style="display:grid;gap:4px"><span class="lvl" style="background:color-mix(in srgb,var(${l[2]}) 22%,transparent);color:var(${lc});justify-self:start">${l[0]}</span><span class="mono" style="font-size:11.5px;color:var(--t2)">Rank ${d.r} / ${N} · exposure #${d.er}</span></div></div>
    </div>
    <div class="sec"><div class="sh">Rank stability <span class="mono" style="font-weight:400;color:var(--t2)">5–95%: ${d.rank_p05}–${d.rank_p95}</span></div>
      <div class="rr"><div class="t"></div><div class="s" style="left:${x(d.rank_p05)}%;width:max(3px,${x(d.rank_p95)-x(d.rank_p05)}%)"></div><div class="p" style="left:${x(d.r)}%"></div></div>
      <div class="cap" style="display:flex;justify-content:space-between;padding:0 14px 10px"><span>#1</span><span>#${N}</span></div></div>
    <div class="sec"><div class="sh">Score lineage <span class="mono" style="font-weight:400;color:var(--t2)">Σ ${d.s.toFixed(1)}</span></div>
      <div class="lin">${COMP.map((p,i)=>`<div class="ln"><span>${p.label}<span class="src"> · ${p.src}</span></span><em>${(d[p.c]*100).toFixed(0)} → ${d.parts[i].toFixed(1)}</em><span class="tr"><i style="width:${(d[p.c]*100).toFixed(0)}%;background:var(${p.col})"></i></span></div>`).join("")}</div></div>
    <div class="sec"><div class="sh">Properties</div><div class="props">
      <div>Battle deaths 2020–24</div><div class="mono">${fmt(d.battle_deaths_2020on)}</div>
      <div>Arms imports 2015–25</div><div class="mono">${fmt(d.arms_imp_tiv_m_2015on)} TIV m</div>
      <div>Exposure</div><div class="mono">${fmt(d.e)}</div>
      <div>ATT status</div><div>${d.att_status==="none"?"Outside the treaty":d.att_status==="not_intending"?"Signed, then notified the UN it will not become a party: scored as outside":d.att_status==="party"?"State party":"Signatory, not ratified"}</div>
      <div>Embargo</div><div>${d.embargo_note||"None in force"}</div>
    </div></div>
    <div class="sec" style="border-bottom:0"><div class="sh">Linked objects <span class="mono" style="font-weight:400;color:var(--t2)">${ns.length} land neighbours</span></div>
      <div class="links">${ns.length?ns.map(n=>`<button class="lk" type="button" data-i="${n.iso3}"><span>${n.name}<small>${n.iso3} · conflict ${(n.conflict_risk*100).toFixed(0)}</small></span>${tagv(n.s)}</button>`).join(""):`<p class="note" style="padding:10px 14px;margin:0;color:var(--t3)">No land neighbours in the dataset.</p>`}</div></div>`;
  document.querySelectorAll("#obj .lk").forEach(b=>b.addEventListener("click",()=>select(b.dataset.i)));
  $("#crumbs").innerHTML=`<span>Ontology</span><em>›</em><span>Sovereign state</span><em>›</em><span>${d.name}</span>`;
}

/* ---------- validation + method */
function renderVal(){
  const v=DATA.validation.map(x=>({...x,d:byIso[x.iso3]}));
  const grp=m=>v.filter(x=>x.mode===m).sort((a,b)=>a.d.r-b.d.r);
  const avg=l=>Math.round(l.reduce((a,x)=>a+pct(x.d.r),0)/l.length);
  const tbl=l=>`<div class="card"><div class="tbl" style="max-height:none"><table style="min-width:560px"><thead><tr><th>State</th><th class="n">Rank</th><th class="n">Percentile</th><th>Documented pattern</th></tr></thead><tbody>${l.map(x=>`<tr data-i="${x.iso3}"><td>${x.d.name}</td><td class="n">${x.d.r}</td><td class="n">${pct(x.d.r)}</td><td style="white-space:normal;color:var(--t2)">${x.example}</td></tr>`).join("")}</tbody></table></div></div>`;
  const L=grp("leakage"),R=grp("re-transfer");
  $("#v-val").innerHTML=`<h2>Validation against known diversion</h2>
    <p>Fifteen states with documented diversion, split by mechanism. Ranks follow the current weights.</p>
    <h3>Leakage: weak states losing their stocks · mean percentile ${avg(L)}</h3>${tbl(L)}
    <h3>Deliberate re-transfer by governments · mean percentile ${avg(R)}</h3>${tbl(R)}
    <div class="callout"><p><b>Blind spot.</b> Governance data measures whether a state <i>can</i> control its arsenal, not whether it <i>chooses</i> to. The UAE ranks ${byIso.ARE.r} despite UN Panel findings on Libya. A planned update adds a component for UN Panel findings of embargo breaches.</p></div>
    <p>These cases were picked knowing the outcome, so this is a sanity check, not a blind test. A planned update replaces it with cases coded blind from Conflict Armament Research and UN Panel reports.</p>`;
  document.querySelectorAll("#v-val tbody tr").forEach(tr=>tr.addEventListener("click",()=>select(tr.dataset.i)));
}
function renderMethod(){
  $("#v-method").innerHTML=`<h2>Method</h2>
    <p>Five components, each scaled from 0 (low risk) to 1 (high risk), weighted and summed to a 0–100 score. It operationalises Criterion 7 of EU Common Position 2008/944/CFSP: the risk of diversion within the buyer country or re-export.</p>
    <ul>
      <li><b>Governance 40%</b>: mean of WGI Rule of Law, Control of Corruption and Government Effectiveness, flipped from −2.5…+2.5.</li>
      <li><b>Conflict at home 20%</b>: half log-scaled battle deaths 2020–24, half WGI Political Stability.</li>
      <li><b>Arms embargo 10%</b>: full UN/EU embargo 1, non-state-forces or targeted 0.5, non-binding OSCE request 0.25.</li>
      <li><b>Neighbourhood 15%</b>: highest conflict score among land neighbours. Islands score 0.</li>
      <li><b>Outside the ATT 15%</b>: party 0, signatory 0.5, outside 1. A signatory that has notified the UN it will not become a party counts as outside (the United States, 2019).</li>
    </ul>
    <h3>Sources</h3>
    <ul>
      <li>World Bank Worldwide Governance Indicators 2025, via the World Bank API.</li>
      <li>SIPRI Arms Transfers Database, imports by recipient 2015–25 (TIV), via the World Bank API.</li>
      <li>UCDP battle-related deaths 2020–24, via the World Bank API.</li>
      <li>ATT Secretariat lists of States Parties (118) and signatories (25), February 2026.</li>
      <li>Embargoes in force: hand-coded from SIPRI's embargo archive and UN/EU sanctions lists, October 2026.</li>
      <li>Borders and map: world-countries and Natural Earth (world-atlas).</li>
    </ul>
    <h3>Known limits</h3>
    <ul>
      <li>Scores states, not licences. A real Criterion 7 assessment looks at the end user and the item.</li>
      <li>Weights are set by judgement, not fitted. Validation cases were not chosen blind.</li>
      <li>Arms imports are from all suppliers, not EU deliveries only.</li>
      <li>Taiwan and small territories without World Bank data are missing.</li>
      <li>UCDP counts deaths where fighting happens: Israel reflects Gaza, Russia only fighting on its own territory.</li>
      <li>Static snapshot dated 30 October 2026; US treaty status updated 26 November 2026.</li>
    </ul>`;
}

/* ---------- state */
function select(iso){
  sel=iso; renderObj(); renderList(); paintMap(); renderHist();
  if(view==="table") renderTable();
  if(view==="graph") renderGraph();
  const li=document.querySelector(`#list .li[data-i="${iso}"]`); if(li) li.scrollIntoView({block:"nearest"});
}
function setView(v){
  view=v;
  document.querySelectorAll(".mtab").forEach(t=>t.setAttribute("aria-selected",String(t.dataset.v===v)));
  ["map","table","graph","val","method"].forEach(k=>$("#v-"+k).hidden=k!==v);
  if(v==="table") renderTable(); if(v==="graph") renderGraph(); if(v==="val") renderVal();
}
function setMetric(m){
  metric=m; $("#m-risk").setAttribute("aria-pressed",String(m==="risk")); $("#m-exp").setAttribute("aria-pressed",String(m==="exp"));
  sortKey=null; makeColor(); paintMap(); renderList(); renderHist(); if(view==="table") renderTable();
}
function update(){ compute(); makeColor(); syncWeights(); renderChips(); renderKpis(); renderList(); renderObj(); paintMap(); renderHist(); if(view==="table") renderTable(); if(view==="graph") renderGraph(); if(view==="val") renderVal(); }

[...new Set(DATA.countries.map(d=>d.region))].sort().forEach(r=>{const o=document.createElement("option");o.value=r;o.textContent=r;$("#region").appendChild(o);});
$("#omnilist").innerHTML=DATA.countries.map(d=>`<option value="${d.name}">`).join("");
$("#omni").addEventListener("input",()=>{renderList(); if(view==="table") renderTable(); const m=DATA.countries.find(d=>d.name.toLowerCase()===$("#omni").value.trim().toLowerCase()); if(m) select(m.iso3);});
["#region","#att"].forEach(s=>$(s).addEventListener("input",()=>{renderList(); if(view==="table") renderTable();}));
document.querySelectorAll(".mtab").forEach(t=>t.addEventListener("click",()=>setView(t.dataset.v)));
document.querySelectorAll(".stab").forEach(t=>t.addEventListener("click",()=>{document.querySelectorAll(".stab").forEach(s=>s.setAttribute("aria-selected",String(s===t))); $("#s-obj").hidden=t.dataset.s!=="obj"; $("#s-model").hidden=t.dataset.s!=="model";}));
$("#m-risk").addEventListener("click",()=>setMetric("risk")); $("#m-exp").addEventListener("click",()=>setMetric("exp"));
$("#reset").addEventListener("click",()=>{W={...BASE};update();});
document.addEventListener("keydown",e=>{ if(e.key==="/"&&document.activeElement.tagName!=="INPUT"){e.preventDefault();$("#omni").focus();} });
renderWeights(); renderMethod(); compute(); makeColor(); initMap(); update();
