"""Local encoder discovery and compatible FFmpeg jobs; all invocations use argument lists."""
from pathlib import Path
import subprocess,shutil,os,time,re
C=me.parent()
CACHE={}

def catalog():return C.op('catalog').module

def executable():
    chosen=str(C.par.Ffmpeg.eval()).strip()
    candidates=[chosen] if chosen else [shutil.which('ffmpeg'),'/opt/homebrew/bin/ffmpeg','/usr/local/bin/ffmpeg']
    for item in candidates:
        if item and Path(item).expanduser().is_file():return str(Path(item).expanduser())
    raise ValueError('未找到FFmpeg；请在高级页指定可执行文件，或选TD原生编码器')

def probe():
    path=executable();key=(path,Path(path).stat().st_mtime_ns)
    if key not in CACHE:
        p=subprocess.run([path,'-hide_banner','-encoders'],capture_output=True,text=True,timeout=10)
        if p.returncode:raise ValueError('FFmpeg能力检测失败：'+p.stderr[-300:])
        names=set(re.findall(r'^\s*[VAS][A-Z.]{5}\s+(\S+)',p.stdout,re.M))
        CACHE[key]=names
    return path,CACHE[key]

def validate(codec,audio=False,container=None):
    path,names=probe();spec=catalog().CODECS[codec]
    if not spec['encoder'] or spec['encoder'] not in names:raise ValueError('当前FFmpeg没有 '+str(spec['encoder'])+'；请换编码器或后端')
    ac=catalog().CONTAINERS[container]['audio'] if container else None
    if audio and (not ac or ac not in names):raise ValueError('当前容器/FFmpeg缺少所需音频编码器 '+str(ac))
    return path

def validate_audio(container):
    """Native-backend offline audio only needs FFmpeg's audio encoder for the final mux."""
    path,names=probe();ac=catalog().CONTAINERS[container]['audio']
    if not ac:raise ValueError('此容器不支持音频轨道')
    if ac not in names:raise ValueError('当前FFmpeg缺少所需音频编码器 '+str(ac)+'；离线合成音频需要本机FFmpeg')
    return path

def core():return C.op('export_core').module

def synth_wav(cfg):
    """Write the offline audio track as a 16-bit PCM WAV from a full-length CHOP.
    Sample mapping and padding follow export_core.audio_plan; rate stays at source rate."""
    import numpy as np,wave
    src=cfg['audio']
    if not src or not src.valid or not src.isCHOP:raise ValueError('音频源已失效，无法离线合成')
    src.cook(force=True)
    if src.isTimeSlice:raise ValueError('音频源是时间切片，无法离线合成；请用含完整数据的CHOP')
    chans=int(src.numChans)
    if chans not in (1,2):raise ValueError('音频须为1或2声道CHOP')
    ap=core().audio_plan(cfg['plan']['start'],cfg['plan']['end'],cfg['plan']['fps'],src.rate,src.numSamples)
    data=src.numpyArray()
    if data is None or data.size==0:raise ValueError('音频源没有可读取的样本数据')
    data=np.asarray(data,dtype='<f4')
    if data.ndim==1:data=data.reshape(1,-1)
    if data.shape[0]!=chans and data.shape[1]==chans:data=data.T
    out=np.zeros((ap['count'],chans),dtype='<f4')
    if ap['take']:out[:ap['take']]=data[:,ap['offset']:ap['offset']+ap['take']].T
    pcm=(np.clip(out,-1.0,1.0)*32767).astype('<i2')
    with wave.open(str(cfg['audio_wav']),'wb') as w:
        w.setnchannels(chans);w.setsampwidth(2);w.setframerate(ap['rate']);w.writeframes(pcm.tobytes())
    cfg['audio_plan']=ap
    return cfg['audio_wav']

def capabilities():
    registry=catalog();native=set(C.op('writer').par.videocodec.menuNames or []);external=set();reason=''
    try:path,external=probe()
    except Exception as exc:reason=str(exc)
    rows=[]
    for key,s in registry.CODECS.items():
        nat=s['td'] in native if s['td'] else False
        if key in ('h264','h265') and 'non-commercial' in root.licenseType.lower():nat=False
        ext=s['encoder'] in external if s['encoder'] else False
        rows.append([key,s['label'],'可用' if nat or ext else '不可用', 'TD' if nat else '',s['encoder'] if ext else '', ' '.join(s['containers'])])
    d=C.op('encoder_capabilities');d.clear();d.appendRow(['id','label','status','native','ffmpeg','containers'])
    for row in rows:d.appendRow(row)
    C.par.Capabilities=f'{len(registry.CONTAINERS)}种容器 / {sum(x[2]=="可用" for x in rows)}项本机可用编码配置'+(' · '+reason if reason else '')
    return rows

def setup_capture(cfg,w):
    work=Path(tempfile_dir(cfg));cfg['workdir']=work
    spec=catalog().CODECS[cfg['codec']]
    high=C.par.Precision.eval()=='high' or (C.par.Precision.eval()=='auto' and spec['depth']>8)
    cfg['capture_high']=high
    if high:
        cfg['intermediate']=work;cfg['input_pattern']=str(work/'frame.0.%06d.exr')
        w.par.type='imagesequence';w.par.imagefiletype='exr';w.par.n=0;w.par.leadingzerosdigits=6;w.par.maxthread=1
        w.par.file.expr=repr(str(work/'frame'))+' + me.fileSuffix';w.par.format='rgba16float';w.par.outputcolorspace='passthrough'
    else:
        cfg['intermediate']=work/'capture.mov';w.par.type='movie';w.par.videocodec='rle';w.par.moviecontainer='mov'
        w.par.videopixelformat='rgba' if cfg['alpha'] else 'rgb';w.par.file.expr='';w.par.file=str(cfg['intermediate']);w.par.format='useinput';w.par.outputcolorspace='srgb';w.par.audiocodec='pcm16'

