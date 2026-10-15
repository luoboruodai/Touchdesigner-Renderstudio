"""Render Studio host adapter. Embedded as a DAT; no external files or packages required."""
from pathlib import Path
import time, math, json, tempfile, os, traceback

C = me.parent()
S = None
TOKEN = 0
SYNCING = False
LOCK_KEY = 'render_studio_timeline_owner_v1'

def sources():return C.op('sources').module
def deterministic():return C.op('determinism').module
def encoder():return C.op('encoding').module

def catalog():return C.op('catalog').module
def core(): return C.op('export_core').module

def value(name): return C.par[name].eval()

def status(message, state=None):
    if not C.valid: return
    C.par.Message = str(message)
    if state is not None: C.par.State = state

def note(message):
    if not C.valid: return
    d=C.op('session_log')
    d.appendRow([time.strftime('%H:%M:%S'),str(message)])
    while d.numRows>80:d.deleteRow(1)

def busy():return bool(S)

def independent_run(fn, *args, frames=1):
    return run(fn,*args,delayFrames=frames,delayRef=op.TDResources,fromOP=root)

def snapshot_time():
    t=root.time
    return dict(play=t.play,frame=t.frame,rate=project.cookRate,realTime=project.realTime,
                start=t.start,end=t.end,rangeStart=t.rangeStart,rangeEnd=t.rangeEnd,loop=t.loop)

def restore_time(saved):
    t=root.time;t.play=False
    # Enlarge before shrinking to avoid range setters clamping each other.
    t.start=min(t.start,saved['start']);t.end=max(t.end,saved['end'])
    t.rangeStart=saved['rangeStart'];t.rangeEnd=saved['rangeEnd']
    t.start=saved['start'];t.end=saved['end'];t.loop=saved['loop']
    project.cookRate=saved['rate'];t.frame=saved['frame'];project.realTime=saved['realTime'];t.play=saved['play']

def resolve_source():
    raw=str(C.par.Source.val).strip()
    if raw or C.par.Source.mode!=ParMode.CONSTANT:
        node=C.par.Source.eval()
        if node is None or not node.isTOP:raise core().ExportError('图像源无效：请拖入一个 TOP，或连接到组件输入端')
    else:
        source=C.op('in_source')
        if not C.inputs:raise core().ExportError('尚未连接图像源：拖入 TOP 到“图像源”，或连接组件的 TOP 输入端')
        node=source
    if node.path.startswith(C.path+'/') and node!=C.op('in_source'):
        raise core().ExportError('不能把导出器自己的预览/输出设为源，避免循环依赖')
    # source_select uses a live expression; never cache a selected OP path here.
    node.cook(force=True)
    if node.errors():raise core().ExportError('图像源报错：'+node.errors())
    prepared=C.op('prepared');prepared.cook(force=True)
    if prepared.width<1 or prepared.height<1:raise core().ExportError('图像源没有有效分辨率')
    if value('Size')=='custom' and (prepared.width,prepared.height)!=(int(value('Width')),int(value('Height'))):
        raise core().ExportError(f'请求尺寸超出宿主限制，实际为 {prepared.width}×{prepared.height}。请降低分辨率或检查许可证')
    return node,prepared

