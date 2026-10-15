"""Reproducible timeline/rain adapter; no permanent edits to source DATs."""
import copy
C=me.parent()
ACTIVE=[]
RESTORE_PAR=None

def begin(cfg):
    global ACTIVE,RESTORE_PAR
    ACTIVE=[];RESTORE_PAR=C.op('sources').module.restore_par
    if cfg['mode']!='render' or not C.par.Repeatable.eval():return
    _,comps=C.op('sources').module.graph()
    for n in comps:
        if not C.op('sources').module.is_rain(n):continue
        eng=n.op('engine').module;native=n.op('native_logic').module;frame=n.op('frame_update')
        entry={'node':n,'frame':frame,'active':frame.par.active.eval(), 'engine':copy.deepcopy(eng.state(n)),
               'native':copy.deepcopy(native.state(n)), 'seed':C.op('sources').module.snapshot(n.par.Seed),'page':n.par.Page.eval(),
               'animate':C.op('sources').module.snapshot(n.par.Animate),'last':None}
        ACTIVE.append(entry);frame.par.active=False
        n.par.Seed=float(C.par.Renderseed.eval());n.par.Animate=True
        eng.state(n).update(clock=0.,last=None,pageclock=0.,dirty=False,render_dirty=False)
        n.op('motion_clock').par.value0=0
        native.rebuild(n)
    hook=C.par.Resetdat.eval()
    if hook:
        if not hook.isDAT:raise ValueError('Reset DAT 必须是 DAT')
        hook.module.onReset(C,int(C.par.Resetframe),float(cfg['plan']['fps']))

def step(frame,fps):
    for entry in ACTIVE:
        n=entry['node'];eng=n.op('engine').module;native=n.op('native_logic').module
        dt=0 if entry['last'] is None else 1/float(fps);entry['last']=frame
        st=eng.state(n);st['clock']+=dt*n.par.Speed.eval();st['last']=absTime.seconds
        n.op('motion_clock').par.value0=st['clock']
        if n.par.Paging=='auto':
            st['pageclock']+=dt
            if st['pageclock']>=n.par.Pageseconds.eval():
                st['pageclock']=0;n.par.Page=n.par.Page.eval()%max(1,n.par.Pagecount.eval())+1;st['render_dirty']=True
        if st.get('render_dirty'):
            eng.render_page(n);native.rebuild(n);st['render_dirty']=False
        if n.par.Displaymode=='htmlflow':native.tick(n,dt)

def restore():
    global ACTIVE
    entries=ACTIVE;ACTIVE=[]
    for ent in entries:
        n=ent['node']
        if not n.valid:continue
        RESTORE_PAR(n.par.Seed,ent['seed']);RESTORE_PAR(n.par.Animate,ent['animate'])
        n.par.Page=ent['page']
        eng=n.op('engine').module;native=n.op('native_logic').module
        eng._cache[n.id]=ent['engine'];eng._cache[n.id]['last']=absTime.seconds
        native.CACHE[n.id]=ent['native']
        n.op('motion_clock').par.value0=ent['engine']['clock']
        n.op('native_flow/dynamic_data').cook(force=True);n.op('native_flow/static_data').cook(force=True)
        ent['frame'].par.active=ent['active']
