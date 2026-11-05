"""Pure validation, naming and FFmpeg bootstrap rules. No TouchDesigner dependency."""
from pathlib import Path
import hashlib
import math
import os
import platform
import re
import shutil
import ssl
import subprocess
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import zipfile

VERSION = '1.5.0'
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


FFMPEG_VERSION = '9.0.2'
FFMPEG_LICENSE_URL = 'https://raw.githubusercontent.com/FFmpeg/FFmpeg/n9.0.2/COPYING.GPLv3'
FFMPEG_LICENSE_SHA256 = '8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903'
FFMPEG_LICENSE_SIZE = 35147
FFMPEG_SOURCE_URL = 'https://ffmpeg.org/releases/ffmpeg-9.0.2.tar.xz'
FFMPEG_BUILD_URL = 'https://git.martin-riedl.de/ffmpeg/build-script'
FFMPEG_MANIFEST = {
    'arm64': {
        'stamp': '1789931890_9.0.2',
        'ffmpeg_sha256': 'c8ed4c4e6978a03c485edbfe4e0a5dc2380f8a30bba5150531b31b094492d924',
        'ffprobe_sha256': 'fcbe839537485eaee7a7a8bc5cbc0f90d53617e80943e8a5b2e31cb851197ea6',
        'versions_sha256': 'fc92572e752e09b20e7ff28d64fb7096f7bc1a0d589b2e40f17ac91b7fd0ca61',
        'ffmpeg_size': 28395699, 'ffprobe_size': 28317701, 'versions_size': 1948,
    },
    'amd64': {
        'stamp': '1789931006_9.0.2',
        'ffmpeg_sha256': '7c6b4125b191cbf773832dc51f424cf2b6bb7da43007d1e066f95909e47cacd4',
        'ffprobe_sha256': '2322438ed2f6319a691291b247d09c69dcaa3a982460d1f269a7e1af335cfdfd',
        'versions_sha256': '64347e66bb487d52c6a8a43180028dc2a4d1dc0519ec81233d55e2bd59ebd98e',
        'ffmpeg_size': 33816391, 'ffprobe_size': 33719233, 'versions_size': 1948,
    },
    'win64': {
        'stamp': 'autobuild-2026-11-04-12-51',
        'bundle': 'ffmpeg-n9.0.2-47-gb204e94e90-win64-gpl-9.0.zip',
        'ffmpeg_sha256': 'db2867364898bf8b68f5404b998165dfd8d31c9bfabc2a35d6e0c941bf33c1ea',
        'versions_sha256': '9508e4f4b1dd98a00391e1f781354dbab6692c78435d570da86b156a4088d4be',
        'ffmpeg_size': 195111884, 'versions_size': 5728,
        'build_url': 'https://github.com/BtbN/FFmpeg-Builds',
    },
}


class BootstrapCancelled(ExportError):
    pass


def host_arch():
    system = platform.system()
    if system == 'Windows':
        machine = platform.machine().lower()
        if machine in ('amd64', 'x86_64'):
            return 'win64'
        raise ExportError('Windows 自动配置目前仅支持 x86_64；其他架构请手动指定系统 FFmpeg')
    if system != 'Darwin':
        raise ExportError('FFmpeg 自动配置目前支持 macOS 与 Windows x86_64；其他平台请使用系统 FFmpeg')
    try:
        if subprocess.check_output(['/usr/sbin/sysctl', '-n', 'hw.optional.arm64'], text=True, timeout=5).strip() == '1':
            return 'arm64'
        machine = subprocess.check_output(['/usr/sbin/sysctl', '-n', 'hw.machine'], text=True, timeout=5).strip()
    except Exception:
        machine = platform.machine()
    if machine in ('arm64', 'aarch64'):
        return 'arm64'
    if machine in ('x86_64', 'amd64'):
        return 'amd64'
    raise ExportError('当前 macOS 架构没有已验证的 FFmpeg 包：' + machine)


def binary_name(name, arch=None):
    return name + '.exe' if (arch or host_arch()) == 'win64' else name


def managed_root(root=None):
    if root is not None:
        return Path(root).expanduser()
    override = os.environ.get('RENDERSTUDIO_FFMPEG_HOME', '').strip()
    if override:
        return Path(override).expanduser()
    return Path.home() / 'Library' / 'Application Support' / 'RenderStudio' / 'ffmpeg'


def managed_dir(root=None, arch=None):
    return managed_root(root) / FFMPEG_VERSION / (arch or host_arch())


