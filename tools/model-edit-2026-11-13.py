import sys,re
src,out=sys.argv[1],sys.argv[2]
s=open(src).read()
s=s.split('</head><body>',1)[1].rsplit('</body>',1)[0].strip()+'\n'
def lit(a,b):
    global s
    n=s.count(a)
    if n!=1: sys.exit("lit: expected 1, got %d: %s"%(n,a[:80]))
    s=s.replace(a,b)
def rx(p,b):
    global s
    s,n=re.subn(p,lambda m:b,s,flags=re.S)
    if n!=1: sys.exit("rx: expected 1, got %d: %s"%(n,p[:80]))

# ---------- CSS
lit('.note{border-top:1px solid var(--rule)','''.tip .sw{width:18px}
.tablebox{overflow-x:auto;margin-top:16px}
.blend{border-collapse:collapse;width:100%;min-width:470px;font-size:13px;font-variant-numeric:tabular-nums}
.blend caption{caption-side:top;text-align:left;font-size:11.5px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;color:var(--ink2);padding-bottom:6px}
.blend th,.blend td{text-align:left;padding:6px 12px 6px 0;border-bottom:1px solid var(--line);white-space:nowrap}
.blend thead th{font-weight:600;color:var(--ink2);font-size:12px;vertical-align:bottom}
.blend thead th b{color:var(--ink);margin-left:3px}
.blend .sw{display:inline-block;vertical-align:middle;margin-right:6px}
.blend .dot{display:inline-block;margin-right:6px}
.blend tbody th{font-weight:600}
.blend td:last-child,.blend thead th:last-child{font-weight:600;color:var(--ink);padding-right:0}
.note{border-top:1px solid var(--rule)''')

# ---------- Step 1: the toggle is a way of reading the chart, nothing more
rx(r'<p class="hint">Two lines: the pace changed once.*?</p>\s*<div id="slotT1"></div>',
 '<p class="hint">Two lines: the pace changed once, in October 2025. A line that curves away: progress has been pulling away from the old straight line faster and faster since 2024, which is how an explosion would look from the inside.</p>\n          <p class="hint">This switch only changes how the chart is drawn. The forecast does not use it. If the curve looks right to you, that is a reason to give the explosion more weight in step 4.</p>')

# ---------- Step 2: regimes describe behaviour only; credences move to step 4
lit('Set how likely you think each one is, and how it behaves.','Set how each one behaves here. You say how likely each one is in step 4, once you have seen where it leads.')
rx(r'\s*<div class="ctl"><label for="wExp">How likely</label>.*?</div>\s*<p class="hint" id="expNote"></p>\s*<div id="slotT2"></div>','')
rx(r'\s*<div class="ctl"><label>How likely \(the rest\)</label>.*?</div></div></div>','')
rx(r'\s*<div class="ctl"><label for="wOne">How likely</label>.*?</div>','')

# ---------- hover read-outs on the pace and capability charts too
lit('<div class="tip" id="tip" hidden></div>','<div class="tip" id="tip_cProb" hidden></div>')
lit('aria-label="Pace of AI progress over time in each regime"></svg>','aria-label="Pace of AI progress over time in each regime"></svg><div class="tip" id="tip_cRate" hidden></div>')
lit('aria-label="Capability over time in each regime, with milestone heights"></svg>','aria-label="Capability over time in each regime, with milestone heights"></svg><div class="tip" id="tip_cCap" hidden></div>')

