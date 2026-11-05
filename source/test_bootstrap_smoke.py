"""Real managed FFmpeg download and H.264/AAC smoke test for desktop CI runners."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

import catalog
import export_core as core


def main():
    arch = core.host_arch()
    required = sorted({item['encoder'] for item in catalog.CODECS.values() if item['encoder']} |
                      {item['audio'] for item in catalog.CONTAINERS.values() if item['audio']})
    with tempfile.TemporaryDirectory(prefix='renderstudio_bootstrap_') as workspace:
        os.environ['RENDERSTUDIO_FFMPEG_HOME'] = workspace
        ffmpeg = core.install_managed(required_encoders=required)
        ffprobe = core.managed_ffprobe()
        core.verify_managed_install(core.managed_dir(), required)
        output = Path(workspace) / 'managed-smoke.mp4'
        subprocess.run([
            ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
            '-f', 'lavfi', '-i', 'testsrc2=size=320x180:rate=30',
            '-f', 'lavfi', '-i', 'sine=frequency=1000:sample_rate=48000',
            '-af', 'aformat=channel_layouts=stereo',
            '-t', '0.1', '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-threads', '1', str(output),
        ], check=True, timeout=180)
        streams = json.loads(subprocess.check_output([
            ffprobe, '-v', 'error', '-count_frames',
            '-show_entries', 'stream=codec_type,codec_name,width,height,nb_read_frames,sample_rate,channels',
            '-of', 'json', str(output),
        ], text=True, timeout=120))['streams']
        video = next(item for item in streams if item['codec_type'] == 'video')
        audio = next(item for item in streams if item['codec_type'] == 'audio')
        assert video['codec_name'] == 'h264', video
        assert (video['width'], video['height']) == (320, 180), video
        assert int(video['nb_read_frames']) == 3, video
        assert audio['codec_name'] == 'aac' and int(audio['sample_rate']) == 48000, audio
        assert int(audio['channels']) == 2, audio
        reused = core.install_managed(required_encoders=required)
        assert reused == ffmpeg, (reused, ffmpeg)
        print(json.dumps({'overall_pass': True, 'arch': arch, 'video': video, 'audio': audio,
                          'second_run_reuse': True}, indent=2))


if __name__ == '__main__':
    main()