def managed_executable(root=None, arch=None):
    binary = managed_dir(root, arch) / 'bin' / binary_name('ffmpeg', arch)
    probe = managed_dir(root, arch) / 'bin' / binary_name('ffprobe', arch)
    if binary.is_file() and probe.is_file() and os.access(binary, os.X_OK) and os.access(probe, os.X_OK):
        return str(binary)
    return None


def managed_ffprobe(root=None, arch=None):
    binary = managed_dir(root, arch) / 'bin' / binary_name('ffprobe', arch)
    return str(binary) if binary.is_file() and os.access(binary, os.X_OK) else None


def ffmpeg_resources(arch):
    if arch not in FFMPEG_MANIFEST:
        raise ExportError('没有此架构的 FFmpeg 下载清单：' + str(arch))
    item = FFMPEG_MANIFEST[arch]
    if arch == 'win64':
        prefix = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/' + item['stamp'] + '/'
        return [
            ('bundle', prefix + item['bundle'], item['ffmpeg_sha256'], item['ffmpeg_size']),
            ('license', FFMPEG_LICENSE_URL, FFMPEG_LICENSE_SHA256, FFMPEG_LICENSE_SIZE),
            ('versions', prefix + 'checksums.sha256', item['versions_sha256'], item['versions_size']),
        ]
    prefix = 'https://ffmpeg.martin-riedl.de/download/macos/' + arch + '/' + item['stamp'] + '/'
    return [
        ('ffmpeg', prefix + 'ffmpeg.zip', item['ffmpeg_sha256'], item['ffmpeg_size']),
        ('ffprobe', prefix + 'ffprobe.zip', item['ffprobe_sha256'], item['ffprobe_size']),
        ('license', FFMPEG_LICENSE_URL, FFMPEG_LICENSE_SHA256, FFMPEG_LICENSE_SIZE),
        ('versions', prefix + 'versions.txt', item['versions_sha256'], item['versions_size']),
    ]


def _check_cancel(cancel_event):
    if cancel_event is not None and cancel_event.is_set():
        raise BootstrapCancelled('已取消 FFmpeg 自动配置；未修改现有环境')


def default_ssl_context():
    try:
        import certifi
        if Path(certifi.where()).is_file():
            return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    if Path('/etc/ssl/cert.pem').is_file():
        return ssl.create_default_context(cafile='/etc/ssl/cert.pem')
    return ssl.create_default_context()


def download_verified(url, destination, expected_sha256, expected_size, cancel_event=None, progress=None):
    parts = urllib.parse.urlsplit(url)
    allowed_hosts = ('ffmpeg.martin-riedl.de', 'raw.githubusercontent.com', 'github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com')
    if parts.scheme != 'https' or parts.hostname not in allowed_hosts:
        raise ExportError('拒绝未列入白名单的下载地址')
    destination = Path(destination)
    partial = destination.with_name(destination.name + '.part')
    digest = hashlib.sha256()
    received = 0
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; RenderStudio/1.5)'})
    try:
        with urllib.request.urlopen(request, timeout=30, context=default_ssl_context()) as response, partial.open('xb') as stream:
            while True:
                _check_cancel(cancel_event)
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                received += len(chunk)
                if received > expected_size:
                    raise ExportError('FFmpeg 下载内容超过清单大小')
                digest.update(chunk)
                stream.write(chunk)
                if progress:
                    progress(received)
        if received != expected_size or digest.hexdigest() != expected_sha256:
            raise ExportError('FFmpeg 下载校验失败；已丢弃未验证文件')
        os.replace(partial, destination)
    except Exception:
        if partial.exists():
            partial.unlink()
        raise


def extract_single_binary(archive, member, destination):
    destination = Path(destination)
    partial = destination.with_name(destination.name + '.part')
    try:
        with zipfile.ZipFile(archive) as bundle:
            files = [item for item in bundle.infolist() if not item.is_dir()]
            if len(files) != 1 or files[0].filename != member:
                raise ExportError('FFmpeg ZIP 成员与清单不符')
            if bundle.testzip() is not None:
                raise ExportError('FFmpeg ZIP CRC 校验失败')
            with bundle.open(files[0]) as source, partial.open('xb') as target:
                shutil.copyfileobj(source, target, 1024 * 1024)
        partial.chmod(0o755)
        os.replace(partial, destination)
    except Exception:
        if partial.exists():
            partial.unlink()
        raise


