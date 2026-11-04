import unittest,tempfile,zipfile
from pathlib import Path
import catalog as c
import export_core as k
class Rules(unittest.TestCase):
 def test_every_container_has_choices(self):
  for name in c.CONTAINERS:self.assertTrue(c.choices(name))
 def test_registry_has_real_backends(self):
  for name,s in c.CODECS.items():self.assertTrue(s['td'] or s['encoder'],name)
 def test_webm_excludes_h264(self):self.assertNotIn('h264',c.choices('webm'))
 def test_mp4_excludes_prores(self):
  with self.assertRaises(ValueError):c.validate('mp4','prores',1920,1080,30)
 def test_prores_alpha_configs(self):
  for name in ('prores4444','prores_xq'):self.assertTrue(c.CODECS[name]['force_alpha']);c.validate('mov',name,1920,1080,30,True)
 def test_h26x_alpha_rejected(self):
  with self.assertRaises(ValueError):c.validate('mp4','h264',1920,1080,30,True)
 def test_odd_subsampled_size(self):
  with self.assertRaises(ValueError):c.validate('webm','vp9',321,180,30)
 def test_dnxhr_minimum(self):
  with self.assertRaises(ValueError):c.validate('mov','dnxhr_hq',128,72,30)
 def test_broadcast_frame_rate(self):
  with self.assertRaises(ValueError):c.validate('mxf','mpeg2422',1920,1080,17)
 def test_native_container_rejected(self):
  with self.assertRaises(ValueError):c.select_backend('mpeg4','mkv','native')
 def test_hap_external_rejected(self):
  with self.assertRaises(ValueError):c.select_backend('hap','mov','ffmpeg')
 def test_auto_h264_does_not_bypass_td_license(self):self.assertEqual(c.select_backend('h264','mp4'),'ffmpeg')
 def test_native_prores_default(self):self.assertEqual(c.select_backend('prores','mov'),'native')
 def test_raw_avi_color_order(self):
  a=c.ffmpeg_options('rawvideo',container='avi');self.assertEqual(a[a.index('-pix_fmt')+1],'bgr24')
 def test_raw_avi_alpha_order(self):
  a=c.ffmpeg_options('rawvideo',container='avi',alpha=True);self.assertEqual(a[a.index('-pix_fmt')+1],'bgra')
 def test_high_precision_metadata(self):self.assertEqual(c.CODECS['ffv1_16']['depth'],16);self.assertEqual(c.CODECS['hevc10']['depth'],10)
 def test_supported_extensions(self):
  for suffix in ('.mkv','.webm','.ts','.avi','.wmv','.mxf','.mpg'):self.assertEqual(k.basename('片段'+suffix),'片段')
 def test_cancelled_job_manifest_reserves_name(self):
  with tempfile.TemporaryDirectory() as d:
   (Path(d)/'take.mp4.json').write_text('{}')
   self.assertEqual(k.target_path(d,'take','.mp4').name,'take_001.mp4')
 def test_inclusive_range(self):self.assertEqual(k.frame_plan(11,15,30)['count'],5)
 def test_audio_plan_exact_frames(self):
  a=k.audio_plan(0,29,30,48000,10**9);self.assertEqual((a['offset'],a['count'],a['take'],a['pad']),(0,48000,48000,0))
 def test_audio_plan_nonzero_start_offset(self):
  a=k.audio_plan(5,9,30,48000,10**9);self.assertEqual((a['offset'],a['count']),(8000,8000));self.assertEqual(a['pad'],0)
 def test_audio_plan_single_frame(self):
  a=k.audio_plan(0,0,30,48000,100);self.assertEqual((a['count'],a['take'],a['pad']),(1600,100,1500))
 def test_audio_plan_fractional_fps(self):
  a=k.audio_plan(0,9,29.97,44100,10**9);self.assertEqual(a['count'],round(10*44100/29.97));self.assertEqual(a['rate'],44100)
 def test_audio_plan_rate_validation(self):
  with self.assertRaises(k.ExportError):k.audio_plan(0,9,30,0,100)
  with self.assertRaises(k.ExportError):k.audio_plan(0,9,30,'x',100)
 def test_audio_plan_frame_validation_reused(self):
  with self.assertRaises(k.ExportError):k.audio_plan(-1,9,30,48000,100)
  with self.assertRaises(k.ExportError):k.audio_plan(9,1,30,48000,100)

