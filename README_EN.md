<div align="center">
  <h1>RenderStudio</h1>
  <p><strong>A controlled, verifiable path from TouchDesigner visuals to finished video.</strong></p>
  <p>Native COMP export panel · Offline frame-based audio assembly · 11 containers / 39 codec configurations</p>
  <p>
    <a href="README_EN.md"><strong>English</strong></a> ·
    <a href="README.md"><strong>中文</strong></a> ·
    <a href="https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.3.0"><strong>Download v1.3.0</strong></a> ·
    <a href="PROMOTION.md">Launch kit</a>
  </p>
  <p>
    <a href="https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/tag/v1.3.0"><img src="https://img.shields.io/badge/release-v1.3.0-7C6FF0?style=for-the-badge" alt="Release v1.3.0"></a>
    <img src="https://img.shields.io/badge/TouchDesigner-2025.31550-222222?style=for-the-badge" alt="TouchDesigner 2025.31550">
    <img src="https://img.shields.io/badge/macOS-tested-333333?style=for-the-badge" alt="Tested on macOS">
    <img src="https://img.shields.io/badge/FFmpeg-external-orange?style=for-the-badge" alt="External FFmpeg required">
  </p>
</div>

<p align="center">
  <a href="preview/RenderStudio_1.3.png"><img src="preview/RenderStudio_1.3.png" alt="RenderStudio 1.3 native TouchDesigner panel" width="1000"></a>
  <br>
  <sub>The actual RenderStudio 1.3 TouchDesigner panel—not a web mockup or composite demo.</sub>
</p>

> [!IMPORTANT]
> Validation currently covers **macOS / TouchDesigner 2025.31550** only. FFmpeg must be installed separately; no FFmpeg binary is bundled. The original declaration limits use to **personal or non-commercial purposes**. Commercial use requires authorization from SkyFeng; see the [original author declaration](原作者声明.txt).

## Download and install

