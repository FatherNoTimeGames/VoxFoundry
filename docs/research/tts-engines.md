# Local TTS engine evaluation

Reviewed 2026-10-29 against primary upstream documentation/source, not installed models.
**Recommendation: Kokoro first integration candidate; Chatterbox original English and
Turbo as expressive listening-test alternatives. No production voice selected.**
The revised mission is personal use. The earlier commercial-default constraint is
superseded; commercial/noncommercial restrictions still matter per model and output
use. Personal use does not waive voice/source rights or checkpoint terms. Every model
download still requires separate exact-artifact/size/license/purpose approval. Piper is a potential
low-resource fallback after licensing review. F5-TTS and XTTS are research-only until
weight terms and intended use are resolved. CosyVoice is a later control-rich candidate.

## Evidence and limits

“Documented” below means primary documentation/source describes a capability; it does
not mean VoxFoundry tested it. Quality descriptions are hypotheses for listening
comparisons. Upstream speed/quality claims are not our benchmarks. No weights,
voices, reference recordings, or inference dependencies were downloaded. No audio
was generated or listened to, and no engine ran on Windows, RTX 3060, or CPU here.

GitHub raw sources were accessible. Requests to Hugging Face model cards were denied
by the environment proxy (403); no bypass attempted. The upstream Kokoro README's
Apache-weight statement is available, but exact model/voice card review is pending.
XTTS documentation links CPML; its full current weight terms were not retrieved.
This limits redistribution conclusions, not the architectural recommendation.
No network-policy change is needed for this documentation phase. Future approved
model installation needs the exact hosting/CDN destinations checked and configured
through environment settings as applicable.

## Comparison: voice and production controls

| Engine / variant | Documented capability | Audiobook hypothesis and risk; unverified |
| --- | --- | --- |
| Kokoro-82M | 82M parameters; preset voice tensors; English US/UK and additional languages; `speed`, text splitting, Misaki G2P, 24 kHz output; README phoneme override example [K1]; pipeline CPU/CUDA selection [K2] | Good lightweight baseline for documentary narration. Fixed voice identities may aid consistency; expressive direction and zero-shot cloning are not established API features. Repeated names and paragraph joins need testing. Phoneme adaptation must preserve original script. |
| Chatterbox original English (500M) | Zero-shot reference voice; exaggeration and CFG controls; CPU/CUDA examples [C1] | Strong expressive comparison candidate; reference clip and settings can change pacing/accent. Generative omissions/repetitions and narrator drift must be checked over chapters. No guaranteed exact rate or general phoneme API. |
| Chatterbox Turbo (350M), Nano (110M) | Turbo reference-cloning and paralinguistic tags; single-step decoder; Nano same API and documented CPU option. Current README also describes 500M Multilingual V3 [C1] | Turbo worth testing for English narrative throughput/quality; tags may suit dialogue rather than documentary. Do not assume original-model exaggeration controls apply to Turbo. Nano is a low-resource alternative, not a measured quality equivalent. Multilingual unnecessary for first English production. |
| F5-TTS v1 Base | Reference audio + transcript, chunk inference, multi-style/speaker workflow, duration/chunk constraints in inference docs [F1,F2] | Promising cloned narrator style; context/chunk seams and reference quality require listening. Supplied reference transcript avoids implicit ASR download/extra GPU memory. Noncommercial pretrained weights prevent recommending unrestricted general-purpose distribution. |
| Maintained Piper (`OHF-Voice/piper1-gpl`) | Local neural TTS, espeak-ng, ONNX voice models; length/noise/volume controls, streaming chunks, optional ONNX CUDA [P1,P2] | Predictable low-resource fallback candidate. Voice quality varies; limited expressive control versus generative cloning candidates. No documented turnkey zero-shot cloning. Phoneme-level controls need further adapter investigation. |
| XTTS-v2 via maintained idiap/coqui-ai-TTS | Reference cloning, multilingual generation, 24 kHz, streaming, conditioning reuse [X1] | Useful historical comparison for stable cloned narrator. Not initial default: CPML model terms need review and packaging is heavier. CPU path and long-form quality not validated here. |
| Fun-CosyVoice 3.0 (0.5B) | Zero-shot/cross-language cloning, instruction controls, pronunciation inpainting (English CMU/Chinese Pinyin), streaming [Y1] | Attractive advanced pronunciation/emotion candidate. More deployment complexity; upstream multilingual/short-latency claims do not prove Windows English audiobook quality or stable hour-long narration. |