class BootstrapRules(unittest.TestCase):
 def fake_download(self,calls):
  def download(url,dest,sha,size,cancel,progress):
   calls.append(url)
   if url.endswith('.zip'):
    member='ffprobe' if url.endswith('ffprobe.zip') else 'ffmpeg'
    with zipfile.ZipFile(dest,'w') as bundle:bundle.writestr(member,b'fake-binary')
   else:dest.write_bytes(b'x'*size)
   progress(size)
  return download
 def fake_verify(self,candidate,required):return True
 def test_manifest_is_pinned(self):
  self.assertEqual(set(k.FFMPEG_MANIFEST),{'arm64','amd64'})
  for arch in ('arm64','amd64'):
   resources=k.ffmpeg_resources(arch)
   self.assertEqual(len(resources),4)
   for name,url,sha,size in resources:self.assertTrue(url.startswith('https://'));self.assertEqual(len(sha),64);self.assertGreater(size,0)
 def test_install_reuse_and_notice(self):
  with tempfile.TemporaryDirectory() as d:
   calls=[];progress=[]
   path=k.install_managed(d,arch='arm64',progress=progress.append,download_fn=self.fake_download(calls),verify_fn=self.fake_verify)
   self.assertTrue(Path(path).is_file());self.assertEqual(len(calls),4);self.assertEqual(progress[-1]['fraction'],1.0)
   notice=Path(d)/'9.0.2'/'arm64'/'NOTICE.txt'
   self.assertIn(k.FFMPEG_SOURCE_URL,notice.read_text())
   again=k.install_managed(d,arch='arm64',download_fn=self.fake_download(calls),verify_fn=self.fake_verify)
   self.assertEqual(path,again);self.assertEqual(len(calls),4)
 def test_download_failure_cleans_staging_and_lock(self):
  with tempfile.TemporaryDirectory() as d:
   def fail(*args):raise k.ExportError('bad hash')
   with self.assertRaises(k.ExportError):k.install_managed(d,arch='arm64',download_fn=fail,verify_fn=self.fake_verify)
   self.assertFalse((Path(d)/'9.0.2'/'arm64').exists());self.assertFalse((Path(d)/'.install.lock').exists())
 def test_cancel_cleans_staging_and_lock(self):
  with tempfile.TemporaryDirectory() as d:
   def cancel(*args):raise k.BootstrapCancelled('cancelled')
   with self.assertRaises(k.BootstrapCancelled):k.install_managed(d,arch='arm64',download_fn=cancel,verify_fn=self.fake_verify)
   self.assertFalse((Path(d)/'9.0.2'/'arm64').exists());self.assertFalse((Path(d)/'.install.lock').exists())
 def test_zip_member_allowlist(self):
  with tempfile.TemporaryDirectory() as d:
   archive=Path(d)/'bad.zip'
   with zipfile.ZipFile(archive,'w') as bundle:bundle.writestr('../escape',b'x');bundle.writestr('extra',b'y')
   with self.assertRaises(k.ExportError):k.extract_single_binary(archive,'ffmpeg',Path(d)/'ffmpeg')
   self.assertFalse((Path(d)/'ffmpeg').exists())
 def test_download_rejects_non_https(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(k.ExportError):k.download_verified('http://example.invalid/ffmpeg',Path(d)/'x','0'*64,1)
   self.assertFalse((Path(d)/'x').exists())
if __name__=='__main__':unittest.main(verbosity=2)
