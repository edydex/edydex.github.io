#!/usr/bin/env python3
"""Prepare a public supporting report from synthetic benchmark evidence.

Run in the original workspace with --source-root. No live services are contacted.
The published edition omits unrelated application acceptance records and host
process/configuration dumps. Prompts, answers, grades and timings remain intact.
"""
from pathlib import Path
import argparse,hashlib,html,json,re,shutil,zipfile
p=argparse.ArgumentParser();p.add_argument('--source-root',required=True,type=Path);args=p.parse_args()
root=args.source_root;site=Path(__file__).resolve().parents[1];out=site/'src/evidence/qwen-strata-2026-10-22'
source=root/'docs/benchmarks/qwen-strata-2026-10-22'
out.mkdir(parents=True,exist_ok=True)
# Known synthetic input/request records and frozen methods; no application integration directory.
for folder in ['inputs','requests']:
 shutil.copytree(source/folder,out/folder,dirs_exist_ok=True)
for name in ['workflow-content-audit.json','speed.json','warmups.json','excluded-exploration.json']:
 target=out/'records'/name;target.parent.mkdir(exist_ok=True);shutil.copy2(source/'records'/name,target)
(out/'methods').mkdir(exist_ok=True)
for name in ['compare-local-models.py','blind-local-model-review.py','report-local-model-comparison.py']:
 shutil.copy2(source/'methods'/name,out/'methods'/name)
for name in ['local_ai_runtime.py','qwen-27b-manifest.json']:
 (out/'methods'/name).unlink(missing_ok=True)
a=json.loads((source/'records/results.json').read_text())
original_sha=hashlib.sha256((source/'records/results.json').read_bytes()).hexdigest()
# Keep evaluation data and aggregate resource observations, omit unrelated process trees and local deployment verification.
public=json.loads(json.dumps(a));public['visibility']='public supporting evidence'
public.pop('finalVerification',None)
for model in public['models'].values():
 model.pop('speedMemoryReceipts',None)
(out/'records/results.json').write_text(json.dumps(public,indent=2,ensure_ascii=False)+'\n')
# Reuse the full question/answer cards and established methodology, with an explicit public-edition notice.
s=(source/'index.html').read_text()
s=s.replace('INTERNAL · 22 OCTOBER 2026 · COMPLETE SUPPORTING EVIDENCE','22 OCTOBER 2026 · COMPLETE SUPPORTING EVIDENCE')
s=s.replace('No public post has been published.','Public edition accompanying the article on mayos.dev.')
s=s.replace('Internal supporting evidence for a possible future article.','Supporting evidence for the article on mayos.dev.')
s=re.sub(r'<h2>Later application integration</h2><p>.*?</p>','',s,flags=re.S)
s=s.replace('<a href="records/results.json">Results archive</a>','<a href="records/results.json">Evaluation archive</a> · <a href="/blog/flash-next-local-benchmark/">Back to article</a>')
# Standalone report keeps local inline filtering; blog navigation needs no JavaScript.
s=s.replace('Results stay internal; no blog or public post has been published.','This public edition accompanies the published article.')
s=s.replace('The later authorized production cutover is separate from these frozen trial results.','Later application deployment is outside this public report.')
s=s.replace('The later production rollout installs a pinned full validator.','')
s=s.replace('The later authorized production cutover is separate from these frozen trial results.','')
s=re.sub(r'<p>Home-PC portability is untested\..*?</p>','',s,flags=re.S)
s=s.replace('Other desktop applications and VMs remained.','Other desktop applications and VMs remained.')
notice='<aside style="padding:16px;border:1px solid #bdc9d8;background:#fff"><strong>Public supporting edition.</strong> All 87 scored prompts, 174 objective answers, five review tasks and all original/retry review answers are preserved, alongside the rubrics and 18 follow-up speed answers. Unrelated application integration records and host process dumps are omitted. Original strict grades remain frozen; the separate content audit credits both workflow sets at 24/24. Paths in method snapshots are generalized; recorded protocol hashes identify original snapshots, while manifest.json hashes the public files. <a href="publication.json">Publication provenance</a>.</aside>'
s=s.replace('<h2>Results at a glance</h2>',notice+'<h2>Results at a glance</h2>')
(out/'index.html').write_text(s)
# Public GPU appendix: exact test messages/answers plus summary/settings. Resource trees are internal-only.
gpu=out/'gpu-comparison';gpu.mkdir(exist_ok=True)
for name in ['summary.json','conclusion.txt','single.requests-and-answers.json','dual-control.requests-and-answers.json','single.profile.json','dual-control.profile.json','single.placement-and-cache.txt','dual-control.placement-and-cache.txt']:
 source_file=source/'gpu-comparison'/name
 if source_file.exists():shutil.copy2(source_file,gpu/name)