def settings(mode='render'):
    k=core();src,prepared=resolve_source();cat=catalog()
    plan=k.frame_plan(value('Start'),value('End'),value('Fps'),value('Warmup')) if mode=='render' else k.frame_plan(0,0,value('Fps'))
    kind=value('Kind');codec=value('Codec');container=value('Container');audio=C.par.Audio.eval()
    if codec not in cat.CODECS:raise k.ExportError('请选择有效的渲染编码器')
    spec=cat.CODECS[codec];alpha=bool(value('Alpha') or spec['force_alpha'])
    backend=cat.select_backend(codec,container,value('Backend')) if kind=='movie' else 'native'
    if kind=='movie':cat.validate(container,codec,prepared.width,prepared.height,plan['fps'],alpha)
    if (str(C.par.Audio.val).strip() or C.par.Audio.mode!=ParMode.CONSTANT) and (audio is None or not audio.isCHOP):raise k.ExportError('音频源无效')
    if audio and (kind=='sequence' or container=='gif'):raise k.ExportError('图像序列/GIF不携带音频')
    if audio and audio.numChans not in (1,2):raise k.ExportError('音频须为1或2声道CHOP')
    if audio and mode=='record' and not audio.isTimeSlice:raise k.ExportError('实时录制须使用开启Time Slice的音频CHOP')
    audio_offline=None
    if audio and mode=='render':
        if audio.isTimeSlice:raise k.ExportError('逐帧渲染需要含完整数据的非时间切片音频CHOP（如 Wave/Script CHOP 或经缓存录制的数据；Audio File In 为时间切片，不可直接使用）；实时输入请改用实时录制')
        audio.cook(force=True)
        if audio.numSamples<1:raise k.ExportError('音频源没有可读取的样本')
        audio_offline=k.audio_plan(value('Start'),value('End'),value('Fps'),audio.rate,audio.numSamples)
    ffmpeg=encoder().validate(codec,bool(audio),container) if backend=='ffmpeg' else None
    if not ffmpeg and audio_offline:ffmpeg=encoder().validate_audio(container)
    if backend=='native' and codec in ('h264','h265'):
        k.validate_codec(codec,kind,alpha,root.licenseType,bool(audio))
    resolved=k.codec_name('rle' if backend=='ffmpeg' else spec['td'],list(C.op('writer').par.videocodec.menuNames)) if kind=='movie' else None
    if mode=='render' and value('Repeatable'):
        origin=int(value('Resetframe'))
        if origin>plan['start']:raise k.ExportError('统一起点帧不能晚于导出起始帧')
        plan['warm_start']=min(plan['warm_start'],origin)
    image=value('Imageformat')
    if image not in k.IMAGES:raise k.ExportError('不支持的图像格式')
    if kind=='sequence' and value('Alpha') and image=='jpeg':raise k.ExportError('JPEG不支持Alpha')
    folder=k.resolve_folder(value('Folder'),str(project.folder))
    if folder.exists() and not folder.is_dir():raise k.ExportError('导出路径不是文件夹')
    if not folder.exists() and not value('Createfolder'):raise k.ExportError('目录不存在；请创建或启用自动创建目录')
    folder.mkdir(parents=True,exist_ok=True)
    try:
        with tempfile.TemporaryFile(dir=str(folder)) as f:f.write(b'probe');f.flush()
    except OSError as exc:raise k.ExportError('目录不可写：'+str(exc))
    suffix=k.IMAGES[image] if kind=='sequence' else cat.CONTAINERS[container]['ext']
    target=k.target_path(folder,value('Filename'),suffix,kind=='sequence',value('Conflict'))
    if mode=='record' and float(value('Seconds'))<=0:raise k.ExportError('录制时长必须大于0')
    if value('Lossless') and codec not in ('h264','h264rgb','h265','hevc10'):raise k.ExportError('此无损开关仅适用于软件H.26x编码；其它格式按其编码定义输出')
    return dict(plan=plan,kind=kind,codec=codec,codec_actual=resolved,image=image,audio=audio,source=src.path,
                width=prepared.width,height=prepared.height,folder=folder,target=target,backend=backend,ffmpeg=ffmpeg,
                container=container,alpha=alpha,quality=float(value('Quality')),bitrate=int(value('Bitrate')),
                lossless=bool(value('Lossless')),mode=mode,timed=bool(value('Timed')),
                limit=max(1,int(math.ceil(float(value('Seconds'))*plan['fps']))),
                audio_plan=audio_offline,audio_chans=int(audio.numChans) if audio else 0)

