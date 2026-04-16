# Sheerwater Skills

Agent skills (Agent Skills standard) that wrap the `sheerwater` CLI.

Each skill is a `SKILL.md` documenting one logical verb against the CLI:

- **Data fetch**: `chirps-fetch`, `imerg-fetch`, `tahmo-fetch`, `ghcn-fetch`,
  `era5-fetch`, `tamsat-fetch`, `rain-over-africa-fetch`, `cbam-fetch`
- **Forecast fetch**: `ecmwf-ifs-fetch`, `fuxi-fetch`, `graphcast-fetch`,
  `gencast-fetch`, `salient-fetch`
- **Ops**: `clip-region`, `regrid`, `aggregate-temporal`
- **Eval**: `evaluate-forecast`, `compare-forecasts`

All skills emit Rhiza Envelope-compliant Zarr stores (see
[forecasting-skills/ENVELOPE.md](../../forecasting-skills/ENVELOPE.md)) so they
compose with other envelope skills.

## Install pattern

The skills' single bin dependency is **`uv`** (declared in each SKILL.md's
`metadata.openclaw.requires.bins`). Sheerwater itself is installed on demand
from PyPI through `uvx`:

```bash
uvx sheerwater@latest <verb> <args>
```

`uvx` resolves the latest published `sheerwater` from PyPI on first call,
caches it, and runs the registered `sheerwater` console script.

### No version pinning

Skills always invoke `sheerwater@latest` rather than a specific version.
The trade-off is intentional, but consumers of these skills need to know it:

- **What we lose:** when a consumer installs a skill (e.g. via
  `skillkit install rhiza-research/sheerwater`), they get a snapshot
  of SKILL.md whose example commands match whatever sheerwater shipped
  at that moment. Later, when sheerwater publishes a release that
  changes the CLI (renamed verbs, removed flags, changed defaults),
  the consumer's next agent run will pull the new sheerwater via
  `uvx sheerwater@latest` but their local SKILL.md snapshot still
  references the old commands. The mismatch breaks the skill at
  runtime. **A pin would have insulated the consumer from this** by
  keeping their agent on the older sheerwater that matched their
  snapshot.
- **What we gain:** one less thing to maintain in this repo. No N-file
  pin bumps per release, no risk of stale pins drifting out of sync.
- **What this requires of consumers:** keep your installed skills
  current with sheerwater. If a sheerwater release breaks a skill you
  have installed, run `skillkit update` to refresh the SKILL.md
  snapshot. The skill is updated in lockstep with the sheerwater
  release in this repo.

## Auth

- Public sheerwater data (`gs://sheerwater-public-datalake/caches`) is readable
  anonymously — `GOOGLE_APPLICATION_CREDENTIALS` is optional for these fetches.
- Private bucket (`gs://sheerwater-datalake/caches`) requires
  `GOOGLE_APPLICATION_CREDENTIALS` set to a GCP service-account JSON.

All fetch and eval skills declare `GOOGLE_APPLICATION_CREDENTIALS` under
`metadata.openclaw.requires.env` (with `primaryEnv` set to the same name). In
the rhiza-agents runtime that field is informational/UX (used for the missing-
credentials chip in the install UI and for the activation hint that tells the
agent which secret name to attach to its `run_file` `credentials` argument). It
does **not** gate skill selection — a user without the credential can still use
public-bucket data because the agent passes credentials per call rather than
having them injected unconditionally.

Ops skills (`clip-region`, `regrid`, `aggregate-temporal`) operate on local
Zarr files only and declare no env requirements.

## Cache management

Cache inspection and management is provided by the `nuthatch` CLI directly.
Sheerwater does not re-export it. See `nuthatch --help`.
