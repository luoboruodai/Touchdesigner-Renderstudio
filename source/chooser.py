"""Reusable eight-row native menu: constant node count despite a growing format registry."""
C=me.parent()
STATE={'parameter':None,'page':0}

def show(parameter):
    STATE.update(parameter=parameter,page=0)
    C.op('engine').module.SYNCING=True
    try:C.par.Menusearch='';C.op('ui/menu_overlay/menu/search').par.text=''
    finally:C.op('engine').module.SYNCING=False
    C.op('ui/menu_overlay').par.display=True
    render()

def page(delta):
    STATE['page']=max(0,STATE['page']+delta);render()

def render(reset_page=False):
    if not STATE['parameter']:return
    if reset_page:STATE['page']=0
    p=C.par[STATE['parameter']];query=C.par.Menusearch.eval().strip().lower();items=list(zip(p.menuNames,p.menuLabels))
    if query:items=[x for x in items if query in (x[0]+' '+x[1]).lower()]
    pages=max(1,(len(items)+7)//8);STATE['page']=min(STATE['page'],pages-1)
    u=C.op('ui/menu_overlay/menu');u.op('menu_title').par.text=p.label
    u.op('count').par.text=f'{len(items)} 项 · 第 {STATE["page"]+1}/{pages} 页'
    for i in range(8):
        button=u.op('item_'+str(i));index=STATE['page']*8+i;button.par.display=index<len(items)
        if index<len(items):
            name,label=items[index];button.op('caption').par.text=label;button.store('action','Pick:'+p.name+':'+name)
    u.op('prev').par.enable=STATE['page']>0;u.op('next').par.enable=STATE['page']<pages-1
