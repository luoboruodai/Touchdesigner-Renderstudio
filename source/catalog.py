"""Format/codec registry. Profiles are explicit; compatibility is not guessed from extensions."""
CONTAINERS={
 'mp4':{'label':'MP4 · 通用 / 网络','ext':'.mp4','mux':'mp4','audio':'aac'},
 'mov':{'label':'MOV · QuickTime / 后期','ext':'.mov','mux':'mov','audio':'pcm_s16le'},
 'mkv':{'label':'MKV · 多编码 / 归档','ext':'.mkv','mux':'matroska','audio':'flac'},
 'webm':{'label':'WebM · 网页视频','ext':'.webm','mux':'webm','audio':'libopus'},
 'avi':{'label':'AVI · 传统 / 无损','ext':'.avi','mux':'avi','audio':'pcm_s16le'},
 'mxf':{'label':'MXF · 广播交换','ext':'.mxf','mux':'mxf','audio':'pcm_s16le'},
 'mpg':{'label':'MPEG · MPG 节目流','ext':'.mpg','mux':'mpeg','audio':'mp2'},
 'ts':{'label':'MPEG-TS · 传输流','ext':'.ts','mux':'mpegts','audio':'aac'},
 'flv':{'label':'FLV · 兼容输出','ext':'.flv','mux':'flv','audio':'aac'},
 'wmv':{'label':'WMV / ASF · Windows兼容','ext':'.wmv','mux':'asf','audio':'wmav2'},
 'gif':{'label':'GIF · 动图','ext':'.gif','mux':'gif','audio':None},
}
CODECS={}
def add(key,label,containers,encoder=None,td=None,tdtype=None,pix='yuv420p',alpha_pix=None,depth=8,group='网络',options=(),alpha=False,constraint=None):
 CODECS[key]={'label':label,'containers':containers.split(),'encoder':encoder,'td':td,'tdtype':tdtype,'pix':pix,'alpha_pix':alpha_pix,'depth':depth,'group':group,'options':list(options),'force_alpha':alpha,'constraint':constraint}
add('h264','H.264 / AVC','mp4 mov mkv ts flv','libx264','h264')
add('h264vt','H.264 · VideoToolbox 硬件','mp4 mov mkv ts flv','h264_videotoolbox')
add('h264rgb','H.264 RGB · 4:4:4','mp4 mov mkv','libx264rgb',pix='rgb24')
add('h265','H.265 / HEVC','mp4 mov mkv ts','libx265','h265')
add('h265vt','H.265 · VideoToolbox 硬件','mp4 mov mkv ts','hevc_videotoolbox')
add('hevc10','HEVC Main 10 · 10-bit','mp4 mov mkv ts','libx265',pix='yuv420p10le',depth=10,options=['-profile:v','main10'])
add('av1','AV1 · SVT-AV1','mp4 mkv webm','libsvtav1')
add('vp8','VP8 · WebM','webm mkv','libvpx')
add('vp9','VP9 · WebM','webm mkv','libvpx-vp9')
add('mpeg4','MPEG-4 Part 2','mp4 mov avi mkv','mpeg4','mpeg4',group='兼容')
for key,label,profile in [('prores_proxy','ProRes 422 Proxy',0),('prores_lt','ProRes 422 LT',1),('prores422','ProRes 422',2),('prores','ProRes 422 HQ',3),('prores4444','ProRes 4444 · Alpha',4),('prores_xq','ProRes 4444 XQ · Alpha',5)]:
 tdtype=['prores422proxy','prores422lt','prores422','prores422hq','prores4444','prores4444xq'][profile]
 add(key,label,'mov mkv','prores_ks','prores',tdtype,pix='yuv444p10le' if profile>=4 else 'yuv422p10le',alpha_pix='yuva444p10le' if profile>=4 else None,depth=12 if profile>=4 else 10,group='后期',options=['-profile:v',str(profile)],alpha=profile>=4)
for key,profile,depth,pix in [('dnxhr_lb','dnxhr_lb',8,'yuv422p'),('dnxhr_sq','dnxhr_sq',8,'yuv422p'),('dnxhr_hq','dnxhr_hq',8,'yuv422p'),('dnxhr_hqx','dnxhr_hqx',10,'yuv422p10le'),('dnxhr_444','dnxhr_444',10,'yuv444p10le')]:
 add(key,profile.replace('_',' ').upper(),'mov mkv mxf','dnxhd',pix=pix,depth=depth,group='后期',options=['-profile:v',profile],constraint='dnxhr')