## Hardware, speed and installation

An RTX 3060 name alone does not specify VRAM (desktop/mobile variants exist). Detect
actual memory, driver and compute support. Model parameter counts do **not** equal
runtime VRAM or total download size: include vocoder, tokenizer, voice/reference
encoders, framework and caches. The following are planning judgments, not guarantees.

| Engine | Documented execution / dependency facts | RTX 3060 / resource and speed assessment |
| --- | --- | --- |
| Kokoro | PyTorch, Misaki, soundfile; espeak-ng fallback; Windows MSI guidance; pipeline supports CPU and CUDA [K1,K2] | Most conservative first candidate by model size. Likely feasible on CPU and 3060; peak RAM/VRAM and real-time factor (RTF) unknown. Need warm/cold runs and Windows phonemizer installation test. |
| Chatterbox | README tested environment Python 3.11/Debian 11; current package source pins torch/torchaudio, transformers/diffusers and references Perth at moving Git master [C1,C3] | Isolate its environment, freeze transitive Git ref before adoption. GPU feasibility plausible, not established on 6/8/12 GB variants. Nano README claims 3× real-time on 8 CPU cores; hardware unspecified, not a VoxFoundry result. Turbo is advertised as lower VRAM/compute, with no reliable 3060 figures established here. |
| F5 | Python >=3.10, matched torch/torchaudio CUDA wheels, FFmpeg; optional vocoder/ASR and TensorRT paths [F1] | Upstream L20 benchmark RTF 0.1467 PyTorch and 0.0394 client-server accelerated configuration are not transferable to 3060 or CPU. Avoid TensorRT complexity initially. Exact VRAM/CPU throughput unknown. |
| Piper | `piper-tts`, ONNX voice+config; `use_cuda=True` needs onnxruntime-gpu [P2] | CPU-first candidate; GPU optional. Per-voice size and quality vary. No measured RTF/VRAM here. Test current Windows wheels rather than assuming archived Piper compatibility. |
| XTTS | Maintained fork documents CUDA use and reference conditioning reuse; CPU operation not established by the reviewed examples [X1] | Expected heavier than Kokoro; no validated GPU budget or CPU throughput. Avoid treating upstream streaming latency as full audiobook generation speed. |
| CosyVoice | Source installation, additional model components and optional optimized runtimes [Y1] | Higher integration/maintenance cost; native Windows and CPU practical feasibility unverified. Exclude accelerated server stack from initial product. |

Maintenance evidence: sources were reachable on review date; this is not a support
commitment or a quantified activity audit. Piper explicitly advertises a search for
maintainers [P1]. Chatterbox's moving Git dependency and changing model family warrant
pinning and revalidation. Prefer maintained projects over abandoned forks, but
re-evaluate release activity/security and wheel availability when integrating.

## Licensing and redistribution gates