def configure(cfg):
    w=C.op('writer');w.par.record=False;w.par.pause=True;w.par.limitlength=False
    w.par.fps=cfg['plan']['fps'];w.par.quality=cfg['quality'];w.par.uniquesuff=False;w.par.stallforopen=True
    w.par.audiochop=cfg['audio'] if cfg['audio'] and cfg['mode']=='record' else '';w.par.audiocodec='mp3' if cfg['container']=='mp4' and cfg['backend']=='native' else 'pcm16'
    w.par.format='useinput';w.par.outputcolorspace='srgb';w.par.n=cfg['plan']['start'] if cfg['mode']=='render' else 0
    w.par.leadingzerosdigits=6;w.par.maxthread=1;w.par.preset='lossless' if cfg['lossless'] and cfg['backend']=='native' else 'none'
    w.par.avgbitrate=cfg['bitrate'];w.par.peakbitrate=max(cfg['bitrate'],int(cfg['bitrate']*1.5))
    if cfg['kind']=='sequence':
        cfg['target'].mkdir(exist_ok=False);w.par.type='imagesequence';w.par.imagefiletype=cfg['image']
        w.par.file.expr=repr(str(cfg['target']/core().basename(value('Filename'))))+' + me.fileSuffix'
    else:
        fd=os.open(str(cfg['target']),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o644);os.close(fd)
        if cfg['backend']=='ffmpeg':encoder().setup_capture(cfg,w)
        else:
            spec=catalog().CODECS[cfg['codec']]
            w.par.type='movie';w.par.videocodec=cfg['codec_actual'];w.par.moviecontainer='automatic' if cfg['container']=='gif' else cfg['container']
            if spec['tdtype']:
                types=list(w.par.videocodectype.menuNames or [])
                if spec['tdtype'] not in types:raise core().ExportError('当前TD缺少所选编码子类型 '+spec['tdtype'])
                w.par.videocodectype=spec['tdtype']
            pix=getattr(w.par,'videopixelformat',None) or getattr(w.par,'moviepixelformat',None);available=list(pix.menuNames or [])
            if cfg['alpha']:
                fmt=next((x for x in available if 'rgba' in x or 'yuva' in x),None)
                if not fmt:raise core().ExportError('此原生编码配置没有Alpha像素格式；可改FFmpeg后端或ProRes4444')
                pix.val=fmt
            elif available:pix.val=available[0]
            w.par.file.expr='';w.par.file=str(cfg['target'])
    if cfg['mode']=='record':
        w.par.pause=False
        if cfg['timed']:w.par.limitlength=True;w.par.lengthunit='frames';w.par.length=cfg['limit']
    w.cook(force=True)
    if w.errors():raise core().ExportError(w.errors())

def start(mode=None):
    global S,TOKEN
    if busy():return
    mode=mode or value('Mode')
    saved=None;claimed=False
    try:
        holder=root.fetch(LOCK_KEY,None)
        if holder and holder.get('id')!=C.id:
            raise core().ExportError('另一个 Render Studio 正在导出，请先停止它')
        sources().live_sync()
        cfg=settings(mode)
        root.store(LOCK_KEY,{'id':C.id,'path':C.path});claimed=True
        saved=snapshot_time();TOKEN+=1
        S=dict(cfg=cfg,saved=saved,token=TOKEN,done=0,next=cfg['plan']['warm_start'],
               start_clock=time.monotonic(),stage='warmup' if mode=='render' else 'record',cancel=False,opened=False,
               owner_id=C.id,adapter_restore=deterministic().restore,stop_encoder=encoder().cancel,encoder_stopped=encoder().stopped,flush_ticks=0,error=None,last_written=0,last_progress=time.monotonic(),file_path='')
        C.par.Busy=True;C.par.Progress=0;C.par.Frames=0;C.par.Dropped=0;C.par.Outputpath=str(cfg['target'])
        C.par.Elapsed='00:00:00';C.par.Eta='—'
        C.op('ui/menu_overlay').par.display=False
        configure(cfg)
        project.cookRate=cfg['plan']['fps']
        if mode=='render':
            root.time.play=False;project.realTime=False
            root.time.start=min(root.time.start,cfg['plan']['warm_start'])
            root.time.end=max(root.time.end,cfg['plan']['end'])
            root.time.rangeStart=min(root.time.rangeStart,cfg['plan']['warm_start'])
            root.time.rangeEnd=max(root.time.rangeEnd,cfg['plan']['end'])
            root.time.frame=cfg['plan']['warm_start']
            deterministic().begin(cfg)
            status('准备逐帧渲染；结束后自动恢复时间线','渲染中')
        else:
            project.realTime=True;root.time.play=True
            C.op('writer').par.record=True;S['opened']=True
            status('实时录制中；停止将保留已录制内容','录制中')
        refresh_ui();note('开始 '+mode+' → '+str(cfg['target']))
        independent_run(tick,TOKEN)
    except Exception as exc:
        if S:abort(str(exc))
        else:
            if saved:restore_time(saved)
            if claimed:root.unstore(LOCK_KEY)
            status(str(exc),'检查未通过');note(str(exc));refresh_ui()

def read_info():
    info=C.op('writer_info');info.cook(force=True)
    return {a.name:float(a[0]) for a in info.chans()}