def tempfile_dir(cfg):
    import tempfile
    return tempfile.mkdtemp(prefix='.'+cfg['target'].stem+'_rs_',dir=str(cfg['folder']))

def start(cfg):
    work=cfg['workdir'];result=work/('encoded'+cfg['target'].suffix);cfg['encode_log']=work/'ffmpeg.log'
    offline_audio=cfg['audio'] and cfg['mode']=='render'
    args=[cfg['ffmpeg'],'-hide_banner','-nostdin','-n']
    if cfg['capture_high']:args+=['-framerate',str(cfg['plan']['fps']),'-start_number','0','-i',cfg['input_pattern']]
    else:args+=['-i',str(cfg['intermediate'])]
    if offline_audio:args+=['-i',str(cfg['audio_wav'])]
    args+=['-map','0:v:0']
    if cfg['audio']:args+=['-map','1:a:0' if offline_audio else '0:a:0']
    else:args+=['-an']
    args+=catalog().ffmpeg_options(cfg['codec'],quality=int(C.par.Crf),speed=C.par.Encodespeed.eval(),bitrate=cfg['bitrate'],alpha=cfg['alpha'],lossless=cfg['lossless'],container=cfg['container'])
    if cfg['audio']:
        ac=catalog().CONTAINERS[cfg['container']]['audio'];args+=['-c:a',ac]
        if ac in ('aac','libopus','wmav2','mp2'):args+=['-b:a','192k']
        if cfg['container']=='mxf':args+=['-ar','48000']
    if cfg['container'] in ('mp4','mov'):
        args+=['-movflags','+faststart']
        if cfg['codec'] in ('h265','h265vt','hevc10'):args+=['-tag:v','hvc1']
    args+=['-threads','4','-progress',str(work/'progress.txt'),'-f',catalog().CONTAINERS[cfg['container']]['mux'],str(result)]
    log=cfg['encode_log'].open('w',encoding='utf-8')
    try:proc=subprocess.Popen(args,stdout=log,stderr=log)
    finally:log.close()
    cfg['encoded']=result;cfg['process']=proc;cfg['encode_started']=time.monotonic();cfg['ffmpeg_arguments']=args
    return proc

def progress(cfg):
    p=cfg['workdir']/'progress.txt'
    if not p.exists():return 0
    try:return int(dict(line.split('=',1) for line in p.read_text(errors='replace').splitlines() if '=' in line).get('frame','0'))
    except ValueError:return 0

def mux_native(cfg):
    """Mux the natively encoded video (stream copy) with the offline WAV; no re-encode."""
    work=cfg.get('workdir') or Path(tempfile_dir(cfg));cfg['workdir']=work
    result=work/('muxed'+cfg['target'].suffix);cfg['encode_log']=work/'ffmpeg.log'
    ac=catalog().CONTAINERS[cfg['container']]['audio']
    args=[cfg['ffmpeg'],'-hide_banner','-nostdin','-n','-i',str(cfg['target']),'-i',str(cfg['audio_wav']),
          '-map','0:v:0','-c:v','copy','-map','1:a:0','-c:a',ac]
    if ac in ('aac','libopus','wmav2','mp2'):args+=['-b:a','192k']
    if cfg['container'] in ('mp4','mov'):args+=['-movflags','+faststart']
    if cfg['codec'] in ('h265','h265vt','hevc10'):args+=['-tag:v','hvc1']
    args+=['-progress',str(work/'progress.txt'),'-f',catalog().CONTAINERS[cfg['container']]['mux'],str(result)]
    log=cfg['encode_log'].open('w',encoding='utf-8')
    try:proc=subprocess.Popen(args,stdout=log,stderr=log)
    finally:log.close()
    cfg['encoded']=result;cfg['process']=proc;cfg['mux_inplace']=True;cfg['encode_started']=time.monotonic();cfg['ffmpeg_arguments']=args
    return proc

def finish(cfg):
    code=cfg['process'].poll()
    if code is None:return False
    cfg['encode_ms']=(time.monotonic()-cfg['encode_started'])*1000
    if code:raise ValueError('FFmpeg编码失败：'+cfg['encode_log'].read_text(errors='replace')[-1000:])
    output=cfg['encoded']
    if not output.exists() or output.stat().st_size<32:raise ValueError('编码器没有生成有效文件；中间素材保留')
    if not cfg.get('mux_inplace') and cfg['target'].stat().st_size!=0:raise ValueError('目标已被其它进程修改，不覆盖；编码结果保留在缓存')
    os.replace(output,cfg['target'])
    if not C.par.Keepcache.eval():shutil.rmtree(cfg['workdir'])
    return True

def cancel(cfg):
    proc=cfg.get('process')
    if proc and proc.poll() is None:proc.terminate();cfg['cancel_started']=time.monotonic()

def stopped(cfg):
    proc=cfg.get('process')
    if not proc or proc.poll() is not None:return True
    if time.monotonic()-cfg.get('cancel_started',time.monotonic())>2:proc.kill()
    return False