def extract_zip_member(archive, member, destination):
    destination = Path(destination)
    partial = destination.with_name(destination.name + '.part')
    try:
        with zipfile.ZipFile(archive) as bundle:
            matches = [item for item in bundle.infolist() if not item.is_dir() and item.filename == member]
            if len(matches) != 1:
                raise ExportError('FFmpeg ZIP 缺少必需成员：' + member)
            if bundle.testzip() is not None:
                raise ExportError('FFmpeg ZIP CRC 校验失败')
            with bundle.open(matches[0]) as source, partial.open('xb') as target:
                shutil.copyfileobj(source, target, 1024 * 1024)
        partial.chmod(0o755)
        os.replace(partial, destination)
    except Exception:
        if partial.exists():
            partial.unlink()
        raise


def extract_windows_binary(archive, name, destination):
    with zipfile.ZipFile(archive) as bundle:
        names = set(bundle.namelist())
    matches = [member for member in names if member in ('bin/' + name, name) or member.endswith('/bin/' + name) or member.endswith('/' + name)]
    if len(matches) == 1:
        return extract_zip_member(archive, matches[0], destination)
    raise ExportError('FFmpeg ZIP 缺少必需成员：bin/' + name + ' 或 ' + name + '；实际成员：' + ', '.join(sorted(names)[:40]))


def verify_pe_arch(binary, expected_machine=0x8664):
    data = Path(binary).read_bytes()
    if len(data) < 0x40 or data[:2] != b'MZ':
        raise ExportError('Windows 可执行文件缺少 MZ/PE 头')
    offset = int.from_bytes(data[0x3C:0x40], 'little')
    if offset + 6 > len(data) or data[offset:offset + 4] != b'PE\0\0':
        raise ExportError('Windows 可执行文件缺少有效 PE 头')
    machine = int.from_bytes(data[offset + 4:offset + 6], 'little')
    if machine != expected_machine:
        raise ExportError('Windows 可执行文件架构不符：0x%04x' % machine)
    return machine


def execution_prefix(windows_package):
    if not windows_package or platform.system() == 'Windows':
        return []
    wine = shutil.which('wine64') or shutil.which('wine')
    if not wine:
        raise ExportError('Windows 包已下载，但当前系统无法执行 Windows 验证；请在 Windows runner 上验收')
    return [wine]


def verify_managed_install(candidate, required_encoders=()):
    candidate = Path(candidate)
    windows_package = (candidate / 'bin' / 'ffmpeg.exe').is_file()
    ffmpeg = candidate / 'bin' / ('ffmpeg.exe' if windows_package else 'ffmpeg')
    ffprobe = candidate / 'bin' / ('ffprobe.exe' if windows_package else 'ffprobe')
    prefix = execution_prefix(windows_package)
    for binary, name in ((ffmpeg, 'ffmpeg'), (ffprobe, 'ffprobe')):
        if windows_package:
            verify_pe_arch(binary)
        result = subprocess.run([*prefix, str(binary), '-version'], capture_output=True, text=True, timeout=60)
        if result.returncode or not result.stdout.splitlines() or ('version ' + FFMPEG_VERSION) not in result.stdout.splitlines()[0]:
            detail = (result.stdout + result.stderr).strip()[-500:]
            raise ExportError(name + ' 无法执行或版本不符：code=' + str(result.returncode) + ' output=' + detail)
        if name == 'ffmpeg' and ('--enable-gpl' not in result.stdout or '--enable-version3' not in result.stdout):
            raise ExportError('FFmpeg 构建许可与发布记录不符')
        if not windows_package and shutil.which('codesign'):
            signed = subprocess.run(['codesign', '--verify', '--strict', str(binary)], capture_output=True, text=True, timeout=30)
            if signed.returncode:
                raise ExportError(name + ' 苹果代码签名验证失败')
        if not windows_package and shutil.which('otool'):
            linked = subprocess.check_output(['otool', '-L', str(binary)], text=True, timeout=30)
            for line in linked.splitlines()[1:]:
                dependency = line.strip().split(' ', 1)[0]
                if dependency and not dependency.startswith(('/usr/lib/', '/System/Library/')):
                    raise ExportError(name + ' 含有非系统动态依赖：' + dependency)
    if required_encoders:
        listing = subprocess.check_output([*prefix, str(ffmpeg), '-hide_banner', '-encoders'], text=True, timeout=60)
        available = set(re.findall(r'^\s*[VAS][A-Z.]{5}\s+(\S+)', listing, re.M))
        missing = [name for name in required_encoders if name not in available]
        if missing:
            raise ExportError('FFmpeg 缺少项目所需编码器：' + ', '.join(missing))
    return True


