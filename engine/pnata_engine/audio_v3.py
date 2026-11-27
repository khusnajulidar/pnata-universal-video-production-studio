"""Reviewed audio mixing primitives. Human review is not semantic detection."""
import math, shutil, subprocess
from pathlib import Path

class AudioV3Error(ValueError):
    pass

def build_audio_filter(project):
    duration=float(project['duration'])
    if not math.isfinite(duration) or duration<=0: raise AudioV3Error('Invalid project duration.')
    tracks=project.get('audio_tracks', [])
    if not tracks: return f'anullsrc=r=48000:cl=stereo,atrim=duration={duration:.9f}[mix]'
    filters=[]; labels=[]
    for i,t in enumerate(tracks):
        if t.get('category') not in {'narration','sfx','natural_ambience'}: raise AudioV3Error('Forbidden or unknown audio category.')
        if t.get('reviewed_non_musical') is not True: raise AudioV3Error('Audio lacks human non-musical review.')
        if t.get('loop',False): raise AudioV3Error('Audio looping is forbidden.')
        start=float(t['start']); trim=float(t.get('in_point',0)); length=float(t['duration']); gain=float(t['gain_db'])
        fi=float(t.get('fade_in',0)); fo=float(t.get('fade_out',0))
        if not all(math.isfinite(x) for x in [start,trim,length,gain,fi,fo]): raise AudioV3Error('Audio values must be finite.')
        if start<0 or trim<0 or length<=0 or gain < -60 or gain > 12: raise AudioV3Error('Invalid audio timing or gain.')
        if start+length>duration+1e-6: raise AudioV3Error('Audio track exceeds project duration.')
        if fi<0 or fo<0 or fi+fo>length: raise AudioV3Error('Audio fades exceed track duration.')
        chain=[f'atrim=start={trim:.9f}:duration={length:.9f}','asetpts=PTS-STARTPTS',f'volume={gain:.6f}dB']
        if fi: chain.append(f'afade=t=in:st=0:d={fi:.9f}')
        if fo: chain.append(f'afade=t=out:st={length-fo:.9f}:d={fo:.9f}')
        chain.append(f'adelay={round(start*1000)}:all=1')
        label=f'a{i}'; filters.append(f'[{i}:a]'+','.join(chain)+f'[{label}]'); labels.append(f'[{label}]')
    filters.append(''.join(labels)+f'amix=inputs={len(labels)}:duration=longest:normalize=0,apad,atrim=duration={duration:.9f},asetpts=PTS-STARTPTS[mix]')
    return ';'.join(filters)

def probe_audio_asset(path, ffprobe=None):
    binary=ffprobe or shutil.which('ffprobe')
    if not binary: raise AudioV3Error('FFprobe unavailable.')
    p=subprocess.run([binary,'-v','error','-show_entries','stream=codec_type,duration','-show_entries','format=duration','-of','json',str(path)],check=True,capture_output=True,text=True)
    import json
    data=json.loads(p.stdout); streams=[s for s in data.get('streams',[]) if s.get('codec_type')=='audio']
    if not streams: raise AudioV3Error(f'No audio stream found in {path}.')
    try: result=float(streams[0].get('duration') or data.get('format',{}).get('duration'))
    except (TypeError,ValueError) as exc: raise AudioV3Error('Cannot verify audio duration.') from exc
    if not math.isfinite(result) or result<=0: raise AudioV3Error('Invalid audio duration.')
    return result

def render_audio_mix(project, project_root, output_path, ffmpeg=None, ffprobe=None):
    ffmpeg=ffmpeg or shutil.which('ffmpeg')
    if not ffmpeg: raise AudioV3Error('FFmpeg unavailable.')
    root=Path(project_root).resolve(); assets={a['id']:a for a in project.get('assets',[])}; args=[ffmpeg,'-hide_banner','-loglevel','error','-y']
    for t in project.get('audio_tracks',[]):
        a=assets.get(t['asset_id'])
        if not a or a.get('media_type')!='audio' or a.get('audio_category')!=t.get('category'): raise AudioV3Error('Invalid audio asset reference.')
        src=(root/a['path']).resolve()
        try: src.relative_to(root)
        except ValueError as exc: raise AudioV3Error('Audio asset path escapes project directory.') from exc
        if not src.is_file(): raise AudioV3Error(f'Audio asset not found: {src}')
        if float(t.get('in_point',0))+float(t['duration'])>probe_audio_asset(src,ffprobe)+1e-6: raise AudioV3Error('Audio trim exceeds source duration.')
        args.extend(['-i',str(src)])
    args.extend(['-filter_complex',build_audio_filter(project),'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le','-t',str(float(project['duration']))])
    out=Path(output_path).resolve(); out.parent.mkdir(parents=True,exist_ok=True); args.append(str(out)); subprocess.run(args,check=True); return out