add('cineform','GoPro CineForm · 10/12-bit','mov avi','cfhd','cineform',pix='gbrp12le',alpha_pix='gbrap12le',depth=12,group='后期',options=['-quality','5'])
add('rle','Animation / QuickTime RLE · 无损','mov','qtrle','rle',pix='rgb24',alpha_pix='argb',group='无损')
add('hap','Hap · GPU 播放','mov',td='hap',tdtype='hap',pix='rgb24',alpha_pix='rgba',group='实时')
add('hapq','Hap Q · GPU 播放','mov',td='hap',tdtype='hapq',pix='rgb24',alpha_pix='rgba',group='实时')
add('mjpeg','Motion JPEG / MJPEG','mov avi mkv','mjpeg','mjpa',pix='yuvj422p',group='兼容',options=['-q:v','3'])
add('jpeg2000','JPEG 2000','mov mkv','jpeg2000',pix='yuv444p',group='后期',options=['-pred','1'])
add('ffv1','FFV1 v3 · 无损归档','mkv avi','ffv1',pix='bgr0',alpha_pix='bgra',group='无损',options=['-level','3','-coder','1','-context','1','-slicecrc','1'])
add('ffv1_16','FFV1 · 16-bit 无损','mkv','ffv1',pix='gbrp16le',alpha_pix='gbrap16le',depth=16,group='无损',options=['-level','3','-coder','1','-context','1','-slicecrc','1'])
add('huffyuv','HuffYUV · 无损','avi mkv','huffyuv',pix='rgb24',alpha_pix='bgra',group='无损')
add('utvideo','Ut Video · 无损','avi mkv','utvideo',pix='gbrp',alpha_pix='gbrap',group='无损')
add('v210','Uncompressed 4:2:2 · 10-bit','mov avi','v210',pix='yuv422p10le',depth=10,group='无压缩')
add('rawvideo','Uncompressed RGB / RGBA','mov avi','rawvideo',pix='rgb24',alpha_pix='argb',group='无压缩')
add('mpeg1','MPEG-1 Video','mpg','mpeg1video',group='兼容',constraint='mpeg')
add('mpeg2','MPEG-2 Video','mpg ts mxf','mpeg2video',group='兼容',constraint='mpeg')
add('mpeg2422','MPEG-2 4:2:2 · 50 Mb/s','mxf mov ts','mpeg2video',pix='yuv422p',group='广播',options=['-profile:v','0','-b:v','50M','-minrate','50M','-maxrate','50M','-bufsize','17825792','-flags','+ildct+ilme'],constraint='broadcast')
add('flv1','FLV / Sorenson Spark','flv','flv',group='兼容')
add('wmv2','Windows Media Video 8','wmv avi','wmv2',group='兼容')
add('gif','GIF · 调色板动图','gif','gif','gif',pix='rgb8',group='动图')

def choices(container):return [k for k,v in CODECS.items() if container in v['containers']]
def native_name(key):return CODECS[key]['td']
def select_backend(key,container,preference='auto'):
 s=CODECS[key]
 if preference=='native':
  if not s['td'] or container not in ('mp4','mov','gif'):raise ValueError('此编码器/容器需要FFmpeg后端')
  return 'native'
 if preference=='ffmpeg':
  if not s['encoder']:raise ValueError('本机FFmpeg不提供此编码器，请使用TD原生')
  return 'ffmpeg'
 # H.26x native licence restrictions are preserved; prefer an independent installed encoder.
 return 'native' if s['td'] and key not in ('h264','h265') and container in ('mp4','mov','gif') else 'ffmpeg'

def validate(container,key,w,h,fps,alpha=False):
 if container not in CONTAINERS or key not in CODECS or container not in CODECS[key]['containers']:raise ValueError('视频格式与编码器不兼容')
 s=CODECS[key]
 if alpha and not s['alpha_pix']:raise ValueError('此编码器不保留Alpha；请选MOV ProRes4444/Animation或支持Alpha的无损编码')
 if (s['pix'].startswith('yuv') or key in ('h264','h265','h264vt','h265vt','vp8','vp9','av1')) and (w%2 or h%2):raise ValueError('此编码器要求偶数宽高')
 if s['constraint']=='dnxhr' and (w<256 or h<120):raise ValueError('DNxHR至少需要256×120')
 if s['constraint'] in ('mpeg','broadcast') and not any(abs(fps-f)<.02 for f in (23.976,24,25,29.97,30,50,59.94,60)):raise ValueError('此广播编码器需要标准帧率：23.976/24/25/29.97/30/50/59.94/60')
 if container=='mxf' and (w,h) not in ((1920,1080),(1280,720)) and s['constraint']!='dnxhr':raise ValueError('此MXF预设要求1920×1080或1280×720')

def ffmpeg_options(key,quality=18,speed='balanced',bitrate=20000,alpha=False,lossless=False,container=None):
 s=CODECS[key];s=dict(s)
 if key=='rawvideo' and container=='avi':s['pix']='bgr24';s['alpha_pix']='bgra'
 args=['-c:v',s['encoder'],'-pix_fmt',s['alpha_pix'] if alpha and s['alpha_pix'] else s['pix']]+s['options']
 presets={'fast':'veryfast','balanced':'medium','quality':'slow'}
 if s['encoder'] in ('libx264','libx264rgb','libx265'):
  args+=['-preset',presets[speed],'-crf',str(0 if lossless and key!='hevc10' else quality)]
  if s['encoder']=='libx265':args+=['-x265-params','pools=2:frame-threads=2:log-level=error'+(':lossless=1' if lossless else '')]
 elif s['encoder'] in ('h264_videotoolbox','hevc_videotoolbox'):
  args+=['-b:v',str(bitrate)+'k','-allow_sw','0','-realtime','1']
 elif key=='av1':args+=['-preset',{'fast':'12','balanced':'9','quality':'6'}[speed],'-crf',str(min(63,quality+10)),'-svtav1-params','lp=4']
 elif key in ('vp8','vp9'):args+=['-b:v','0','-crf',str(min(63,quality+10)),'-deadline','good','-cpu-used',{'fast':'8','balanced':'5','quality':'2'}[speed]]
 elif key in ('mpeg1','mpeg2','mpeg4','flv1','wmv2'):args+=['-b:v',str(bitrate)+'k']
 return args