def tick(token):
    global S
    if not S or token!=S['token']:return
    try:
        if not C.valid:
            if not S.get('deleted_cleanup'):
                S['deleted_cleanup']=True;S['stop_encoder'](S['cfg'])
            if not S['encoder_stopped'](S['cfg']):independent_run(tick,token,frames=2);return
            S['adapter_restore']();restore_time(S['saved']);root.unstore(LOCK_KEY);S=None;return
        w=C.op('writer');cfg=S['cfg'];p=cfg['plan']
        if S['stage']=='encode_stop':
            if not encoder().stopped(cfg):independent_run(tick,token,frames=2);return
            S['error']=None;S['stage']='flush';cfg['encoding_cancelled']=True;return finalize()
        if S['stage']=='encode':
            if S['cancel']:
                encoder().cancel(cfg);S['stage']='encode_stop';independent_run(tick,token,frames=2);return
            if encoder().finish(cfg):
                cfg['encoded_done']=True;S['stage']='flush';return finalize()
            count=encoder().progress(cfg);C.par.Progress=min(.99,.8+.2*count/max(1,S['done']))
            status(f'正在编码 {cfg["codec"].upper()} · {count}/{S["done"]} 帧','编码中');refresh_ui(light=True);independent_run(tick,token,frames=3);return
        if S['stage']=='restore':
            restore_time(S['saved']);complete(S['final_message'],S['final_state']);return
        if S['stage']=='closing':
            w.par.record=False;w.cook(force=True);S['stage']='flush'
            independent_run(tick,token,frames=2);return
        if S['stage']=='flush':return finalize()
        if S['cancel']:return begin_finish(cancelled=True)
        if cfg['mode']=='render':
            f=S['next'];root.time.frame=f
            deterministic().step(f,p['fps'])
            src=C.op(cfg['source']) or op(cfg['source'])
            if not src:raise core().ExportError('渲染途中图像源被删除，已中止并恢复时间线')
            src.cook(force=True);C.op('prepared').cook(force=True)
            if f<p['start']:
                status(f'预热 {f-p["warm_start"]+1} / {p["start"]-p["warm_start"]} 帧','预热中')
                S['next']+=1;independent_run(tick,token);return
            if not S['opened']:w.par.record=True;S['opened']=True
            w.par.addframe.pulse();w.cook(force=True)
            S['done']+=1;S['next']+=1
        else:
            C.op('prepared').cook(force=True);w.cook(force=True)
        if w.errors():raise core().ExportError('编码器错误：'+w.errors())
        inf=read_info();written=int(inf.get('total_frames_written',0))
        if cfg['mode']=='render' and written!=S['done']:
            raise core().ExportError(f'编码帧数异常：请求 {S["done"]} / 编码器 {written}，已停止以免错帧')
        S['done']=written
        C.par.Frames=written;C.par.Dropped=int(inf.get('total_frames_dropped',0))
        if C.par.Dropped.eval() and cfg['mode']=='render':raise core().ExportError('离线编码出现丢帧，已停止')
        limit=p['count'] if cfg['mode']=='render' else (cfg['limit'] if cfg['timed'] else 0)
        C.par.Progress=(.8 if cfg['backend']=='ffmpeg' else 1)*min(1,written/limit) if limit else 0
        elapsed=time.monotonic()-S['start_clock'];C.par.Elapsed=core().format_duration(elapsed)
        C.par.Eta=core().format_duration((limit-written)*elapsed/written) if limit and written else '—'
        status((f'{written} / {limit} 帧' if limit else f'{written} 帧')+f'  ·  视频 {written/p["fps"]:.2f} 秒', '渲染中' if cfg['mode']=='render' else '录制中')
        if written!=S['last_written']:S['last_written']=written;S['last_progress']=time.monotonic()
        elif time.monotonic()-S['last_progress']>15:raise core().ExportError('编码器 15 秒没有写入新帧，已停止；请检查输入与编码器')
        if time.monotonic()-S.get('ui_clock',0)>.05:
            refresh_ui(light=True);S['ui_clock']=time.monotonic()
        if limit and written>=limit:return begin_finish()
        independent_run(tick,token)
    except Exception as exc:abort(str(exc))

def begin_finish(cancelled=False,error=None):
    if not S:return
    w=C.op('writer');w.par.pause=True
    # Leave Record on until the next independent frame: GPU readback of the last frame is asynchronous.
    S['cancel']=cancelled;S['error']=error;S['stage']='closing';S['finish_clock']=time.monotonic()
    status('正在关闭文件并恢复时间线…','收尾中')
    independent_run(tick,S['token'],frames=2)