| Your goal | Release asset | How to use it |
|---|---|---|
| Add the component to your own TD project | [`RenderStudio_1.3_TD2025.tox`](https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/download/v1.3.0/RenderStudio_1.3_TD2025.tox) | Drag it into a TouchDesigner project |
| Open the companion code-rain project | [`RenderStudio_1.3_TD2025_code-rain.toe`](https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/download/v1.3.0/RenderStudio_1.3_TD2025_code-rain.toe) | Open it with TD 2025.31550 |
| Verify published files | [`SHA256SUMS`](https://github.com/luoboruodai/Touchdesigner-Renderstudio/releases/download/v1.3.0/SHA256SUMS) | Check the corresponding Release members and assets |

GitHub's automatic **Source code** archives are for source review; they do not replace the installable assets above.

### Requirements

1. **TouchDesigner 2025.31550 on macOS**.
2. FFmpeg installed separately, with `ffmpeg` and `ffprobe` available. A custom executable path can be set on the component's advanced page.
3. Download the TOX or TOE and validate your own project with a short sample first.

### Start an export

1. Connect the final TOP to the component input, or set its name in “Source TOP”. For a sibling node, a name such as `out1` is sufficient; leave it empty to follow the input.
2. Choose an output folder and filename. The default `./renders` path is relative to the current TOE. Existing files are not overwritten; new names are numbered automatically.
3. Set width, height, frame range and FPS, then choose a container, codec and speed preset.
4. To include audio, provide a CHOP that meets the mode-specific requirements below.
5. Run the settings check, then start rendering or recording.

## What it does

| Capability | Current implementation |
|---|---|
| Two export modes | Real-time recording and frame-range rendering; live camera and microphone inputs remain in real-time recording |
| Offline frame-based audio | Calculates cumulative integer sample boundaries from frame range and FPS, pads missing source audio with silence, and mixes audio during final assembly |
| Extended format catalog | 11 containers and 39 codec, quality-tier and implementation configurations—not 39 independent codec standards |
| Native search and pagination | Separate container and codec controls, eight reused entry widgets, search, pagination and local capability redetection |
| 8-bit / EXR16 intermediate paths | Lossless MOV for ordinary external output; EXR16 for higher-precision workflows, with audio still added during final assembly |
| Controlled source and resolution | Follows source references and takes over related output dimensions, then restores recorded state when released or deleted |
| Repeatable-start adaptation | The companion code-rain project uses a fixed start/seed and fixed-step progression; third-party sources can provide a Reset DAT |
| Cancellation and recovery | Distinguishes active cancellation from completed jobs, preserves intermediate material on cancellation/failure and cleans up on success as documented |

## Audio without a manual alignment pass

Frame-range renders can now include an audio track. The component calculates the required sample range, creates a 16-bit PCM WAV intermediate and mixes it into the finished video.

| Mode | Audio source requirement |
|---|---|
| Frame-range rendering | A **non-time-sliced** CHOP containing the complete data, such as a Wave CHOP, Script CHOP or cached recording |
| Real-time recording | An audio CHOP with **Time Slice** enabled |

On the tested TD 2025.31550 build, Audio File In CHOP remained time-sliced even when its Time Slice parameter was disabled. Convert or cache it before using it for offline rendering. Resampling, time/pitch manipulation and multi-track mixing are not included.

The native MOV/ProRes path can copy the video stream while adding PCM; external paths use FFmpeg. In the existing native MOV/ProRes host test, the decoded audio impulse landed at the expected sample with **zero-sample offset**.

## Formats and workflow

The catalog covers MP4, MOV, MKV, WebM, AVI, MXF, MPEG/MPG, MPEG-TS, FLV, WMV/ASF and GIF, with configurations for H.264, HEVC, AV1, VP8/VP9, ProRes, DNxHR, CineForm, Hap, FFV1 and more.

See the **[format catalog](FORMAT_CATALOG.md)** for compatibility, quality tiers and precision details. Detecting a codec does not mean every hardware, source and parameter combination has been validated.

<p align="center">
  <a href="preview/编码器搜索.png"><img src="preview/编码器搜索.png" alt="RenderStudio native codec search and pagination" width="800"></a>
  <br>
  <sub>Native codec search and pagination. This is not a claim that every configuration was individually clicked through the UI.</sub>
</p>

## Validation and boundaries

| Evidence layer | Passed | Scope |
|---|---|---|
| TD host execution | **9/9** 1.3 offline-audio cases | Native/external paths, single frame, short-source silence padding, EXR16, cancellation and mode-specific rejection |
| Pure rules | **25/25** | Audio planning, synthesis and validation plus existing naming/range rules |
| Actual decoding | **39** 1.2 codec configuration samples | Reused evidence from the same source modules; not rerun for 1.3 and not a full cross-product |
| Native UI | Real-pointer search, pagination, container selection and panel checks | Not a claim of exhaustive per-item mouse testing |
| Release identity | TOX/TOE hashes, source members and downloaded bytes checked | Release assets and the v1.3.0 tag verified at their respective layers |

**Not covered:** Windows, older TD versions, long-form stress tests, a full disk, every resolution/color/alpha combination, or complete broadcast-delivery certification. A 16-bit intermediate does not configure HDR color or metadata automatically.

Read the **[test report](TEST_REPORT.md)** for methodology and limitations, or the **[structured test summary](TEST_SUMMARY.json)** for machine-readable results.

## Documentation

- **[中文说明](README.md)** — 中文安装、工作流与验证边界
- **[Format catalog](FORMAT_CATALOG.md)** — containers, codecs, tiers and compatibility
- **[Changelog](CHANGELOG.md)** — version and documentation changes
- **[Test report](TEST_REPORT.md)** — host evidence, performance scope and uncovered cases
- **[Maintainer source notes](source/README.md)** — module responsibilities and maintenance entry points
- **[Original author declaration](原作者声明.txt)** — attribution, personal/non-commercial use and commercial authorization
- **[Launch kit / 宣发文案](PROMOTION.md)** — bilingual copy for sharing the project

## Who it is for

- Creators turning code-rain or other TouchDesigner visuals into deliverable video.
- TD users who want audio assembled with frame-range renders instead of aligned manually afterwards.
- Artists and technical directors who prefer a native panel for format, speed, precision, cancellation and recovery workflows.

If RenderStudio helps your workflow, a star or a share with another TouchDesigner creator is appreciated. For bug reports, include your **TD build, OS, source type, format configuration, a short sample and reproducible steps**.

## Attribution and permitted use

The original component was **SkyFengStudio_MovieFileOut_2023X_RC** by **SkyFeng Studio**. This is a personal continuation based on the discontinued version, **not an official SkyFeng release**.

The original attribution, declaration and disabled archive are preserved. Under the original declaration, use is limited to personal or non-commercial purposes; commercial use requires authorization from SkyFeng. Public repository visibility does not grant a broader license. The complete terms remain in the **[original author declaration](原作者声明.txt)**.