# ---------- Step 4: credences beside the forecast, and a table showing how the blend is made up
lit('then blends the three regimes by how likely you said each is.','then blends the three regimes by how likely you think each one is, which you set here.')
rx(r'</div></div>\s*<div class="ctls">\s*<div class="grp"><h3>Uncertainty within a regime</h3>','''</div>
        <div class="tablebox"><table class="blend"><caption>What goes into the blend</caption>
          <thead><tr><th scope="col">Median date</th><th scope="col"><i class="sw"></i>Explosion<b id="w_exp"></b></th><th scope="col"><i class="sw bnd"></i>Compute-bounded<b id="w_bnd"></b></th><th scope="col"><i class="sw one"></i>One-off step<b id="w_one"></b></th><th scope="col">All three blended</th></tr></thead>
          <tbody id="blendBody"></tbody></table></div>
        <p class="hint" style="margin-top:8px">Each regime's median date comes from step 3. The percentages are your credences. The blended date is when the chart above crosses 50%.</p></div>
      <div class="ctls">
        <div class="grp"><h3>How likely is each regime</h3>
          <div class="split" id="split"><div class="e"></div><div class="b"></div><div class="o"></div></div>
          <div class="splitkey"><span>Explosion</span><span>Compute-bounded</span><span>One-off</span></div>
          <div class="ctl"><label for="wExp"><i class="sw"></i>Software-only explosion</label><output id="o_wExp"></output><input type="range" id="wExp" min="0" max="100" step="1"></div>
          <div class="ctl"><label for="wOne"><i class="sw one"></i>One-off step</label><output id="o_wOne"></output><input type="range" id="wOne" min="0" max="100" step="1"></div>
          <p class="hint">Compute-bounded gets the rest: <b id="o_wBnd"></b>. These credences are the biggest lever on the forecast.</p></div>
        <div class="grp"><h3>Uncertainty within a regime</h3>''')

# ---------- JS: model no longer branches on the reading of the dots
rx(r'var smooth=\$\("fitSmooth"\)\.checked,fit=null;.*?\n    var ese=0,en=0;','var ese=0,en=0;')
lit('r0:p.r0,T:p.T,fit:fit,kinkRmse','r0:p.r0,T:p.T,kinkRmse')
# the curve is fitted once, to the dots alone: when it runs away is fitted too, and no slider touches it
lit('  var BRK=2025.77;','''  var BRK=2025.77;
  // "A line that curves away": score = old straight line + A*h(t), leaving the line in 2024 with no jump and no kink and
  // running away at tc. A and tc are both fitted to the dots. It is a way of reading the chart and feeds nothing downstream.
  function fitCurve(tc){var TS=2024,d0=tc-TS,shh=0,shz=0,sse=0;
    var hh=function(t){return t>TS?1/Math.pow(tc-t,2)-1/(d0*d0)-2*(t-TS)/Math.pow(d0,3):0},line=function(t){return 149.5+15*(t-BRK)};
    FITPTS.forEach(function(h){var x=hh(h[1]),z=h[2]-line(h[1]);shh+=x*x;shz+=x*z});
    var A=Math.max(0,shz/shh),score=function(t){return line(t)+A*hh(t)};FITPTS.forEach(function(h){var e=score(h[1])-h[2];sse+=e*e});
    return {tc:tc,rmse:Math.sqrt(sse/(FITPTS.length-2)),now:1+(A/15)*(2/Math.pow(tc-T0,3)-2/Math.pow(d0,3)),score:score,line:line}}
  var CURVE=(function(){var best=null,lo=null,hi=null,d,c;for(d=0.3;d<=15;d+=0.01){c=fitCurve(T0+d);if(!best||c.rmse<best.rmse)best=c}
    for(d=0.3;d<=15;d+=0.01){c=fitCurve(T0+d);if(c.rmse<=best.rmse+0.1){if(!lo)lo=c;hi=c}}best.lo=lo;best.hi=hi;return best})();
  function roughDate(d){var y=Math.floor(d),f=d-y;return (f<1/3?"early ":f<2/3?"mid-":"late ")+y}''')

# drawHist reads the toggle itself
a=s.index('  function drawHist(M){'); b=s.index('  var probGeom=null;')
h=s[a:b]
assert h.count('M.fit')>5
h=h.replace('M.fit','F').replace('function drawHist(M){','function drawHist(M){\n    var F=$("fitSmooth").checked?CURVE:null;',1)
h,n=re.subn(r'\$\("fitNote"\)\.textContent=.*?;\n\s*\$\("expNote"\)\.textContent=.*?;\n',
 lambda m:'''$("fitNote").textContent=sm?"The best-fitting curve runs away in "+roughDate(F.tc)+", but any date from "+roughDate(F.lo.tc)+" to "+roughDate(F.hi.tc)+" fits about as well. It misses Anthropic's models by "+F.rmse.toFixed(1)+" points on average, and the two straight lines miss by "+M.kinkRmse.toFixed(1)+". The error bars on each dot are several points, so the data cannot tell the two readings apart.":"The two straight lines miss Anthropic's models by "+M.kinkRmse.toFixed(1)+" points on average, with the earlier line carried back to Claude 2 in 2023.";
''',h,flags=re.S)
assert n==1
s=s[:a]+h+s[b:]