# This appendix's concise public page provides every sample and links to the integrated paired answers.
g=json.loads((gpu/'summary.json').read_text())
rows=''.join('<tr>'+''.join('<td>'+x+'</td>' for x in [f'{one["inputTokens"]:,}',f'{one["generationTokensPerSecond"]:.1f}',f'{two["generationTokensPerSecond"]:.1f}',f'{one["replySeconds"]:.2f}',f'{two["replySeconds"]:.2f}'])+'</tr>' for one,two in zip(g['single'],g['dualControl']))
(gpu/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Flash-Next: one GPU versus two</title><style>body{max-width:900px;margin:40px auto;padding:20px;font:16px/1.7 system-ui;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}td,th{padding:10px;text-align:left;border-bottom:1px solid #ccc}.table{overflow:auto}a{color:#1761ad}</style><h1>Flash-Next: one GPU versus two</h1><p>Same model, quantization, 128K context and settings; GPU selection changed. Three warm samples per input, 128 output tokens, thinking off, no cached prompt tokens. Run order: GPU 0, then a fresh two-GPU control.</p><div class="table"><table><tr><th>Input tokens</th><th>1 GPU tokens/s</th><th>2 GPU tokens/s</th><th>1 GPU reply seconds</th><th>2 GPU reply seconds</th></tr>'+rows+'</table></div><p>Small sequential sample with an adapting expert cache; single-GPU accuracy and long reasoning were not retested. The slow second slot’s effect was not isolated.</p><p><a href="../index.html#gpu-tests">All nine paired speed requests and 18 retained answers</a> · <a href="summary.json">Summary, sample ranges and aggregate resources</a></p><p><a href="single.requests-and-answers.json">Single-GPU exact calls</a> · <a href="dual-control.requests-and-answers.json">Two-GPU exact calls</a></p><h2>Conclusion</h2>'+''.join('<p>'+html.escape(x)+'</p>' for x in (gpu/'conclusion.txt').read_text().split('\n\n'))+'</html>')
# Markdown edition retains all questions/answers; unrelated later acceptance and speculative home-PC prose are excluded.
md=(source/'README.md').read_text()
md=md.replace('Internal supporting evidence for a possible future article.','Public supporting evidence for the article on mayos.dev.')
md=re.sub(r'## Later application integration checks\n.*?(?=## |\Z)','',md,flags=re.S)
md=re.sub(r'Home-PC portability is untested\..*?\n\n','',md,flags=re.S)
md=md.replace('Results stay internal; no blog or public post has been published.','This public edition accompanies the published article.')
(out/'README.md').write_text(md)
# Generalize filesystem identities in surrounding methods/metadata, without touching candidate answers or prompt records.
for f in out.rglob('*'):
 if f.is_file() and f.suffix in ['.py','.md','.html','.txt']:
  t=f.read_text();t=t.replace('/home/pfr/GitHub/pfr_it','/path/to/workspace').replace('/home/pfr/.config','/path/to/config');f.write_text(t)
publication={'edition':'public supporting evidence','date':'2026-10-22','originalResultsJsonSha256':original_sha,'originalResultsRetainedPrivately':True,'changes':['Omitted unrelated application integration checks, application runtime helpers and host process dumps.','Generalized local filesystem roots in method snapshots and surrounding prose.','Removed speculative home-PC portability discussion from this experiment.','Candidate prompts, final answers, recorded grades, timings, source anchors and rubric are unchanged.','Separate post-hoc workflow content audit is included; original exact-field grades remain intact.'],'sourceRepositories':{'mayo':'https://github.com/edydex/edydex.github.io','strata':'https://github.com/Niko1221/Strata'},'lawDatasetAttribution':a['publicLawAttribution']}
(out/'publication.json').write_text(json.dumps(publication,indent=2,ensure_ascii=False)+'\n')
manifest={'edition':'public','objectiveCases':87,'objectiveAnswers':174,'reviewCases':5,'reviewAttempts':12,'gpuFollowupSpeedSamples':18,'rawReasoningIncluded':False,'files':{str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.rglob('*')) if f.is_file() and f.name!='manifest.json'}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(out.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(out.parent))
# Import the reviewed short article into the new site's shared layout.
blog=(root/'docs/blog/flash-next-local-benchmark/index.html').read_text()
body=blog.split('</header>',1)[1].split('<footer>',1)[0]
body=body.replace('assets/','/assets/benchmark/').replace('../../benchmarks/qwen-strata-2026-10-22/gpu-comparison/index.html','/evidence/qwen-strata-2026-10-22/gpu-comparison/')
header='''---
layout: post.njk
title: "Qwen 27B vs Flash-Next on RTX 5060 Ti GPUs"
description: "A local AI experiment: two models, one borrowed GPU, and a surprisingly capable single-card setup."
date: 2026-10-22
readingTime: 3 min read
tags: [post]
topics: [local AI, benchmarks, self-hosting]
permalink: /blog/flash-next-local-benchmark/index.html
---
'''
(site/'src/blog/flash-next-local-benchmark.njk').write_text(header+body)
shutil.copytree(root/'docs/blog/flash-next-local-benchmark/assets',site/'src/assets/benchmark',dirs_exist_ok=True)
# Confirm objective/review evidence survived publication preparation exactly.
for model in ['qwen','strata']:
 for key in ['objective','speed','reviewOriginal','reviewPairedRetry']:
  assert public['models'][model][key]==a['models'][model][key],(model,key)
print(json.dumps({'publicFiles':len(manifest['files']),'objectiveAnswers':174,'reviewAnswers':12,'publicArchiveBytes':out.with_suffix('.zip').stat().st_size}))
