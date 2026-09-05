# PAR2 worker recovery and cleanup — 2026-09-05

All disposable PAR2 worker VMs were frozen, exported, verified byte-for-byte and
then deleted. The three allowlisted instances were never touched.

## Workers recovered

| Worker | Zone | Archive bytes | SHA-256 (source = destination) | Pose shards | Sentinels |
|---|---|---:|---|---:|---:|
| par2w3 | europe-west4-b | 21,050,184 | `89e7a578a96c4ace1fac32b7cd174b0bc0f55c5847431b9ae1007e1d10130b29` | 98 | 98 |
| pw-c3a | europe-west4-b | 18,131,069 | `498429742a43e39bc58aa3b4510bc57de678424c8c8130048051fe31c187d43f` | 67 | 67 |
| pw-h3b | us-central1-a | 18,522,859 | `33215d81ac43ff459349b6914b54da59f97c441a9b7414244b8090bced8fd42a` | 74 | 74 |
| pw-n2a | europe-west4-b | 16,344,502 | `31b6193187a6836508603af72216ca82d9d83ca50777af78757346b1499f4aff` | 43 | 43 |

Total 74,048,614 bytes pulled, 282 pose shards, 282 `.done` sentinels,
367 MB on disk after extraction.

## Integrity

Every archive's SHA-256 computed on the worker matches the SHA-256 computed on
the destination Mac, and byte counts match exactly. Archives were re-extracted
and path counts reconciled against `tar tzf` entry counts. **PASS for all four.**

No git checkout existed on any worker: they received only the shard payload,
the receptors/configs and `v2_run_screen.sh`. No source code was modified on a
worker, so no uncommitted code was lost.

## Unique data recovered

50 pose shards had never been merged into the 2026-09-04 analysis — roughly
1,250 additional ligand-pocket docking results, all from the previously
unfinished portion of the library. They are preserved but were **not** folded
into the committed rankings, which therefore still describe the 11,485-design
universe of commit `f342a8d`.

## Data lost

`pw-n2b` (us-central1-a) had already been deleted before this cleanup began,
together with its auto-delete boot disk. Its post-14:45 output is unrecoverable.
The partial export pulled from it at 14:45 on 2026-09-04 survives in the working
scratchpad and is included in the merged analysis.

## Where things are

- Raw archives and extracted trees: `PAR2_WORKER_RECOVERY_2026-09-05/<worker>/`
  on the local Mac (sibling of the repository, deliberately not committed).
- De-duplicated pose shards: `PAR2_WORKER_RECOVERY_2026-09-05/ALL_UNIQUE_POSES/`.
- Committed here: per-worker manifests and the 282 shard sentinels, which carry
  each shard's input/output SHA-256, return code, wall time and GNINA parameters.

## Instances

Deleted: `par2w3`, `pw-c3a`, `pw-h3b`, `pw-n2a`.
Preserved and untouched: `a100`, `a100-40`, `h3` — all TERMINATED, none started
by this cleanup beyond the four workers, which were started only to export data.

No scientific compute was launched: no docking, PIGNet2, Boltz, MD or EX32.
