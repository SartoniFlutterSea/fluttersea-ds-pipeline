import{j as e}from"./jsx-runtime-u17CrQMm.js";const m=c=>c==null||c===""||Array.isArray(c)&&!c.length||typeof c=="object"&&!Array.isArray(c)&&!Object.keys(c).length;function j(c,a=[]){const r=[];for(const[o,l]of Object.entries(c??{}))l&&typeof l=="object"&&!Array.isArray(l)?r.push(...j(l,[...a,o])):m(l)||r.push([[...a,o],String(l)]);return r}function f({data:c}){const a=j(c);return a.length?e.jsx("div",{className:"cp-scroll",children:e.jsx("table",{className:"cp-tbl",children:e.jsx("tbody",{children:a.map(([r,o],l)=>e.jsxs("tr",{children:[e.jsx("td",{className:"cp-path",children:r.map((n,t)=>e.jsxs("span",{children:[t>0&&e.jsx("em",{children:"›"}),n]},t))}),e.jsx("td",{className:"cp-val",children:e.jsx("code",{children:o})})]},l))})})}):null}function d({title:c,count:a,children:r}){return e.jsxs("section",{className:"cp-sec",children:[e.jsxs("h2",{children:[c,a!==void 0&&e.jsx("span",{className:"cp-n",children:a})]}),r]})}function v({contract:c}){const a=[["variante",c.props??[]],["booleana",c.booleans??[]],["testo",c.texts??[]],["slot icona",c.swaps??[]]],r=a.reduce((o,[,l])=>o+l.length,0);return r?e.jsx(d,{title:"Property",count:r,children:e.jsx("div",{className:"cp-scroll",children:e.jsxs("table",{className:"cp-tbl cp-tbl--api",children:[e.jsx("thead",{children:e.jsxs("tr",{children:[e.jsx("th",{children:"Nome"}),e.jsx("th",{children:"Tipo"}),e.jsx("th",{children:"Valori"}),e.jsx("th",{children:"Default"}),e.jsx("th",{children:"In Figma"})]})}),e.jsx("tbody",{children:a.flatMap(([o,l])=>(l??[]).map((n,t)=>e.jsxs("tr",{children:[e.jsx("td",{children:e.jsx("b",{children:n.name})}),e.jsx("td",{children:e.jsx("span",{className:"cp-kind",children:o})}),e.jsx("td",{children:Array.isArray(n.values)?e.jsx("span",{className:"cp-vals",children:n.values.map(p=>e.jsx("code",{children:p},p))}):n.type?e.jsx("code",{children:n.type}):e.jsx("span",{className:"cp-dim",children:"—"})}),e.jsx("td",{children:n.default!==void 0&&n.default!==""?e.jsx("code",{children:String(n.default)}):e.jsx("span",{className:"cp-dim",children:"—"})}),e.jsx("td",{className:"cp-dim",children:n.figmaProperty??"—"})]},`${o}-${t}`)))})]})})}):null}function w({slug:c,contract:a,intent:r,figma:o}){const l=a?.name??r?.componentName??c,n=a?.id??r?.id,t=r?.antiPatterns??[],p=r?.behavior??{},x=r?.commonPatterns??[],g=r?._reproducibility,b=(s,i)=>`https://www.figma.com/design/${s}/?node-id=${String(i).replace(":","-")}`;return e.jsxs("div",{className:"cp",children:[e.jsx("style",{children:y}),e.jsxs("header",{className:"cp-head",children:[e.jsxs("div",{className:"cp-kick",children:[n&&e.jsx("code",{children:n}),o?.variantCount?e.jsxs("span",{children:[o.variantCount," varianti"]}):null,o?.nodeType&&e.jsx("span",{children:o.nodeType})]}),e.jsx("h1",{children:l}),r?.purpose&&e.jsx("p",{className:"cp-lead",children:r.purpose}),e.jsxs("div",{className:"cp-prov",children:[e.jsxs("span",{className:a?"on":"off",children:["contratto",a?.source?.ds?` · ${a.source.ds}`:""]}),e.jsxs("span",{className:r?"on":"off",children:["intento",r?._source?.ds?` · ${r._source.ds}`:""]}),e.jsxs("span",{className:o?"on":"off",children:["ancoraggio",o?.lastModified?` · ${o.lastModified.slice(0,10)}`:""]})]})]}),t.length>0&&e.jsx(d,{title:"Anti-pattern",count:t.length,children:e.jsx("div",{className:"cp-stack",children:t.map((s,i)=>e.jsxs("div",{className:"cp-anti",children:[e.jsx("p",{className:"cp-anti-t",children:s.scenario}),s.reason&&e.jsxs("p",{children:[e.jsx("span",{className:"cp-k",children:"Perché è sbagliato"}),s.reason]}),s.alternative&&e.jsxs("p",{children:[e.jsx("span",{className:"cp-k",children:"Cosa usare invece"}),s.alternative]}),e.jsxs("div",{className:"cp-anti-m",children:[s.origin&&e.jsx("span",{children:s.origin}),s.section&&e.jsx("span",{children:s.section})]})]},i))})}),!m(p)&&e.jsx(d,{title:"Comportamento",children:Object.entries(p).map(([s,i])=>e.jsxs("div",{className:"cp-plat",children:[e.jsx("h3",{children:s}),e.jsx("dl",{className:"cp-dl",children:Object.entries(i).filter(([,h])=>!m(h)).map(([h,u])=>e.jsxs("div",{children:[e.jsx("dt",{children:h.replace(/([a-z])([A-Z])/g,"$1 $2")}),e.jsx("dd",{children:String(u)})]},h))})]},s))}),x.length>0&&e.jsx(d,{title:"Pattern ricorrenti",count:x.length,children:e.jsx("div",{className:"cp-stack",children:x.map((s,i)=>e.jsxs("div",{className:"cp-item",children:[s.name&&e.jsx("b",{children:s.name}),e.jsx("span",{children:s.description??(typeof s=="string"?s:"")})]},i))})}),a&&e.jsx(v,{contract:a}),a&&!m(a.sizing)&&e.jsx(d,{title:"Dimensioni",children:e.jsx(f,{data:a.sizing})}),a&&!m(a.tokens)&&e.jsxs(d,{title:"Token",count:j(a.tokens).length,children:[e.jsx("p",{className:"cp-hint",children:"Sempre per nome, mai per valore: i colori cambiano per brand alla compilazione."}),e.jsx(f,{data:a.tokens})]}),g&&e.jsxs(d,{title:"Qualità dell’estrazione",children:[e.jsx("p",{className:"cp-hint",children:"Confronto fra ciò che la pipeline ha letto da Figma e ciò che era scritto a mano."}),e.jsx("div",{className:"cp-scroll",children:e.jsxs("table",{className:"cp-tbl cp-tbl--api",children:[e.jsx("thead",{children:e.jsxs("tr",{children:[e.jsx("th",{children:"Campo"}),e.jsx("th",{children:"Da Figma"}),e.jsx("th",{children:"Scritto a mano"})]})}),e.jsx("tbody",{children:Object.entries(g).filter(([,s])=>s&&typeof s=="object").map(([s,i])=>e.jsxs("tr",{children:[e.jsx("td",{children:e.jsx("b",{children:s.replace(/([a-z])([A-Z])/g,"$1 $2")})}),e.jsx("td",{className:i.figma>=i.metadata?"cp-win":"",children:i.figma}),e.jsx("td",{className:i.metadata>i.figma?"cp-win":"",children:i.metadata})]},s))})]})})]}),a?._coverage&&e.jsx(d,{title:"Cosa è stato misurato",children:e.jsx(f,{data:a._coverage})}),(o?.fileKey||r?._source)&&e.jsx(d,{title:"Su Figma",children:e.jsxs("div",{className:"cp-links",children:[o?.fileKey&&o?.nodes&&Object.entries(o.nodes).map(([s,i])=>e.jsxs("a",{href:b(o.fileKey,i),target:"_blank",rel:"noreferrer",children:[o.fileName??s," · componente →"]},s)),r?._source?.fileKey&&r?._source?.purposeFrame&&e.jsx("a",{href:b(r._source.fileKey,r._source.purposeFrame.id),target:"_blank",rel:"noreferrer",children:"Purpose & Usage →"}),r?._source?.fileKey&&r?._source?.behaviorFrame&&e.jsx("a",{href:b(r._source.fileKey,r._source.behaviorFrame.id),target:"_blank",rel:"noreferrer",children:"Behavior →"})]})})]})}const y=`
.cp {
  --b: #14161b; --b2: #474d58; --b3: #7b828f;
  --line: #e3e5ea; --soft: #f7f8fa; --acc: #1e3fcc; --warn: #b3341f; --ok: #1d6b4a;
  background: #fff; color: var(--b2); min-height: 100%;
  font: 15px/1.62 ui-sans-serif, "Segoe UI", system-ui, sans-serif;
  padding: 2.3rem clamp(1.2rem, 5vw, 3.2rem) 5rem; max-width: 64rem; margin: 0 auto;
}
.cp * { box-sizing: border-box; }
.cp-head { border-bottom: 2px solid var(--b); padding-bottom: 1.2rem; }
.cp-kick { display: flex; flex-wrap: wrap; gap: .45rem .9rem; margin-bottom: .6rem; }
.cp-kick > * {
  font: .69rem/1 ui-monospace, Consolas, monospace; letter-spacing: .08em;
  text-transform: uppercase; color: var(--b3); border: 1px solid var(--line);
  border-radius: 2px; padding: .3rem .5rem; background: none;
}
.cp h1 { font: 600 clamp(1.9rem, 4.6vw, 2.7rem)/1.08 inherit; color: var(--b); margin: 0 0 .6rem; letter-spacing: -.015em; }
.cp-lead { margin: 0 0 1rem; font-size: 1.04rem; max-width: 62ch; }
.cp-prov { display: flex; flex-wrap: wrap; gap: .4rem; }
.cp-prov span {
  font: .7rem/1 ui-monospace, Consolas, monospace; padding: .32rem .55rem; border-radius: 2px;
}
.cp-prov .on  { background: #e6f0ea; color: var(--ok); }
.cp-prov .off { background: var(--soft); color: var(--b3); text-decoration: line-through; }
.cp-sec { padding: 1.7rem 0; border-bottom: 1px solid var(--line); }
.cp-sec:last-child { border-bottom: 0; }
.cp h2 {
  font: 600 .73rem/1 ui-monospace, Consolas, monospace; letter-spacing: .13em;
  text-transform: uppercase; color: var(--b3); margin: 0 0 .9rem;
  display: flex; align-items: center; gap: .5rem;
}
.cp-n { background: var(--b); color: #fff; border-radius: 9px; padding: .1rem .44rem; font-size: .68rem; letter-spacing: 0; }
.cp-hint { font-size: .88rem; color: var(--b3); margin: -.4rem 0 .9rem; max-width: 62ch; }
.cp-stack { display: grid; gap: .7rem; }
.cp-item { padding-left: .9rem; border-left: 2px solid var(--line); display: grid; gap: .12rem; }
.cp-item b { color: var(--b); }
.cp-anti { background: var(--soft); border-left: 3px solid var(--warn); border-radius: 0 3px 3px 0; padding: .85rem 1.05rem; }
.cp-anti p { margin: 0 0 .5rem; }
.cp-anti-t { font-weight: 600; color: var(--b); }
.cp-k { display: block; font: .65rem/1 ui-monospace, Consolas, monospace; letter-spacing: .11em; text-transform: uppercase; color: var(--b3); margin-bottom: .2rem; }
.cp-anti-m { display: flex; gap: .4rem; }
.cp-anti-m span { font: .64rem/1 ui-monospace, Consolas, monospace; color: var(--b3); border: 1px solid var(--line); border-radius: 2px; padding: .2rem .38rem; background: #fff; }
.cp-plat + .cp-plat { margin-top: 1.2rem; }
.cp h3 { font: 600 .95rem/1 inherit; color: var(--b); margin: 0 0 .5rem; }
.cp-dl { margin: 0; display: grid; gap: .6rem; }
.cp-dl > div { display: grid; grid-template-columns: 11rem minmax(0, 1fr); gap: 0 1.2rem; }
.cp-dl dt { font-weight: 600; color: var(--b); font-size: .88rem; text-transform: capitalize; }
.cp-dl dd { margin: 0; white-space: pre-line; }
@media (max-width: 640px) { .cp-dl > div { grid-template-columns: 1fr; gap: .15rem; } }
.cp-scroll { overflow-x: auto; }
.cp-tbl { border-collapse: collapse; width: 100%; font-size: .88rem; }
.cp-tbl td, .cp-tbl th { padding: .42rem .8rem .42rem 0; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
.cp-tbl th { font: 400 .66rem/1 ui-monospace, Consolas, monospace; letter-spacing: .1em; text-transform: uppercase; color: var(--b3); border-bottom: 1px solid var(--b3); white-space: nowrap; }
.cp-tbl--api { min-width: 34rem; }
.cp-tbl b { color: var(--b); }
.cp-path { font: .8rem/1.5 ui-monospace, Consolas, monospace; color: var(--b2); white-space: nowrap; }
.cp-path em { color: var(--b3); font-style: normal; margin: 0 .3rem; }
.cp-val code, .cp-tbl code {
  font: .8em/1.4 ui-monospace, Consolas, monospace; background: var(--soft);
  border: 1px solid var(--line); border-radius: 2px; padding: .08em .34em; color: var(--b);
  overflow-wrap: anywhere;
}
.cp-vals { display: flex; flex-wrap: wrap; gap: .25rem; }
.cp-kind { font: .68rem/1 ui-monospace, Consolas, monospace; color: var(--b3); }
.cp-dim { color: var(--b3); }
.cp-win { color: var(--ok); font-weight: 600; }
.cp-links { display: flex; flex-wrap: wrap; gap: .45rem; }
.cp-links a {
  font: .8rem/1 ui-monospace, Consolas, monospace; color: var(--acc); text-decoration: none;
  border: 1px solid var(--acc); border-radius: 2px; padding: .45rem .65rem;
}
.cp-links a:hover, .cp-links a:focus-visible { background: var(--acc); color: #fff; }
`;export{w as C};
