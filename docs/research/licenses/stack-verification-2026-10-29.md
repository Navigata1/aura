# T01 stack license verification — 2026-10-29

This records primary-source code-license checks for selected foundation pins and planned prefactor components. It is an engineering interpretation of the license texts, not legal advice. It is not a model-license acceptance, an owner act, a complete binary SBOM, or evidence of runtime compatibility. No weights were downloaded.

All retrieved text was saved on STUDIO outside the repository. The source manifest records exact version, URL, license-text SHA-256, and archive hash/member when extracted from an official package archive. Repository notes do not vendor upstream license text or personal contact details.

| Component | Pin | Source license | Source |
|---|---|---|---|
| react | 19.3.1 | MIT | [Primary source](https://raw.githubusercontent.com/react/react/v19.3.1/LICENSE) |
| react-dom | 19.3.1 | MIT | [Primary source](https://raw.githubusercontent.com/react/react/v19.3.1/LICENSE) |
| vite | 8.3.5 | MIT | [Primary source](https://raw.githubusercontent.com/vitejs/vite/v8.3.5/LICENSE) |
| vitest | 5.0.5 | MIT | [Primary source](https://raw.githubusercontent.com/vitest-dev/vitest/v5.0.5/LICENSE) |
| typescript | 7.0.2 | Apache-2.0 | [Primary source](https://raw.githubusercontent.com/microsoft/TypeScript/v7.0.2/LICENSE.txt) |
| playwright | 1.64.1 | Apache-2.0 | [Primary source](https://raw.githubusercontent.com/microsoft/playwright/v1.64.1/LICENSE) |
| uv | 0.11.8 | MIT | [Primary source](https://raw.githubusercontent.com/astral-sh/uv/0.11.8/LICENSE-MIT) |
| uv-build | 0.11.8 | MIT | [Primary source](https://raw.githubusercontent.com/astral-sh/uv/0.11.8/LICENSE-MIT) |
| pnpm | 11.1.2 | MIT | [Primary source](https://raw.githubusercontent.com/pnpm/pnpm/v11.1.2/LICENSE) |
| pytest | 9.2.0 | MIT | [Primary source](https://raw.githubusercontent.com/pytest-dev/pytest/9.2.0/LICENSE) |
| fastapi | 0.162.0 | MIT | [Primary source](https://raw.githubusercontent.com/fastapi/fastapi/0.162.0/LICENSE) |
| starlette | 1.10.0 | BSD-3-Clause | [Primary source](https://raw.githubusercontent.com/Kludex/starlette/1.10.0/LICENSE.md) |
| uvicorn | 0.54.0 | BSD-3-Clause | [Primary source](https://raw.githubusercontent.com/Kludex/uvicorn/0.54.0/LICENSE.md) |
| pydantic | 2.14.2 | MIT | [Primary source](https://raw.githubusercontent.com/pydantic/pydantic/v2.14.2/LICENSE) |
| mlx | 0.32.4 | MIT | [Primary source](https://raw.githubusercontent.com/ml-explore/mlx/v0.32.4/LICENSE) |
| numpy | 2.5.4 | BSD-3-Clause | [Primary source](https://raw.githubusercontent.com/numpy/numpy/v2.5.4/LICENSE.txt) |
| scipy | 1.18.1 | BSD-3-Clause | [Primary source](https://raw.githubusercontent.com/scipy/scipy/v1.18.1/LICENSE.txt) |
| soundfile | 0.14.0 | BSD-3-Clause | [Primary source](https://raw.githubusercontent.com/bastibe/python-soundfile/0.14.0/LICENSE) |
| libsndfile | 1.2.2 | LGPL-2.1-or-later | [Primary source](https://raw.githubusercontent.com/libsndfile/libsndfile/1.2.2/COPYING) |
| types-react | 19.3.0 | MIT | [Primary source](https://registry.npmjs.org/@types/react/-/react-19.3.0.tgz) |
| types-react-dom | 19.3.0 | MIT | [Primary source](https://registry.npmjs.org/@types/react-dom/-/react-dom-19.3.0.tgz) |
| sqlite | Python-linked runtime version checked at adoption | Public domain dedication | [Primary source](https://www.sqlite.org/copyright.html) |
| keyring | 25.7.0 | MIT | [Primary source](https://files.pythonhosted.org/packages/43/4b/674af6ef2f97d56f0ab5153bf0bfa28ccb6c3ed4d1babf4305449668807b/keyring-25.7.0.tar.gz) |
| node | 22.22.3 | MIT with bundled dependency notices | [Primary source](https://raw.githubusercontent.com/nodejs/node/v22.22.3/LICENSE) |
| python | 3.12.13 | PSF-2.0 and historical Python licenses | [Primary source](https://raw.githubusercontent.com/python/cpython/v3.12.13/LICENSE) |

## Boundaries and remaining work

- Foundation pins used by the scaffold are source-verified; the installed control and web dependency inventories must still pass the license allowlist. Root package metadata is not a substitute for every resolved dependency.
- FastAPI, Starlette, uvicorn, Pydantic, keyring, Playwright and worker libraries are verified for the named versions, but remain future adoption choices until their owning tickets pin and test exact environments. No SSE helper is selected.
- The grouped `codegen-tools` row remains UNVERIFIED and research-only: T01 has not chosen third-party generators. Future T04 adoption requires named pinned tools and source checks. Stdlib-based planning is not adoption of an unspecified generator.
- SQLite has a public-domain dedication rather than a conventional SPDX license. Its official page distinguishes deliverable library code from build scripts. Confirm the exact Python-linked version at runtime.
- NumPy and SciPy source licenses do not describe every bundled wheel library. SciPy distributions can include compiler runtimes with LGPL/GPL runtime-exception terms. Keep numerical/audio dependencies out of the control service and browser; inspect actual platform distributions before adoption.
- SoundFile is BSD-3-Clause, while libsndfile is LGPL-2.1-or-later. Both run inside a separate worker. The source header corroborates the or-later grant. Neither is allowed in control or web by the project policy.
- Node is build-time only; its official LICENSE includes bundled dependency notices. No license clearance for redistributing a Node executable is implied. Playwright browser binaries likewise require their own distribution review if packaged.
- License checks do not establish security, acoustics, hardware compatibility, or product quality. Dependencies must still be pinned and checked for advisories before adoption.

## Bounded reconciliation of T01 wording

T01 requires stack-register updates and byte-identical fixture regeneration, while saying existing contracts remain untouched. Two invalid-record fixtures embed a registry snapshot, so both requirements cannot hold literally. No schema or reference behavior changes; the generated component register and `contracts/fixtures/invalid/component-nc-in-process.json` and `contracts/fixtures/invalid/component-nc-in-llc.json` change together. The lead authorized this explicit reconciliation on 2026-10-29 for PR review. No frozen legacy fixture changes.

A separate clean-checkout defect was discovered: `contracts/fixtures/world/store/store.json` is produced by the baseline generator but absent from Git because the broad `store/` ignore pattern excluded it. The local canonical checkout had masked this missing fixture. T01 adds the generated fixture and a narrow ignore exception, so clean CI can reproduce the contract gate.
