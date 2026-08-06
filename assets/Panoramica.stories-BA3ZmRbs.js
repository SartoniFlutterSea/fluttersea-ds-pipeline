import{j as e}from"./jsx-runtime-u17CrQMm.js";function l({index:n}){const r=n.filter(t=>t.has.contract&&t.has.intent&&t.has.figma).length,c=n.reduce((t,a)=>t+a.antiPatterns,0),s=n.flatMap(t=>Object.entries(t.reproducibility??{}).filter(([,a])=>a&&typeof a=="object"&&a.figma>a.metadata).map(([a,i])=>({name:t.name,field:a,figma:i.figma,meta:i.metadata})));return e.jsxs("div",{className:"ov",children:[e.jsx("style",{children:d}),e.jsxs("header",{className:"ov-head",children:[e.jsx("h1",{children:"Stato dell’estrazione"}),e.jsxs("p",{className:"ov-lead",children:["Ogni pagina è costruita da tre artefatti letti da Figma: il"," ",e.jsx("b",{children:"contratto"})," (props, token, dimensioni), l’",e.jsx("b",{children:"intento"})," (scopo, anti-pattern, comportamento) e l’",e.jsx("b",{children:"ancoraggio"})," (dove sta e quando è cambiato). Quello che vedi qui è quanti componenti li hanno già."]})]}),e.jsxs("div",{className:"ov-stats",children:[e.jsxs("div",{className:"ov-s",children:[e.jsx("b",{children:n.length}),e.jsx("span",{children:"componenti estratti"})]}),e.jsxs("div",{className:"ov-s",children:[e.jsx("b",{children:r}),e.jsx("span",{children:"con tutti e tre"})]}),e.jsxs("div",{className:"ov-s",children:[e.jsx("b",{children:c}),e.jsx("span",{children:"anti-pattern"})]}),e.jsxs("div",{className:"ov-s",children:[e.jsx("b",{children:n.reduce((t,a)=>t+a.props,0)}),e.jsx("span",{children:"property"})]})]}),e.jsxs("div",{className:"ov-note",children:["Questa è una ",e.jsx("b",{children:"prova del meccanismo"}),", non la copertura finale: i componenti documentati in Figma sono molti di più. Il passo successivo è far girare l’estrazione su tutti."]}),e.jsxs("section",{children:[e.jsx("h2",{children:"Componenti"}),e.jsx("div",{className:"ov-scroll",children:e.jsxs("table",{children:[e.jsx("thead",{children:e.jsxs("tr",{children:[e.jsx("th",{children:"Componente"}),e.jsx("th",{children:"Artefatti"}),e.jsx("th",{className:"n",children:"Varianti"}),e.jsx("th",{className:"n",children:"Property"}),e.jsx("th",{className:"n",children:"Anti-pattern"}),e.jsx("th",{children:"Aggiornato"})]})}),e.jsx("tbody",{children:n.map(t=>e.jsxs("tr",{children:[e.jsxs("td",{children:[e.jsx("b",{children:t.name}),e.jsx("span",{className:"ov-id",children:t.id}),t.purpose&&e.jsxs("span",{className:"ov-d",children:[t.purpose.slice(0,110),t.purpose.length>110?"…":""]})]}),e.jsxs("td",{children:[e.jsxs("div",{className:"ov-dots",children:[e.jsx("i",{className:t.has.contract?"on":"",title:"contratto",children:"C"}),e.jsx("i",{className:t.has.intent?"on":"",title:"intento",children:"I"}),e.jsx("i",{className:t.has.figma?"on":"",title:"ancoraggio",children:"A"})]}),e.jsxs("span",{className:"ov-src",children:[t.dsContract&&`contratto ${t.dsContract}`,t.dsContract&&t.dsIntent&&" · ",t.dsIntent&&`intento ${t.dsIntent}`]})]}),e.jsx("td",{className:"n",children:t.variantCount||e.jsx("span",{className:"z",children:"—"})}),e.jsx("td",{className:"n",children:t.props||e.jsx("span",{className:"z",children:"—"})}),e.jsx("td",{className:"n",children:t.antiPatterns||e.jsx("span",{className:"z",children:"—"})}),e.jsx("td",{className:"ov-when",children:t.lastModified?.slice(0,10)??"—"})]},t.slug))})]})})]}),s.length>0&&e.jsxs("section",{children:[e.jsx("h2",{children:"Dove l’estrazione trova più della documentazione scritta a mano"}),e.jsx("p",{className:"ov-sub",children:"È la ragione per cui la pipeline esiste: legge dai frame Figma cose che non erano mai state riportate."}),e.jsx("div",{className:"ov-scroll",children:e.jsxs("table",{children:[e.jsx("thead",{children:e.jsxs("tr",{children:[e.jsx("th",{children:"Componente"}),e.jsx("th",{children:"Campo"}),e.jsx("th",{className:"n",children:"Da Figma"}),e.jsx("th",{className:"n",children:"A mano"}),e.jsx("th",{className:"n",children:"Differenza"})]})}),e.jsx("tbody",{children:s.map((t,a)=>e.jsxs("tr",{children:[e.jsx("td",{children:e.jsx("b",{children:t.name})}),e.jsx("td",{children:t.field.replace(/([a-z])([A-Z])/g,"$1 $2")}),e.jsx("td",{className:"n ok",children:t.figma}),e.jsx("td",{className:"n",children:t.meta}),e.jsxs("td",{className:"n ok",children:["+",t.figma-t.meta]})]},a))})]})})]})]})}const d=`
.ov {
  --b: #14161b; --b2: #474d58; --b3: #7b828f;
  --line: #e3e5ea; --soft: #f7f8fa; --ok: #1d6b4a; --warn: #b3341f;
  background: #fff; color: var(--b2); min-height: 100%;
  font: 15px/1.62 ui-sans-serif, "Segoe UI", system-ui, sans-serif;
  padding: 2.3rem clamp(1.2rem, 5vw, 3.2rem) 5rem; max-width: 68rem; margin: 0 auto;
}
.ov * { box-sizing: border-box; }
.ov-head { border-bottom: 2px solid var(--b); padding-bottom: 1.2rem; }
.ov h1 { font: 600 clamp(1.9rem, 4.5vw, 2.6rem)/1.1 inherit; color: var(--b); margin: 0 0 .5rem; letter-spacing: -.015em; }
.ov-lead { margin: 0; max-width: 64ch; }
.ov-lead b { color: var(--b); }
.ov-stats { display: flex; flex-wrap: wrap; gap: 2.4rem; padding: 1.4rem 0; border-bottom: 1px solid var(--line); }
.ov-s { display: grid; gap: .1rem; }
.ov-s b { font: 600 1.9rem/1 inherit; color: var(--b); font-variant-numeric: tabular-nums; }
.ov-s span { font: .7rem/1 ui-monospace, Consolas, monospace; letter-spacing: .1em; text-transform: uppercase; color: var(--b3); }
.ov-note { background: var(--soft); border-left: 3px solid var(--b3); padding: .8rem 1rem; margin: 1.3rem 0 0; border-radius: 0 3px 3px 0; font-size: .93rem; max-width: 64ch; }
.ov-note b { color: var(--b); }
.ov section { padding-top: 2.2rem; }
.ov h2 { font: 600 .73rem/1.5 ui-monospace, Consolas, monospace; letter-spacing: .13em; text-transform: uppercase; color: var(--b3); margin: 0 0 .8rem; }
.ov-sub { font-size: .9rem; color: var(--b3); margin: -.4rem 0 .9rem; max-width: 62ch; }
.ov-scroll { overflow-x: auto; }
.ov table { border-collapse: collapse; width: 100%; min-width: 44rem; font-size: .9rem; }
.ov th { text-align: left; font: 400 .66rem/1 ui-monospace, Consolas, monospace; letter-spacing: .1em; text-transform: uppercase; color: var(--b3); padding: .5rem .8rem .5rem 0; border-bottom: 1px solid var(--b3); white-space: nowrap; }
.ov td { padding: .65rem .8rem .65rem 0; border-bottom: 1px solid var(--line); vertical-align: top; }
.ov td b { color: var(--b); display: block; }
.ov-id { display: block; font: .7rem/1.5 ui-monospace, Consolas, monospace; color: var(--b3); }
.ov-d { display: block; font-size: .82rem; color: var(--b3); margin-top: .2rem; max-width: 42ch; }
.ov-dots { display: flex; gap: .25rem; }
.ov-dots i {
  font: 600 .66rem/1.5rem ui-monospace, Consolas, monospace; font-style: normal;
  width: 1.5rem; height: 1.5rem; text-align: center; border-radius: 2px;
  background: var(--soft); color: var(--b3); border: 1px solid var(--line);
}
.ov-dots i.on { background: #e6f0ea; color: var(--ok); border-color: #bcd8c8; }
.ov-src { display: block; font: .68rem/1.5 ui-monospace, Consolas, monospace; color: var(--b3); margin-top: .3rem; }
.ov .n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.ov .z { color: var(--b3); }
.ov .ok { color: var(--ok); font-weight: 600; }
.ov-when { font: .78rem/1.5 ui-monospace, Consolas, monospace; color: var(--b3); white-space: nowrap; }
`,m=[{slug:"button",name:"Button",has:{contract:!0,figma:!0,intent:!0},id:"ds.button",purpose:`The Button is an interactive control that allows the user to trigger an action, submit a decision, start a process, or confirm an intent. It exists to make actionable choices clear, recognizable, and easy to activate across different product flows. 

The Button component is defined by two independent decision axes:\u2028
Hierarchy: defines the visual weight of the action within the screen:
Primary: the single main action of the screen or action context.
Secondary: an alternative, supporting, or equal-weight side action next to a Primary.
Ghost: a low-impact contextual action, such as Skip, Later, Show more, or similar non-blocking actions.
\u2028For all the status described above, an icon can be actived (left or right).\u2028
Appearance: defines the semantic context of the action:
Brand: product-level CTAs, such as Confirm, Continue, or Play.
Neutral: standard actions, technical actions, or settings-related actions, such as Save or Apply.
Accent: emphasised secondary actions that need more visibility without becoming the main action.
Danger: irreversible, destructive, or high-risk actions, such as Delete account or Cancel order.
Inverse: buttons placed on dark surfaces where the standard appearance would not provide the correct contextual contrast.`,antiPatterns:4,behaviorKeys:1,props:11,variantCount:90,dsContract:"b2c",dsIntent:"b2c",lastModified:"2026-08-06T09:49:15Z",reproducibility:{antiPatterns:{figma:4,metadata:5},behaviorKeys:{figma:6,metadata:1},commonPatterns:{figma:5,metadata:6},contentBlock:{figma:0,metadata:0}}},{slug:"fab",name:"FAB",has:{contract:!0,figma:!0,intent:!0},id:"ds.fab",purpose:`Use the FAB (Floating Action Button) only for actions that must remain always accessible during the scroll of a long page. It is a single, persistent action floating over the scrollable content, one instance per page. Implementation note: the FAB is an instance of the Button, so all styling and state visuals (Default, Pressed, Disabled) are delegated to the Button. The FAB exposes only two own properties: os (android, ios) and Label (yes, no, when no the FAB is the icon-only square).

Common scenarios in the DS Cross-App:

• Filter entry point: floating over the navbar, opens the filter bottom sheet. Only this pattern uses a Notification Badge on the icon, to surface the count of applied filters.
• Scroll-to-top: appears past a scroll threshold, hides near the top. Typically icon-only (Label=no).`,antiPatterns:5,behaviorKeys:0,props:2,variantCount:6,dsContract:"b2c",dsIntent:"b2c",lastModified:"2026-08-06T09:49:15Z",reproducibility:{antiPatternsInFigma:5,antiPatternsInMetadata:5,commonPatternsInMetadata:3,doBlocksInFigma:1}},{slug:"button-icon",name:"Icon Button",has:{contract:!0,figma:!0,intent:!0},id:"ds.button-icon",purpose:`An Icon Button is an interactive control that allows the user to trigger a single action through an icon alone, without a visible text label. It exists for compact contexts where the action is already clear from the icon, the surrounding interface, or a widely recognized convention.
The Icon Button should be used only when the icon can communicate the action without ambiguity. If the action requires explanation, carries risk, or is not immediately recognizable, use a Button with a visible label instead.

The Icon Button component is defined by two independent decision axes:\u2028
Hierarchy: defines the relative emphasis of the action within the current context:
Primary: the most important icon action in the current context.
Secondary: a standard icon action that must remain discoverable.
Ghost: a low-impact icon action used in compact or familiar contexts.\u2028
Appearance: defines the semantic context of the action
Brand: product-level icon actions that are clear from context.
Neutral: standard utility actions, such as close, back, share, search, or more.
Accent: emphasized secondary icon actions.
Danger: destructive or high-risk icon actions.
Inverse: icon actions placed on dark surfaces or image-based backgrounds.`,antiPatterns:11,behaviorKeys:1,props:5,variantCount:90,dsContract:"b2c",dsIntent:"b2c",lastModified:"2026-08-06T09:49:15Z",reproducibility:{antiPatterns:{figma:11,metadata:4},behaviorKeys:{figma:6,metadata:3},commonPatterns:{figma:4,metadata:3},contentBlock:{figma:1,metadata:0}}}],p={title:"Panoramica/Stato dell’estrazione",component:l},o={args:{index:m}};o.storyName="Stato dell’estrazione";o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  args: {
    index
  }
}`,...o.parameters?.docs?.source}}};const u=["Stato"];export{o as Stato,u as __namedExportsOrder,p as default};