# generic crosshair read-out, shared by three charts
a=s.index('  var probGeom=null;'); s=s[:a]+s[a:].replace('  var probGeom=null;\n','',1)
rx(r'  function hover\(ev\)\{.*?\n  function unhover\(\)\{.*?\}\n','''  var GEOM={},KDOT=function(c){return "<i class=\\"dot\\" style=\\"background:"+c+"\\"></i>"},KSW={exp:"<i class=\\"sw\\"></i>",bnd:"<i class=\\"sw bnd\\"></i>",one:"<i class=\\"sw one\\"></i>"};
  function hoverLayer(svg,id,n,top,bot){var g=el(svg,"g",{id:id+"_hv",visibility:"hidden","pointer-events":"none"});el(g,"line",{id:id+"_hl",y1:top,y2:bot,stroke:C.ink2,"stroke-width":1});for(var i=0;i<n;i++)el(g,"circle",{id:id+"_hd"+i,r:4.5,stroke:C.bg,"stroke-width":2})}
  function hover(id,ev){
    var g=GEOM[id];if(!g)return;var svg=$(id),r=svg.getBoundingClientRect(),px=(ev.clientX-r.left)*g.W/r.width;
    var t=g.x0+(px-g.ml)/(g.W-g.ml-g.mr)*(g.x1-g.x0),tip=$("tip_"+id);
    if(t<g.x0||t>g.x1){unhover(id);return}
    $(id+"_hv").setAttribute("visibility","visible");$(id+"_hl").setAttribute("x1",g.X(t));$(id+"_hl").setAttribute("x2",g.X(t));
    var rows=g.rows(t),h="<b>"+dateLabel(t)+"</b>";
    for(var i=0;i<g.n;i++){var d=$(id+"_hd"+i),q=rows[i];if(q&&q.y!=null){d.setAttribute("cx",g.X(t));d.setAttribute("cy",q.y);d.setAttribute("fill",q.c);d.setAttribute("visibility","inherit")}else d.setAttribute("visibility","hidden")}
    rows.forEach(function(q){h+="<span>"+q.key+q.s+"</span>"});
    tip.innerHTML=h;tip.hidden=false;var sx=g.X(t)*r.width/g.W,w=tip.offsetWidth;tip.style.left=Math.max(0,Math.min(r.width-w,sx<r.width/2?sx+12:sx-w-12))+"px";
  }
  function unhover(id){(id?[id]:Object.keys(GEOM)).forEach(function(k){var h=$(k+"_hv");if(h)h.setAttribute("visibility","hidden");var t=$("tip_"+k);if(t)t.hidden=true})}
''')
rx(r'    var g=el\(svg,"g",\{id:"hover",visibility:"hidden"\}\);.*?probGeom=\{[^}]*\};','''    hoverLayer(svg,"cProb",3,mt,c.H-mb);
    GEOM.cProb={X:X,x0:x0,x1:x1,ml:ml,mr:mr,W:c.W,n:3,rows:function(t){return MS.map(function(m){var v=M.prob(m[0],t);return {c:m[2],y:Y(v),key:KDOT(m[2]),s:m[1]+" "+Math.round(v*100)+"%"}})}};''')
lit('    lb.forEach(function(l){txt(svg,c.W-mr-2,l.y,l.s,{a:"end",fill:C.ink,w:600})});','''    lb.forEach(function(l){txt(svg,c.W-mr-2,l.y,l.s,{a:"end",fill:C.ink,w:600})});
    hoverLayer(svg,"cRate",3,mt,c.H-mb);
    GEOM.cRate={X:X,x0:x0,x1:x1,ml:ml,mr:mr,W:c.W,n:3,rows:function(t){
      if(t<T0){var r=t<BRK?1:M.r0;return [{c:C.ink,y:Y(r),key:KSW.exp,s:"Measured pace "+r.toFixed(2)+"x"}]}
      return ["exp","bnd","one"].map(function(k){var r=M.R[k].rate(t-T0),off=!isFinite(r)||r>100;return {c:REG[k].stroke,y:off?null:Y(r),key:KSW[k],s:REG[k].name+" "+(off?"over 100x":(r>=10?r.toFixed(0):r.toFixed(1))+"x")}})}};''')
