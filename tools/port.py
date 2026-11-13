"""Turn the model's source page (a Claude artifact body) into the standalone public page.

usage: python3 tools/port.py <artifact-page.html> index.html
Adds a proper document head, milestone definition pop-ups, vertical gridlines, and public-facing wording.
"""
import sys,re
src,out=sys.argv[1],sys.argv[2]
s=open(src).read()
body=s.split('<meta name="claude:viewport-fit-sides" content="cover">',1)[1].rsplit('</body>',1)[0]
fontlink='<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap">'
assert body.count(fontlink)==1; body=body.replace(fontlink,'')
style_end=body.index('</style>')+len('</style>')
style,rest=body[:style_end].strip(),body[style_end:]
def tip(k,label): return '<button type="button" class="info" data-t="%s" aria-label="What is %s?">i</button>'%(k,label)
CSS_ADD='''
/* public-page additions: base reset, milestone definition pop-ups */
body{margin:0}
[hidden]{display:none!important}
.info,.info-inline{display:inline-flex;align-items:center;justify-content:center;flex:none;width:16px;height:16px;padding:0;margin:0 0 0 1px;border-radius:50%;border:1px solid var(--mute);background:transparent;color:var(--ink2);font:600 10.5px/1 var(--body);vertical-align:1px;cursor:help}
.info:hover,.info:focus-visible{background:var(--ink);border-color:var(--ink);color:var(--bg)}
.info:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.info-inline{cursor:default}
#infobox{position:absolute;z-index:20;max-width:min(300px,calc(100vw - 16px));background:var(--ink);color:#fff;font-size:13px;line-height:1.45;font-weight:400;padding:9px 11px;border-radius:7px;box-shadow:0 4px 14px rgba(0,0,0,.18);pointer-events:none}
</style>'''
style=style[:-len('</style>')]+CSS_ADD
JS_ADD='''  var $=function(id){return document.getElementById(id)};
  // Milestone definitions, borrowed from the AI Futures Project (aifuturesmodel.com, ai-2027.com).
  var DEFS={
    AC:"Automated Coder. An AI that can fully automate an AI company's coding work, replacing its entire software engineering staff.",
    SAR:"Superhuman AI Researcher. An AI that can fully automate AI research: it does the job of the best human AI researcher, but faster and cheaply enough to run lots of copies.",
    TED:"Top-Expert-Dominating AI. An AI that is at least as good as top human experts at virtually all cognitive tasks.",
    ASI:"Artificial Superintelligence. The gap between an ASI and the best humans is twice the gap between the best humans and the median professional, at virtually all cognitive tasks."
  };
  var infoBox=document.createElement("div");infoBox.id="infobox";infoBox.setAttribute("role","tooltip");infoBox.hidden=true;document.body.appendChild(infoBox);
  var infoOwner=null;
  function showInfo(b){var d=DEFS[b.getAttribute("data-t")];if(!d)return;infoOwner=b;infoBox.textContent=d;infoBox.hidden=false;
    var r=b.getBoundingClientRect(),w=infoBox.offsetWidth,h=infoBox.offsetHeight,vw=document.documentElement.clientWidth;
    var left=Math.min(Math.max(8,r.left+r.width/2-w/2),vw-w-8),top=r.top-h-8;if(top<8)top=r.bottom+8;
    infoBox.style.left=(left+window.scrollX)+"px";infoBox.style.top=(top+window.scrollY)+"px";b.setAttribute("aria-describedby","infobox")}
  function hideInfo(){infoBox.hidden=true;if(infoOwner)infoOwner.removeAttribute("aria-describedby");infoOwner=null}
  function infoOf(e){return e.target&&e.target.closest?e.target.closest(".info"):null}
  document.addEventListener("mouseover",function(e){var b=infoOf(e);if(b)showInfo(b)});
  document.addEventListener("mouseout",function(e){var b=infoOf(e);if(b&&b===infoOwner&&!b.contains(e.relatedTarget))hideInfo()});
  document.addEventListener("focusin",function(e){var b=infoOf(e);if(b)showInfo(b)});
  document.addEventListener("focusout",function(e){if(infoOf(e))hideInfo()});
  document.addEventListener("click",function(e){var b=infoOf(e);if(b){e.preventDefault();showInfo(b)}else hideInfo()});
  document.addEventListener("keydown",function(e){if(e.key==="Escape")hideInfo()});
  window.addEventListener("scroll",hideInfo,{passive:true});'''