def abort(message):
    if S:
        if S['stage'] in ('closing','flush','restore','encode','encode_stop'):
            if S['stage'] in ('encode','encode_stop'):encoder().cancel(S['cfg'])
            try:restore_time(S['saved'])
            finally:complete(message,'失败')
            return
        try:begin_finish(error=message)
        except Exception:
            try:restore_time(S['saved'])
            finally:complete(message,'失败')
    else:status(message,'失败')

def finalize():
    cfg=S['cfg'];target=cfg['target'];info=read_info()
    if info.get('active_records',0)>0:
        if time.monotonic()-S['finish_clock']>20:raise core().ExportError('等待写盘超时，请保留部分文件并检查磁盘')
        independent_run(tick,S['token'],frames=2);return
    done=S['done'];error=S['error'];cancelled=S['cancel']
    if not error and not cancelled and cfg['audio'] and cfg['mode']=='render' and done and not cfg.get('wav_ready'):
        if not cfg.get('workdir'):cfg['workdir']=Path(encoder().tempfile_dir(cfg))
        cfg['audio_wav']=cfg['workdir']/'audio.wav'
        try:
            encoder().synth_wav(cfg);cfg['wav_ready']=True
        except Exception as exc:error='离线音频合成失败：'+str(exc)
    if cfg['backend']=='native' and cfg['audio'] and cfg['mode']=='render' and not error and not cancelled and (not target.exists() or target.stat().st_size<32):
        error='输出文件为空或缺失，请检查编码器 / 写入权限'
    if cfg['backend']=='ffmpeg' and not cfg.get('encoded_done') and not error and not cancelled:
        deterministic().restore();restore_time(S['saved'])
        encoder().start(cfg);S['stage']='encode';status('画面采集完成，正在本地编码…','编码中');independent_run(tick,S['token'],frames=3);return
    if cfg['backend']=='native' and not cfg.get('encoded_done') and not error and not cancelled and cfg['audio'] and cfg['mode']=='render':
        deterministic().restore();restore_time(S['saved'])
        encoder().mux_native(cfg);S['stage']='encode';status('画面完成，正在合成音轨…','编码中');independent_run(tick,S['token'],frames=3);return
    if not error and done:
        if cfg['kind']=='sequence':
            files=list(target.glob('*'+core().IMAGES[cfg['image']]))
            if len(files)!=done or any(x.stat().st_size==0 for x in files):error=f'写盘核验不符：期望 {done} 张，请检查序列目录'
        elif not cancelled and (not target.exists() or target.stat().st_size<32):error='输出文件为空或缺失，请检查编码器 / 写入权限'
    deterministic().restore();restore_time(S['saved'])
    if error:state='失败';message=error+'；时间线已恢复，部分文件保留'
    elif cancelled:state='已停止' if cfg['mode']=='record' else '已取消';message=f'已保留 {done} 帧；时间线已恢复'
    else:state='完成';message=f'完成 {done} 帧 · {done/cfg["plan"]["fps"]:.2f} 秒；时间线已恢复'
    if cfg['backend']=='ffmpeg' and cancelled:
        message+='；中间素材已保留'
        if cfg.get('workdir') and cfg['workdir'].exists():C.par.Outputpath=str(cfg['workdir'])
        if target.exists() and target.stat().st_size==0:target.unlink()
    if cfg['backend']=='native' and cancelled and cfg['mode']=='render' and cfg.get('audio') and cfg.get('audio_wav'):
        message+='；视频成片完整，音轨未合成'
    if not error and not cancelled:C.par.Progress=1
    # A portable task manifest accompanies output, never embeds the project source or audio data.
    audio_info=None
    if cfg['audio'] and cfg['mode']=='render' and cfg.get('audio_plan'):
        ap=cfg['audio_plan']
        audio_info=dict(channels=cfg.get('audio_chans'),rate=ap['rate'],offset_samples=ap['offset'],samples=ap['count'],padded_samples=ap['pad'],codec=catalog().CONTAINERS[cfg['container']]['audio'] if cfg['kind']=='movie' else None)
    manifest=dict(version=core().VERSION,result=state,frames=done,fps=cfg['plan']['fps'],
                  start=cfg['plan']['start'] if cfg['mode']=='render' else None,
                  end=cfg['plan']['end'] if cfg['mode']=='render' else None,width=cfg['width'],height=cfg['height'],
                  capture_precision='EXR16' if cfg.get('capture_high') else 'native_or_8bit',encode_ms=cfg.get('encode_ms'),mode=cfg['mode'],container=cfg.get('container'),backend=cfg.get('backend'),repeatable=bool(value('Repeatable')),reset_frame=value('Resetframe'),render_seed=value('Renderseed'),codec=cfg['codec'] if cfg['kind']=='movie' else cfg['image'],audio=audio_info,error=error)
    try:
        meta=(target/'render_manifest.json') if cfg['kind']=='sequence' else target.with_suffix(target.suffix+'.json')
        # Exclusive metadata creation, also never overwrites a previous user file.
        with meta.open('x',encoding='utf-8') as f:json.dump(manifest,f,ensure_ascii=False,indent=2)
    except OSError as exc:message+='；日志未写入：'+str(exc)
    S['final_message']=message;S['final_state']=state;S['stage']='restore'
    independent_run(tick,S['token'],frames=1)

