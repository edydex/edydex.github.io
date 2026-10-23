import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
fs.rmSync(path.join(root,'_site'),{recursive:true,force:true});
const result=spawnSync(process.execPath,[path.join(root,'node_modules/@11ty/eleventy/cmd.cjs')],{cwd:root,stdio:'inherit'});
process.exit(result.status??1);