lit('    else{txt(svg,ml+6,mt+12,"solid: explosion · dashed: compute-bounded · dotted: one-off",{size:10.5,fill:C.ink2})}','''    else{txt(svg,ml+6,mt+12,"solid: explosion · dashed: compute-bounded · dotted: one-off",{size:10.5,fill:C.ink2})}
    hoverLayer(svg,"cCap",3,mt,c.H-mb);
    GEOM.cCap={X:X,x0:x0,x1:x1,ml:ml,mr:mr,W:c.W,n:3,rows:function(t){
      if(t<T0){var v=Hh.past(t);return [{c:C.ink,y:Y(v),key:KSW.exp,s:"Measured: "+(-v).toFixed(1)+" years of progress before today"}]}
      return ["exp","bnd","one"].map(function(k){var q=M.R[k].cap(t-T0),off=!isFinite(q)||q>ymax;return {c:REG[k].stroke,y:off?null:Y(q),key:KSW[k],s:REG[k].name+" "+(off?"off the chart":"+"+q.toFixed(1)+" years")}})}};''')
# every crossing dot on the capability chart names itself
lit('      el(svg,"circle",{cx:X(d),cy:Y(hh),r:5,fill:m[1],stroke:C.bg,"stroke-width":2});','      var cd=el(svg,"circle",{cx:X(d),cy:Y(hh),r:5,fill:m[1],stroke:C.bg,"stroke-width":2});el(cd,"title",{},REG[k].name+" reaches "+(m[0]==="TED"?"TED-AI":m[0])+": "+dateLabel(d));')

# results: the blend table
lit('    var w=[p.wExp,Math.max(0,100-p.wExp-p.wOne),p.wOne],ch=$("split").children;','''    var w=[p.wExp,Math.max(0,100-p.wExp-p.wOne),p.wOne],ch=$("split").children,rows="";
    ["exp","bnd","one"].forEach(function(k,i){$("w_"+k).textContent=w[i]+"%"});
    MS.forEach(function(m){rows+="<tr><th scope=\\"row\\">"+KDOT(m[2])+m[1]+"</th>";["exp","bnd","one"].forEach(function(k){rows+="<td>"+dateLabel(T0+M.R[k].cross(M.hgt(m[0],k)))+"</td>"});rows+="<td>"+dateLabel(M.pct(m[0],0.5))+"</td></tr>"});
    $("blendBody").innerHTML=rows;''')

# render / start
rx(r'\n\s*var slot=\$\(\$\("fitSmooth"\)\.checked\?"slotT1":"slotT2"\),ct=\$\("ctlT"\);if\(ct\.parentNode!==slot\)slot\.appendChild\(ct\);','')
rx(r'var PRESETS=\{.*?\};','var PRESETS={"default":{},aifp:{wExp:85,wOne:5,T:1.25},paul:{wExp:67,wOne:8,T:1},sentinel:{wExp:55,wOne:15,T:0.6,sig:0.65}};')
lit('set(q);$(v.smooth?"fitSmooth":"fitKink").checked=true;$("preset").value=name;','set(q);$("preset").value=name;')
lit('$("reset").addEventListener("click",function(){applyPreset("default")});$("fitKink").addEventListener("change",function(){$("preset").value="custom";render()});$("fitSmooth").addEventListener("change",function(){$("preset").value="custom";render()});',
    '$("reset").addEventListener("click",function(){$("fitKink").checked=true;applyPreset("default")});$("fitKink").addEventListener("change",function(){render()});$("fitSmooth").addEventListener("change",function(){render()});')
rx(r'var pp=\$\("pProb"\);pp\.addEventListener\("pointermove",hover\);pp\.addEventListener\("pointerdown",hover\);pp\.addEventListener\("pointerleave",unhover\);',
   '["cProb","cRate","cCap"].forEach(function(id){var sv=$(id);sv.addEventListener("pointermove",function(e){hover(id,e)});sv.addEventListener("pointerdown",function(e){hover(id,e)});sv.addEventListener("pointerleave",function(){unhover(id)})});')
for dead in ['slotT','expNote','probGeom','fitSmooth").checked,fit','v.smooth']:
    assert dead not in s, dead
open(out,'w').write(s)
print('ok',len(s))