def complete(message,state):
    global S
    deterministic().restore();S=None;root.unstore(LOCK_KEY)
    if not C.valid:return
    C.par.Busy=False;C.par.Eta='00:00:00' if state=='完成' else '—';status(message,state);note(message);refresh_ui()

def cancel():
    if not S:return
    # Terminate an active child immediately on the UI action, rather than waiting for the next progress poll.
    if S['stage']=='encode':
        cfg=S['cfg'];code=cfg['process'].poll()
        if code is not None:
            try:
                encoder().finish(cfg);cfg['encoded_done']=True;S['cancel']=False;S['stage']='flush';finalize()
            except Exception as exc:abort(str(exc))
            return
        encoder().cancel(cfg);S['stage']='encode_stop'
        independent_run(tick,S['token'],frames=1)
    S['cancel']=True;status('正在停止；已写入文件不会删除','正在停止')

def check():
    if busy():return
    try:
        cfg=settings(value('Mode'))
        if cfg['mode']=='render':
            detail=f'{cfg["plan"]["count"]} 帧 · {cfg["plan"]["seconds"]:.2f} 秒'
            if cfg.get('audio_plan'):
                ap=cfg['audio_plan'];detail+=f' · 音频 {ap["rate"]}Hz，同步 {ap["take"]:,} 样本'+('（尾部补静音）' if ap['pad'] else '')
        else:detail=(f'定时 {cfg["limit"]} 帧 / {cfg["limit"]/cfg["plan"]["fps"]:.2f} 秒' if cfg['timed'] else '实时录制 · 手动停止')
        status(f'检查通过 · {cfg["width"]} × {cfg["height"]} · '+detail,'就绪')
        C.par.Outputpath=str(cfg['target'])
    except Exception as exc:status(str(exc),'检查未通过')
    refresh_ui()

def choose_folder():
    if busy():return
    try:start=str(core().resolve_folder(value('Folder'),str(project.folder)))
    except Exception:start=str(project.folder)
    try:
        path=ui.chooseFolder(title='选择导出文件夹',start=start)
        if path:C.par.Folder=path;refresh_ui()
        show_panel()
    except Exception as exc:status('目录选择失败：'+str(exc),'提示');refresh_ui()

def open_folder():
    try:
        path=core().resolve_folder(value('Folder'),str(project.folder))
        if not path.is_dir():raise core().ExportError('目录尚未创建；先导出或手动创建目录')
        ui.viewFile(str(path))
    except Exception as exc:status(str(exc),'提示');refresh_ui()

def snapshot():
    if busy():return
    try:
        src,prepared=resolve_source();k=core();folder=k.resolve_folder(value('Folder'),str(project.folder))
        if not folder.exists() and not value('Createfolder'):raise k.ExportError('目录不存在')
        folder.mkdir(parents=True,exist_ok=True)
        image=value('Snapshotformat');suffix=k.IMAGES[image]
        dest=k.target_path(folder,k.basename(value('Filename'))+'_snapshot',suffix,False,value('Conflict'))
        with dest.open('xb'):pass
        # TOP.save is synchronous by default. Do not toggle an asynchronous image writer off in the same cook.
        prepared.save(str(dest),asynchronous=False,quality=float(value('Quality')))
        if not dest.exists() or not dest.stat().st_size:raise k.ExportError('快照文件没有写入成功')
        C.par.Frames=1;C.par.Progress=1;C.par.Elapsed='00:00:00';C.par.Eta='—'
        C.par.Outputpath=str(dest);status('快照已保存 · '+dest.name,'完成');note('快照 '+str(dest))
    except Exception as exc:status(str(exc),'快照失败')
    refresh_ui()

