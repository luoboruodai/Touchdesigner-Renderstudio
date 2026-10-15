"""Live source resolution and reversible ownership of connected output dimensions."""
import copy,time,posixpath
C=me.parent()
UPDATING=False
WATCH=0
LAST=None
LAST_SCAN=0.0
RAIN_NODES=[]
PENDING=None

def raw_source():
    if str(C.par.Source.val).strip() or C.par.Source.mode!=ParMode.CONSTANT:
        n=C.par.Source.eval()
        return n if n and n.isTOP else None
    ins=C.op('in_source')
    return ins if C.inputs else None

def source_path():
    n=raw_source()
    return n.path if n else ''

def graph():
    src=raw_source()
    if not src:return [],[]
    queue=[src];seen=set();tops=[];comps=[];seencomp=set()
    while queue and len(seen)<500:
        n=queue.pop(0)
        if not n or n.id in seen:continue
        seen.add(n.id)
        if n.path.startswith(C.path+'/') and n!=C.op('in_source'):continue
        tops.append(n)
        par=n.parent()
        while par and par.path not in ('/','/project1') and par!=C:
            # Only custom output dimensions, never container width/height or UI dimensions.
            a=getattr(par.par,'Width',None);b=getattr(par.par,'Height',None)
            if a and b and a.isCustom and b.isCustom and ('输出' in a.label or 'output' in a.label.lower() or par.op('native_logic')):
                if par.id not in seencomp:comps.append(par);seencomp.add(par.id)
                break
            par=par.parent()
        if any(n.path.startswith(x.path+'/') for x in comps):continue
        queue.extend(n.inputs)
        if n.OPType=='selectTOP':
            ref=n.par.top.eval()
            if ref:queue.append(ref)
        if n.OPType=='inTOP':queue.extend(n.parent().inputs)
    return tops,comps

def is_rain(n):return bool(n and n.op('native_logic') and n.op('motion_clock') and n.op('frame_update') and hasattr(n.par,'Seed'))

def snapshot(p):
    return {'value':p.val,'expression':p.expr or '', 'bind':p.bindExpr or '', 'mode':str(p.mode).split('.')[-1], 'readonly':p.readOnly}

def restore_par(p,s):
    p.readOnly=False;p.mode=ParMode.CONSTANT;p.val=s['value'];p.expr=s['expression'];p.bindExpr=s['bind'];p.mode=getattr(ParMode,s['mode']);p.readOnly=s['readonly']

def resolve_row(row):return C.op(row['node'])

def release():
    rows=C.fetch('rs11_dimensions',[]);restored=0
    for row in rows:
        n=resolve_row(row)
        if not n:continue
        p=getattr(n.par,row['par'],None)
        if p and p.expr==row['ours']:
            restore_par(p,row['old']);restored+=1
    C.store('rs11_dimensions',[])
    if C.op('managed_nodes'):C.op('managed_nodes').clear();C.op('managed_nodes').appendRow(['node','parameter','original','managed'])
    return restored

def dimension_targets():
    tops,comps=graph();targets=[]
    for n in comps:targets.extend([(n,'Width','Width'),(n,'Height','Height')])
    # Only actual image-output chain, not material textures, glyph atlases or UI nodes.
    allowed={'constantTOP','noiseTOP','textTOP','glslTOP','renderTOP','resolutionTOP','moviefileinTOP'}
    for n in tops:
        if n==C.op('in_source') or any(n.path.startswith(x.path+'/') for x in comps):continue
        if n.OPType in allowed:
            for par,key in [('outputresolution','mode'),('resolutionw','Width'),('resolutionh','Height')]:
                if hasattr(n.par,par):targets.append((n,par,key))
    return targets,comps