def ffmpeg_notice(arch):
    lines = [
        'RenderStudio managed FFmpeg distribution', '',
        'Version: ' + FFMPEG_VERSION,
        'Architecture: Windows x86_64' if arch == 'win64' else 'macOS/' + arch,
        'Build license: GNU General Public License v3 (build uses --enable-gpl and --enable-version3)',
        'Upstream source: ' + FFMPEG_SOURCE_URL,
        'Build script: ' + FFMPEG_MANIFEST[arch].get('build_url', FFMPEG_BUILD_URL),
        'License text: share/COPYING.GPLv3', '',
        'Pinned downloads:',
    ]
    for name, url, sha256, size in ffmpeg_resources(arch):
        lines.append('- ' + name + ' | ' + url + ' | SHA-256 ' + sha256 + ' | bytes ' + str(size))
    lines += ['', 'FFmpeg is downloaded as a separate executable; it is not linked into RenderStudio.',
              'Installed: ' + time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())]
    return '\n'.join(lines) + '\n'


def install_managed(root=None, arch=None, progress=None, cancel_event=None, required_encoders=(), download_fn=None, verify_fn=None):
    arch = arch or host_arch()
    base = managed_root(root)
    base.mkdir(parents=True, exist_ok=True)
    existing = managed_executable(base, arch)
    if existing:
        return existing
    target = managed_dir(base, arch)
    lock = base / '.install.lock'
    deadline = time.monotonic() + 120
    while True:
        try:
            lock.mkdir()
            break
        except FileExistsError:
            existing = managed_executable(base, arch)
            if existing:
                return existing
            _check_cancel(cancel_event)
            if time.monotonic() > deadline:
                raise ExportError('另一 RenderStudio 实例正在配置 FFmpeg，请稍后重试')
            time.sleep(0.25)
    staging = None
    download_fn = download_fn or download_verified
    verify_fn = verify_fn or verify_managed_install
    cancel_event = cancel_event or threading.Event()
    try:
        staging = Path(tempfile.mkdtemp(prefix='.install-', dir=str(base)))
        resources = ffmpeg_resources(arch)
        total = sum(item[3] for item in resources)
        completed = 0
        for name, url, sha256, size in resources:
            _check_cancel(cancel_event)
            if progress:
                progress({'stage': name, 'fraction': completed / total, 'message': '正在下载 FFmpeg 9.0.2 · ' + name})
            destination = staging / (name + ('.zip' if name in ('ffmpeg', 'ffprobe', 'bundle') else '.txt'))
            before = completed

            def advance(received):
                if progress:
                    progress({'stage': name, 'fraction': min(0.95, (before + received) / total), 'message': '正在下载 FFmpeg 9.0.2 · ' + name})

            download_fn(url, destination, sha256, size, cancel_event, advance)
            completed += size
        (staging / 'bin').mkdir()
        (staging / 'share').mkdir()
        if arch == 'win64':
            extract_windows_binary(staging / 'bundle.zip', 'ffmpeg.exe', staging / 'bin' / 'ffmpeg.exe')
            extract_windows_binary(staging / 'bundle.zip', 'ffprobe.exe', staging / 'bin' / 'ffprobe.exe')
            (staging / 'bundle.zip').unlink()
        else:
            extract_single_binary(staging / 'ffmpeg.zip', 'ffmpeg', staging / 'bin' / 'ffmpeg')
            extract_single_binary(staging / 'ffprobe.zip', 'ffprobe', staging / 'bin' / 'ffprobe')
            (staging / 'ffmpeg.zip').unlink()
            (staging / 'ffprobe.zip').unlink()
        os.replace(staging / 'license.txt', staging / 'share' / 'COPYING.GPLv3')
        os.replace(staging / 'versions.txt', staging / 'share' / 'versions.txt')
        (staging / 'NOTICE.txt').write_text(ffmpeg_notice(arch), encoding='utf-8')
        _check_cancel(cancel_event)
        verify_fn(staging, required_encoders)
        if target.exists():
            if managed_executable(base, arch):
                return managed_executable(base, arch)
            backup = target.with_name(target.name + '.replaced-' + str(time.time_ns()))
            os.replace(target, backup)
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staging, target)
        if progress:
            progress({'stage': 'ready', 'fraction': 1.0, 'message': 'FFmpeg 9.0.2 已配置完成'})
        return str(target / 'bin' / binary_name('ffmpeg', arch))
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging)
        if lock.exists():
            lock.rmdir()