def use_range():
    if busy():return
    C.par.Start=int(root.time.rangeStart);C.par.End=int(root.time.rangeEnd);C.par.Fps=project.cookRate;refresh_ui()

def show_panel():C.op('ui').openViewer()

def advanced():C.openParameters()

def changed(name):
    if sources().UPDATING:return
    if name=='Container':
        previous=value('Codec');available=catalog().choices(value('Container'))
        C.par.Codec.menuNames=available;C.par.Codec.menuLabels=[catalog().CODECS[x]['label'] for x in available]
        C.par.Codec=previous if previous in available else available[0]
    if name=='Menusearch':
        C.op('chooser').module.render(reset_page=True);return
    if name=='Ffmpeg':encoder().capabilities()
    sources().changed(name)
    refresh_ui()

def field_commit(comp,text):
    if SYNCING or busy():return
    name=comp.fetch('parameter',None)
    if not name:return
    try:
        p=C.par[name]
        if p.isInt:text=core().integer(text,p.label)
        elif p.isFloat:
            text=float(text)
            if not math.isfinite(text):raise core().ExportError('数字必须有限')
        p.val=text;changed(name)
    except Exception as exc:status('输入无效：'+str(exc),'检查未通过');refresh_ui()

def action(name):
    actions={'Start':start,'Cancel':cancel,'Check':check,'Browse':choose_folder,'Folder':open_folder,
             'Snapshot':snapshot,'Range':use_range,'Advanced':advanced,'Openpanel':show_panel,
             'Help':lambda: C.op('help').openViewer(), 'Closemenu':close_menu,
             'Menuprev':lambda:C.op('chooser').module.page(-1),'Menunext':lambda:C.op('chooser').module.page(1),
             'Scanencoders':encoder().capabilities,
             'Fast':lambda:setattr(C.par,'Encodespeed','fast'),'Balanced':lambda:setattr(C.par,'Encodespeed','balanced'),'Qualitymode':lambda:setattr(C.par,'Encodespeed','quality'),
             'Timed':lambda: setattr(C.par,'Timed',not value('Timed')),
             'Masterres':lambda: setattr(C.par,'Masterres',not value('Masterres')),
             'Repeatable':lambda: setattr(C.par,'Repeatable',not value('Repeatable')),
             'Release':sources().release_action,
             'Preset1080':lambda: apply_size(1920,1080),'Preset720':lambda: apply_size(1280,720),'Preset4k':lambda: apply_size(3840,2160),
             'Alpha':lambda: setattr(C.par,'Alpha',not value('Alpha'))}
    if name.startswith('Menu:'):return show_menu(name.split(':',1)[1])
    if name.startswith('Pick:'):
        _,par,selection=name.split(':',2)
        if not busy():C.par[par]=selection;changed(par)
        close_menu();refresh_ui();return
    if name in actions:
        actions[name]();refresh_ui()

def apply_size(w,h):
    if busy():return
    C.par.Width=w;C.par.Height=h;C.par.Size='custom';sources().changed('Width')

def close_menu():C.op('ui/menu_overlay').par.display=False

def show_menu(par):
    if not busy():C.op('chooser').module.show(par)