| Engine | Code evidence | Weights / voices / dependencies and distribution consequence |
| --- | --- | --- |
| Kokoro | Apache-2.0 code [K3] | README says Apache-licensed weights [K1]. Exact pinned weights and each voice card still need verification; phonemizer/Misaki/espeak-ng dependencies have separate obligations. Tentatively most suitable permissive baseline, not blanket clearance. |
| Chatterbox | MIT [C2] | Repository describes an open-source family, but MIT code alone does not establish every variant's checkpoint terms. Verify each exact weight/tokenizer/vocoder/reference asset. Built-in Perth watermarking is documented [C1]; preserve provenance, do not promise removable watermarks. |
| F5 | MIT code [F3] | Upstream explicitly states CC-BY-NC pretrained models due to Emilia data [F1]. “Free application” does not resolve commercial production rights. Not a bundled/default model without resolved intended-use terms. |
| Piper | GPL-3.0 text in COPYING [P3] | Voice models have separate licenses; verify each voice card and training-source conditions. GPL obligations require distribution review; a subprocess boundary alone is not a license exemption. Do not inherit old Piper repository's license assumption. |
| XTTS | Maintained fork code MPL-2.0 [X2] | Model docs specify Coqui Public Model License [X1]; full terms not reviewed here. Treat commercial/output/redistribution permissions as unresolved. |
| CosyVoice | Apache-2.0 repository license [Y2] | This does not independently clear every checkpoint and auxiliary model. Verify exact model cards and dependency notices before approval. |

Record a model bill of materials before **each** approved download: exact repository
and revision, artifacts and total compressed/installed size, SHA-256 checksums, code
and weight/voice licenses, attribution/source obligations, purpose, expected RAM/VRAM,
reference-audio rights, offline loading path, and removal/update behavior. Parameter
counts above are not download size estimates. No substantial downloads are authorized
by this research recommendation. Project source license also remains a user decision.

## Listening and compatibility trial (future P3-01)

1. Use licensed/producer-owned reference speech. Start with Kokoro US/UK preset
   candidates, Chatterbox original and Turbo with one consistent reference. Add
   Piper only after license review; add F5 only after intended-use clearance.
2. Freeze a shared English test corpus: neutral documentary prose, emotional passages,
   dialogue/quotation, dates/numbers, abbreviations, fantasy proper names (including
   Embervale), long sentences and chapter transitions. Do not invent production lore.
3. Blind/randomize engine labels and loudness-match preview copies. Keep raw audio,
   exact text, reference digests, settings, seeds and model revisions. Score 1–5 for
   naturalness, expressiveness, pronunciation, intelligibility, fatigue, voice identity
   and seam quality. Record omissions/repetitions separately; do not average them away.
4. Compare 2–5 minute excerpts, then a repeated 20-minute chapter, then the Phase 3
   60-minute recovery run. Producer approves voice/style; no automatic quality winner.
5. Measure cold startup, warm RTF (= wall time / output duration), peak RAM/VRAM,
   disk/download size, failed segments and regeneration rate, separately on actual
   Windows 10 + available RTX 3060 and CPU. Record OS/driver/CPU/GPU/VRAM, concurrency,
   precision and versions. CPU fallback may be slower; publish measurements honestly.
6. Kill worker/service mid-write, cancel/retry, exhaust disk and deny network after
   explicit install. Verify recovery, complete segment coverage, unchanged cached
   artifacts and no network requirement. Choose production engine only after listening,
   compatibility, license and recovery gates pass.

## Primary sources

All links below were retrieved 2026-10-29 from upstream GitHub raw equivalents unless
stated otherwise. Branch URLs are mutable; source-response hashes are recorded below
for the core TTS evidence. Recheck and pin release commits at adoption.