def sync_dimensions():
    global UPDATING
    if UPDATING:return
    UPDATING=True
    try:
        rows=C.fetch('rs11_dimensions',[])
        if not C.par.Masterres.eval():
            if rows:release()
            C.par.Managedinfo='仅控制导出尺寸；上游已释放'
            comps=graph()[1]
            for n in comps:
                if is_rain(n) and n.op('engine').module.state(n).get('dirty'):
                    n.op('measure_font').cook(force=True);n.op('engine').module.rebuild(n)
            return comps
        targets,comps=dimension_targets();wanted={(posixpath.relpath(n.path,C.path),name) for n,name,key in targets}
        kept=[]
        for row in rows:
            n=resolve_row(row)
            if not n:continue
            if (row['node'],row['par']) not in wanted:
                p=n.par[row['par']]
                if p.expr==row['ours']:restore_par(p,row['old'])
            else:kept.append(row)
        existing={(x['node'],x['par']):x for x in kept}
        changed=set()
        for n,name,key in targets:
            p=n.par[name];nk=(posixpath.relpath(n.path,C.path),name)
            expr="'custom'" if key=='mode' else 'me.parent().op('+repr(posixpath.relpath(C.path,n.parent().path))+').par.'+key
            row=existing.get(nk)
            if not row:
                # Do not steal a binding owned by another render component.
                if p.mode==ParMode.EXPRESSION and 'RenderStudio' in (p.expr or '') and p.expr!=expr:continue
                row={'node':nk[0],'par':name,'old':snapshot(p),'ours':expr};kept.append(row)
            row['ours']=expr
            if p.expr!=expr or p.mode!=ParMode.EXPRESSION:
                p.readOnly=False;p.expr=expr;p.mode=ParMode.EXPRESSION
                if p.isCustom:p.readOnly=True
                changed.add(n.path)
        if kept!=rows:C.store('rs11_dimensions',kept)
        table=C.op('managed_nodes')
        desired=[['node','parameter','original','managed']]+[[row['node'],row['par'],str(row['old']['value']),row['ours']] for row in kept]
        if [[str(x) for x in row] for row in table.rows()]!=desired:
            table.clear()
            for row in desired:table.appendRow(row)
        C.par.Managedinfo=f'统一接管 {len(set(x["node"] for x in kept))} 个输出节点 / {len(kept)} 项尺寸参数'
        # Deferred refresh handles source parameter changes even while the timeline is paused.
        for n in comps:
            if is_rain(n):
                e=n.op('engine').module;st=e.state(n)
                if n.path in changed or st.get('dirty'):
                    n.op('measure_font').cook(force=True);e.rebuild(n)
        return comps
    finally:UPDATING=False

def live_sync():
    global LAST,LAST_SCAN,RAIN_NODES
    e=C.op('engine').module
    if e.busy():return
    n=raw_source();audio=C.par.Audio.eval()
    signature=(n.id if n else None,n.path if n else '',tuple(x.id for x in n.inputs) if n else (),str(C.par.Source.val),audio.id if audio else None,audio.path if audio else '',C.par.Width.eval(),C.par.Height.eval(),C.par.Masterres.eval())
    dirty=any(x.valid and x.op('engine').module.state(x).get('dirty') for x in RAIN_NODES)
    now=time.monotonic()
    if signature==LAST and now-LAST_SCAN<1 and not dirty:return
    LAST_SCAN=now
    # Binding path always resolves dynamically; detect renames/replacement even without a Par value event.
    comps=sync_dimensions();RAIN_NODES=[x for x in comps or [] if is_rain(x)]
    if not n:
        C.par.Sourceinfo='未连接 / 路径失效'
        if signature!=LAST:
            C.op('source_select').par.top='';C.par.Message='请选择有效的源TOP或接入图像端口';e.refresh_ui();LAST=signature
        return
    if n.path.startswith(C.path+'/') and n!=C.op('in_source'):
        C.par.Sourceinfo='源不能指向导出器内部';return
    if signature!=LAST:
        sel=C.op('source_select');sel.par.top.expr='';sel.par.top=n.path
        n.cook(force=True);sel.cook(force=True);C.op('prepared').cook(force=True)
    # Existing TOP connections propagate pixel updates; no redundant idle force-cook.
    C.op('writer').par.audiochop=audio if audio else ''
    C.par.Sourceinfo=f'{n.path} · 音频: '+(audio.path if audio else '无')
    C.par.Determinism='代码雨固定种子 / 固定步长' if any(is_rain(x) for x in (comps or [])) else '时间线复位；其它状态型组件需 Reset DAT'
    if signature!=LAST:
        LAST=signature;e.refresh_ui()

def watch(token):
    if not C.valid or token!=WATCH:return
    try:live_sync()
    except Exception as exc:
        if not C.op('engine').module.busy():C.par.Sourceinfo='源同步提示：'+str(exc)
    if C.valid:run(watch,token,delayMilliSeconds=100,delayRef=op.TDResources,group='rs12_live_'+str(C.id))

def start_watch():
    global WATCH
    WATCH+=1
    for item in list(runs):
        if item.group=='rs12_live_'+str(C.id):item.kill()
    run(watch,WATCH,delayFrames=2,delayRef=op.TDResources,group='rs12_live_'+str(C.id))

def settle():
    global PENDING
    PENDING=None
    if not C.valid:return
    live_sync();C.op('engine').module.refresh_ui()

def changed(name):
    global PENDING
    if PENDING:
        try:PENDING.kill()
        except Exception:pass
    PENDING=run(settle,delayFrames=1,delayRef=op.TDResources)

def release_action():
    C.par.Masterres=False;count=release();C.op('engine').module.status(f'已恢复 {count} 项上游原分辨率设置','就绪');settle()