def refresh_ui(light=False):
    global SYNCING
    if not C.valid or not C.op('ui'):return
    SYNCING=True
    try:
        u=C.op('ui')
        if not light:
            for o in u.findChildren(type=textCOMP):
                name=o.fetch('parameter',None)
                if name:
                    p=C.par[name]
                    txt=str(p.eval())
                    if name in ('Source','Audio'):txt=str(p.val)
                    if p.isInt:txt=str(int(p.eval()))
                    elif p.isFloat:txt=f'{p.eval():g}'
                    if o.par.text.eval()!=txt:o.par.text=txt
            for name in ('Codec','Kind','Imageformat','Mode','Container','Encodespeed'):
                o=u.op('choice_'+name.lower())
                if o:
                    p=C.par[name];o.op('caption').par.text=('速度：' if name=='Encodespeed' else '')+p.menuLabels[p.menuIndex]+'  ▾'
            mode=value('Mode')
            isrender=mode=='render'
            for n in ('field_start','field_end','field_warmup','label_start','label_end','label_warmup','use_range','alpha'):
                if u.op(n):u.op(n).par.display=isrender
            for n in ('field_seconds','label_seconds','timed','label_timed'):
                if u.op(n):u.op(n).par.display=not isrender
            for n in ('field_audio','label_audio'):
                o=u.op(n)
                if o:o.par.display=True;o.par.x=492 if isrender else 392;o.par.w=140 if isrender else 240
            u.op('range_title').par.text='03  帧范围 / 统一起点' if isrender else '03  录制控制'
            if u.op('use_range'):u.op('use_range').par.display=False
            if u.op('timed'):u.op('timed/caption').par.text='定时停止：'+('开启' if value('Timed') else '关闭')
            if u.op('alpha'):
                u.op('alpha/caption').par.text='Alpha：自带' if catalog().CODECS[value('Codec')]['force_alpha'] and value('Kind')=='movie' else 'Alpha：'+('保留' if value('Alpha') else '关闭')
            u.op('start/caption').par.text='开始渲染' if mode=='render' else '开始录制'
            u.op('mode_note').par.text='逐帧推进 · 不丢帧 · 音频离线合成 · 导出后恢复时间线' if mode=='render' else '实时捕获 · 支持音频 · 慢帧可能重复画面'
            if u.op('master/caption'):u.op('master/caption').par.text='接管上游：'+('开启' if value('Masterres') else '关闭')
            if u.op('repeatable/caption'):u.op('repeatable/caption').par.text='相同起点：'+('开启' if value('Repeatable') else '关闭')
            if u.op('managed_info'):u.op('managed_info').par.text=value('Managedinfo')
            if u.op('determinism_info'):u.op('determinism_info').par.text=value('Determinism')
            if u.op('backend_info'):
                try:
                    backend=catalog().select_backend(value('Codec'),value('Container'),value('Backend'))
                    label=('VideoToolbox · 硬件编码' if value('Codec').endswith('vt') else 'FFmpeg · 本地编码') if backend=='ffmpeg' else 'TouchDesigner · 原生编码'
                except Exception:label='后端与当前选项不兼容，请检查设置'
                u.op('backend_info').par.text=label
            if u.op('safe_note'):u.op('safe_note').par.text=value('Capabilities')
            if u.op('speed_label'):u.op('speed_label').par.text='编码速度：'+{'fast':'快速','balanced':'平衡','quality':'质量优先'}[value('Encodespeed')]
            if u.op('choice_container'):u.op('choice_container').par.display=value('Kind')=='movie'
            u.op('choice_codec').par.display=value('Kind')=='movie';u.op('choice_imageformat').par.display=value('Kind')=='sequence'
            try:
                p=core().frame_plan(value('Start'),value('End'),value('Fps'),value('Warmup'))
                u.op('range_summary').par.text=f'{p["count"]:,} 帧  /  {p["seconds"]:.2f} 秒   ·   首尾均包含'
            except Exception:u.op('range_summary').par.text='请修正帧范围或帧率'
            if mode=='record':u.op('range_summary').par.text=(f'定时 {value("Seconds"):g} 秒 · 到时自动结束' if value('Timed') else '手动停止 · 已写入内容保留')
        u.op('state_label').par.text=value('State');u.op('message').par.text=value('Message')
        u.op('elapsed').par.text='已用 '+value('Elapsed')+'   /   预计剩余 '+value('Eta')
        u.op('progress_text').par.text=f'{value("Progress")*100:.0f}%  ·  {int(value("Frames")):,} 帧'
        u.op('path_result').par.text=value('Outputpath') or '导出前可点击“检查设置”查看最终路径'
        if C.op('prepared').width>0:u.op('source_info').par.text=f'{C.op("prepared").width} × {C.op("prepared").height}   ·   {float(value("Fps")):g} FPS'
    finally:SYNCING=False

def initialize():
    global S,TOKEN
    S=None;TOKEN+=1
    holder=root.fetch(LOCK_KEY,None)
    if holder and holder.get('path')==C.path:root.unstore(LOCK_KEY)
    for name in ('writer','snapshot_writer'):
        w=C.op(name)
        if w:w.par.record=False
    if C.par.Busy:
        C.par.Busy=False;C.par.Progress=0;C.par.Frames=0;C.par.Outputpath=''
        status('连接 TOP → 选择目录 → 检查设置 → 开始渲染','就绪')
    refresh_ui()
    sources().start_watch()
    run(encoder().capabilities,delayFrames=3,delayRef=op.TDResources)