- K1: [Kokoro README](https://github.com/hexgrad/kokoro/blob/main/README.md)
- K2: [Kokoro pipeline source](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py)
- K3: [Kokoro license](https://github.com/hexgrad/kokoro/blob/main/LICENSE)
- C1: [Chatterbox README](https://github.com/resemble-ai/chatterbox/blob/master/README.md)
- C2: [Chatterbox license](https://github.com/resemble-ai/chatterbox/blob/master/LICENSE)
- C3: [Chatterbox dependencies](https://github.com/resemble-ai/chatterbox/blob/master/pyproject.toml)
- F1: [F5-TTS README and weight-license statement](https://github.com/SWivid/F5-TTS/blob/main/README.md)
- F2: [F5-TTS inference guide](https://github.com/SWivid/F5-TTS/blob/main/src/f5_tts/infer/README.md)
- F3: [F5 code license](https://github.com/SWivid/F5-TTS/blob/main/LICENSE)
- P1: [Maintained Piper README](https://github.com/OHF-Voice/piper1-gpl/blob/main/README.md)
- P2: [Piper Python API](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md)
- P3: [Piper COPYING](https://github.com/OHF-Voice/piper1-gpl/blob/main/COPYING)
- X1: [XTTS documentation in maintained fork](https://github.com/idiap/coqui-ai-TTS/blob/dev/docs/source/models/xtts.md)
- X2: [Maintained fork code license](https://github.com/idiap/coqui-ai-TTS/blob/dev/LICENSE.txt)
- Y1: [CosyVoice README](https://github.com/FunAudioLLM/CosyVoice/blob/main/README.md)
- Y2: [CosyVoice license](https://github.com/FunAudioLLM/CosyVoice/blob/main/LICENSE)

Unavailable primary model cards: [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)
and [XTTS-v2](https://huggingface.co/coqui/XTTS-v2) returned proxy 403. These URLs
are follow-up references, not evidence claimed as read.

### Retrieved response fingerprints

SHA-256 of retrieved response bytes, retained as evidence fingerprints (not model
checksums or guarantees about future branch content). Labels follow source order
K1–K3, C1–C3, F1–F3, P1–P3, X1–X2, Y1–Y2.

| Source | SHA-256 |
| --- | --- |
| K1 | `b50b84220668f8247a2405b249c34c7083acc24114279ff1429fd79f46a2c04b` |
| K2 | `499982bbc23a1019681cdb4c327c1d911e7034e240721b95686ff1a8f15c2a9a` |
| K3 | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` |
| C1 | `fd9315cc529c65d46ddd21ded05ba3372b6f6f39242bd015f770145bf5e0448f` |
| C2 | `4248e910a928849fe5815a0f9236e17fa07768d95b9193212752c464b93d6caa` |
| C3 | `e1aab210e1eb6023a694a05e92ae4cbb08efa9510d295401303e90eec41d594f` |
| F1 | `3c74da9760857de03a0fe22d6124fd50000b986c6aeba6c23bb14635e20e4ae1` |
| F2 | `fcd421b40b1c0c769325f280ebb385ca469c0bf4903117324cab1c3c5ebe48d6` |
| F3 | `c70811d1402134de900e811d3eaa349eb60f4d38a8f635b27b1e378c630facd2` |
| P1 | `a73f576020071a1d58701a40026a451385ef4dad4c9ba0a2499544d988d06e84` |
| P2 | `734acd1cbcbb971c03746d818e91baef1d0a540fee2c462d1be3a50ef4ed8bde` |
| P3 | `0ae0485a5bd37a63e63603596417e4eb0e653334fa6c7f932ca3a0e85d4af227` |
| X1 | `393f4a649b62c4594a9bc53670b8e6574c1ed59b4b7896f4259dc2a77f5ee1b9` |
| X2 | `1f256ecad192880510e84ad60474eab7589218784b9a50bc7ceee34c2b91f1d5` |
| Y1 | `66436370172c2830ed98aa643b31898c65e16eee14ade68f00828d21fae602e0` |
| Y2 | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` |

## Revised Sites + Windows worker context

Reuse the primary-source evidence above; do not rerun unrelated downloads. No engine
ran on RTX 3060 or Windows and no listening trial occurred. Kokoro remains the first
lightweight candidate, Chatterbox the expressive comparison. F5's noncommercial weights
may be compatible with the personal-use goal only after exact terms/reference rights
are checked; no blanket clearance is granted. Piper GPL and per-voice terms, XTTS
model terms and all redistribution/attribution obligations remain separate gates.
The new disposable transport POC uses a deterministic tone generator with Python's
standard library, not a TTS engine; it validates neither narration quality nor GPU
performance. No model downloads or significant dependency installs were performed.