reps=[
 # the explainer is a Claude Motion film with no video file to host
 ('<a class="vid" href="https://claude.ai/artifact/1Sp2nvdvyBCDnb5cPH5nTp">Watch the 30-second explainer</a>',''),
 ('<button id="reset" type="button">Reset defaults</button>','<button id="reset" type="button">Reset to default settings</button>'),
 ("Niel Bowerman and Claude's model of how","Niel Bowerman and Claude made a model of how"),
 ('<i class="dot" style="background:var(--sar)"></i>SAR</div>','<i class="dot" style="background:var(--sar)"></i>SAR '+tip('SAR','SAR')+'</div>'),
 ('<i class="dot" style="background:var(--ted)"></i>TED-AI</div>','<i class="dot" style="background:var(--ted)"></i>TED-AI '+tip('TED','TED-AI')+'</div>'),
 ('<i class="dot" style="background:var(--asi)"></i>ASI</div>','<i class="dot" style="background:var(--asi)"></i>ASI '+tip('ASI','ASI')+'</div>'),
 ('AC: automated coder</label>','AC: automated coder '+tip('AC','AC')+'</label>'),
 ('SAR, if there is an explosion</label>','SAR, if there is an explosion '+tip('SAR','SAR')+'</label>'),
 ('SAR, if there is not</label>','SAR, if there is not '+tip('SAR','SAR')+'</label>'),
 ('TED-AI: beats top experts</label>','TED-AI: beats top experts '+tip('TED','TED-AI')+'</label>'),
 ('ASI: superintelligence</label>','ASI: superintelligence '+tip('ASI','ASI')+'</label>'),
 ('<p class="hint">The definitions are the AI Futures Project\'s.</p>',
  '<p class="hint">The definitions are the <a href="https://www.aifuturesmodel.com/">AI Futures Project</a>\'s. Hover over or tap an <span class="info-inline">i</span> for the full definition.</p>'),
 ('  var $=function(id){return document.getElementById(id)};',JS_ADD),
 # vertical gridlines at every year
 ('function yearTicks(svg,X,y0,y1,base,narrow){for(var y=y0;y<=y1;y++){if(narrow',
  'function yearTicks(svg,X,y0,y1,base,narrow,top){for(var y=y0;y<=y1;y++){if(top!=null)el(svg,"line",{x1:X(y),x2:X(y),y1:top,y2:base,stroke:C.line,"stroke-width":1});if(narrow'),
 ('yearTicks(svg,X,2023,2027,c.H-mb,false)','yearTicks(svg,X,2023,2027,c.H-mb,false,mt)'),
 ('yearTicks(svg,X,2027,2032,c.H-mb,false)','yearTicks(svg,X,2027,2032,c.H-mb,false,mt)'),
 ('yearTicks(svg,X,2024,2031,c.H-mb,c.W<420)','yearTicks(svg,X,2024,2031,c.H-mb,c.W<420,mt)'),
 ('yearTicks(svg,X,2024,2035,c.H-mb,narrow)','yearTicks(svg,X,2024,2035,c.H-mb,narrow,mt)'),
 # definitions on chart milestone labels
 ('labels.push({y:Y(M.prob(m[0],x1)),s:m[1],c:m[2]});','labels.push({y:Y(M.prob(m[0],x1)),s:m[1],c:m[2],k:m[0]});'),
 ('txt(svg,c.W-mr+17,l.y+4,l.s,{fill:C.ink,w:600,halo:false})});','var lt=txt(svg,c.W-mr+17,l.y+4,l.s,{fill:C.ink,w:600,halo:false});el(lt,"title",{},l.s+": "+DEFS[l.k])});'),
 ('LV.forEach(function(l){txt(svg,c.W-mr-3,Y(l[3])-5,l[2],{a:"end",fill:C.ink,w:600})});','LV.forEach(function(l){var lt=txt(svg,c.W-mr-3,Y(l[3])-5,l[2],{a:"end",fill:C.ink,w:600});el(lt,"title",{},DEFS[l[0]])});'),
]
doc=style+rest
for a,b in reps:
    n=doc.count(a)
    if n!=1: sys.exit("expected 1 match, got %d: %s"%(n,a[:70]))
    doc=doc.replace(a,b)
assert 'claude.ai' not in doc and not re.search('memo',doc,re.I)
head='''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>AI Timelines Model</title>
<meta name="description" content="An interactive model of how AI progress could unfold after the METR report: three regimes, four milestones, adjustable assumptions.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
'''+fontlink+'\n'
style_part,body_part=doc.split('</style>',1)
open(out,'w').write(head+style_part+'</style>\n</head>\n<body>'+body_part.rstrip()+'\n</body>\n</html>\n')
print("ok")
