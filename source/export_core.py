"""Pure validation and naming rules for Render Studio. No TouchDesigner dependency."""
from pathlib import Path
import math
import re

VERSION = '1.3.0'
CODECS = {
    'mpeg4': ('MPEG-4 · 通用', '.mp4', False),
    'h264': ('H.264 / AVC', '.mp4', False),
    'h265': ('H.265 / HEVC', '.mp4', False),
    'hap': ('Hap · 高性能 / Alpha', '.mov', True),
    'prores4444': ('ProRes 4444 · Alpha', '.mov', True),
    'prores': ('ProRes · 后期剪辑', '.mov', True),
    'rle': ('Animation · 无损 / Alpha', '.mov', True),
    'gif': ('GIF · 动图（无音频）', '.gif', False),
}
IMAGES = {'png': '.png', 'jpeg': '.jpg', 'exr': '.exr', 'tiff': '.tif', 'bmp': '.bmp', 'dds': '.dds'}

class ExportError(ValueError):
    pass

def integer(value, label):
    try:
        n = float(value)
    except (ValueError, TypeError):
        raise ExportError(label + '必须是整数')
    if not math.isfinite(n) or n != int(n):
        raise ExportError(label + '必须是整数')
    return int(n)

def frame_plan(start, end, fps, warmup=0):
    start, end = integer(start, '起始帧'), integer(end, '结束帧')
    warmup = integer(warmup, '预热帧')
    if start < 0 or end < start:
        raise ExportError('帧范围无效：起始帧须 ≥ 0，结束帧须 ≥ 起始帧（含首尾）')
    try:
        fps = float(fps)
    except (ValueError, TypeError):
        raise ExportError('帧率必须是数字')
    if not math.isfinite(fps) or not 1 <= fps <= 240:
        raise ExportError('帧率须在 1–240 FPS 之间')
    if warmup < 0 or warmup > 10000:
        raise ExportError('预热须在 0–10000 帧之间')
    if end - start > 10000000:
        raise ExportError('单次任务超过 1000 万帧，请拆分范围')
    return dict(start=start, end=end, fps=fps, count=end-start+1,
                warm_start=max(0,start-warmup), seconds=(end-start+1)/fps)

def audio_plan(start, end, fps, rate, source_samples):
    """Offline audio sample budget. First sample locks to the start frame's timeline
    second (start/fps); N inclusive frames map to round(N*rate/fps) samples via one
    cumulative boundary, never per-frame rounding. Source shortfall pads silence."""
    plan = frame_plan(start, end, fps)
    try:
        r = float(rate)
    except (ValueError, TypeError):
        raise ExportError('音频采样率必须是数字')
    if not math.isfinite(r) or not 1000 <= r <= 768000:
        raise ExportError('音频采样率须在 1000–768000 Hz 之间')
    src = max(0, int(source_samples))
    offset = int(round(start * r / plan['fps']))
    count = int(round(plan['count'] * r / plan['fps']))
    take = max(0, min(count, src - offset))
    return dict(offset=offset, count=count, take=take, pad=count-take,
                rate=int(round(r)), seconds=count/r)

def basename(value):
    name = str(value).strip()
    if not name or name in {'.','..'}:
        raise ExportError('请输入文件名（不含扩展名）')
    if re.search(r'[\x00-\x1f<>:"/\\|?*]', name):
        raise ExportError('文件名不能包含路径分隔符或 < > : " | ? * 等字符')
    if name.endswith(('.', ' ')):
        raise ExportError('文件名不能以句点或空格结尾')
    # Strip only known media suffixes; preserve dots in user names.
    if Path(name).suffix.lower() in {'.mp4','.mov','.mkv','.gif','.png','.jpg','.jpeg','.exr','.tif','.tiff','.avi','.webm','.wmv','.mxf','.ts','.mpg','.mpeg','.bmp','.dds'}:
        name = name[:name.rfind('.')]
    if not name:
        raise ExportError('文件名不能为空')
    if re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', name, re.I):
        raise ExportError('该名称是 Windows 保留名称，请换一个')
    if len(name.encode('utf-8')) > 180:
        raise ExportError('文件名过长，请缩短至 180 UTF-8 字节以内')
    return name

def resolve_folder(folder, project_folder):
    text = str(folder).strip()
    if not text:
        raise ExportError('请选择导出文件夹，或输入 ./renders')
    if '\x00' in text:
        raise ExportError('文件夹路径含无效字符')
    path = Path(text).expanduser()
    if not path.is_absolute():
        path = Path(project_folder) / path
    return path.resolve()

def target_path(folder, name, suffix, sequence=False, conflict='increment'):
    """Never overwrite. Sequence gets a dedicated directory per take."""
    folder = Path(folder)
    stem = basename(name)
    candidate = folder / (stem if sequence else stem+suffix)
    occupied=lambda p:p.exists() or (not sequence and Path(str(p)+'.json').exists())
    if not occupied(candidate):
        return candidate
    if conflict == 'error':
        raise ExportError('目标已存在：请更换文件名或启用自动编号')
    for i in range(1, 100000):
        candidate = folder / (f'{stem}_{i:03d}' + ('' if sequence else suffix))
        if not occupied(candidate):
            return candidate
    raise ExportError('无法分配未占用的输出文件名')

def codec_name(requested, available):
    candidates = {'h264': ('h264','h264nvgpu'), 'h265': ('h265','h265nvgpu')}.get(requested,(requested,))
    for name in candidates:
        if name in available:
            return name
    raise ExportError('当前系统没有此编码器，请改用 MPEG-4、PNG 序列或其他可用编码器')

def validate_codec(codec, kind, alpha, license_name, audio=False):
    if kind not in ('movie','sequence'):
        raise ExportError('未知输出类型')
    if kind == 'sequence':
        if audio:
            raise ExportError('图像序列不包含音频；请清空本次音频选择或改为视频录制')
        return
    if codec not in CODECS:
        raise ExportError('未知编码器')
    if codec in ('h264','h265') and 'non-commercial' in license_name.lower():
        raise ExportError('H.264 / H.265 需要 TouchDesigner 商业或 Pro 许可证；可改用 MPEG-4 或 PNG 序列')
    if alpha and not CODECS[codec][2]:
        raise ExportError('此编码器不保留 Alpha。可选择 Hap、Animation、ProRes 4444 或 PNG 序列')
    if codec == 'gif' and audio:
        raise ExportError('GIF 不支持音频；音频选择不会被自动清空，请手动移除')

def format_duration(seconds):
    if not math.isfinite(seconds) or seconds < 0:
        return '—'
    m,s=divmod(int(round(seconds)),60);h,m=divmod(m,60)
    return f'{h:02d}:{m:02d}:{s:02d}'

CONTAINERS={'mp4':('MP4',['h264','h265','mpeg4']), 'mov':('MOV / QuickTime',['prores','prores4444','h264','h265','rle','hap']), 'gif':('GIF',['gif'])}
def validate_container(container,codec):
    if container not in CONTAINERS or codec not in CONTAINERS[container][1]:
        raise ExportError('当前视频格式与编码器不兼容，请重新选择')
