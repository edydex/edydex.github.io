import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const root=path.resolve(import.meta.dirname,'../_site');
const files=[];
function walk(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,entry.name);entry.isDirectory()?walk(p):files.push(p);}}
walk(root);
let links=0;
for(const file of files.filter(f=>f.endsWith('.html'))){
 const source=fs.readFileSync(file,'utf8');
 for(const match of source.matchAll(/(?:href|src)="([^"<>]+)"/g)){
  const url=match[1];if(/^(?:[a-z][a-z\d+.-]*:|\/\/|#)/i.test(url))continue;
  const target=decodeURIComponent(url.split(/[?#]/)[0]);if(!target)continue;
  const resolved=path.resolve(target.startsWith('/')?root:path.dirname(file),target.replace(/^\//,''));
  assert.ok(resolved.startsWith(root+path.sep)||resolved===root,`Link escapes output: ${url}`);
  assert.ok(fs.existsSync(resolved)||fs.existsSync(path.join(resolved,'index.html')),`Broken local link in ${file}: ${url}`);links++;
 }
}
const pub=path.join(root,'evidence/qwen-strata-2026-10-22');
const results=JSON.parse(fs.readFileSync(path.join(pub,'records/results.json')));
assert.equal(results.models.qwen.objective.length,87);assert.equal(results.models.strata.objective.length,87);
const audit=JSON.parse(fs.readFileSync(path.join(pub,'records/workflow-content-audit.json')));
assert.equal(audit.models.qwen.contentCorrect,24);assert.equal(audit.models.strata.contentCorrect,24);
assert.ok(!fs.existsSync(path.join(pub,'integration')));
assert.ok(!fs.readFileSync(path.join(root,'blog/flash-next-local-benchmark/index.html'),'utf8').includes('32 GB home PC'));
console.log(JSON.stringify({files:files.length,localLinks:links,objectiveAnswers:174,workflowContent:'24/24 both',unrelatedIntegrationPublished:false}));
