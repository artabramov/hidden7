# Hidden — secure S3-compatible object storage

Hidden is S3-compatible object storage for sensitive data on privately
managed infrastructure. Instead of relying on encryption provided by the
S3 layer, it protects the underlying filesystem independently, keeping
stored data encrypted at rest while preserving compatibility with the
S3 ecosystem.

Built with `gocryptfs`, `VersityGW`, and `FastAPI`, the system separates
storage management from the S3 data plane. `VersityGW` handles the S3
API, WebGUI, and IAM, while `FastAPI` manages the `gocryptfs` lifecycle
and encrypted storage state.

Hidden is distributed as a `Docker` image and can run in any compatible
environment. Persistent data is split between two volumes: `cipherdir`
for encrypted storage and a bind-mounted `secrets` volume for internal
secrets. The `secrets` volume can be hosted on removable media or a
separate remote host.

The `cipherdir` is mounted through `gocryptfs` using an encrypted
passphrase stored in `secrets` and unlocked with a `master password`
for each mount. When not mounted, the data remains encrypted and
inaccessible.

Within the encrypted filesystem, `VersityGW` maps S3 objects directly
to regular files and directories alongside IAM data.

For emergency recovery, the `cipherdir` can be mounted directly with
`gocryptfs` using the decrypted passphrase. This exposes the `VersityGW`
data and IAM directories, allowing their contents to be recovered
independently of the application.

## Use cases

Hidden is designed with one primary goal: making data protection the
highest priority. Typical use cases include:

**Private storage** — sensitive or confidential data that must remain
encrypted independently of the storage service itself.

**Internal storage** — protected object storage for teams and
organizations operating on privately managed infrastructure.

**Isolated environments** — storage for infrastructure segments where
external cloud services are unavailable, restricted, or undesirable.

**Backup and archival storage** — encrypted storage for backups,
exports, snapshots, and long-term retention.

## How it works

Decrypted data is available only while the storage is mounted and
remains internal to the application, with external access provided
exclusively through the S3 API.

S3 data and IAM state reside within the mounted encrypted filesystem.
A `watchdog` monitors critical runtime conditions, automatically
unmounting the decrypted data view and stopping the S3 service.

All persistent data and secrets are kept outside the application in
dedicated volumes, making application upgrades, storage migration, and
data recovery straightforward.

```text
        Container                           Container
        Internals                           Externals

┌───────────────────────────┐
│ VersityGW                 │───── S3-compatible API and WebGUI
│ (S3, WebGUI, IAM)         │      provide storage and IAM access
└───────────────────────────┘
              │
┌───────────────────────────┐
│ FastAPI application       │───── REST API provides encrypted
│ (management layer)        │      storage lifecycle management
└───────────────────────────┘
              │
┌───────────────────────────┐
│ gocryptfs mountpoint      │
│ (decrypted data and IAM)  │
└───────────────────────────┘
              │
┌───────────────────────────┐     ┌───────────────────────────┐
│ watchdog                  │-----│ gocryptfs passphrase      │
│ (mount supervisor)        │     │ (detachable secrets)      │
└───────────────────────────┘     └───────────────────────────┘
              │
┌───────────────────────────┐     ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│ gocryptfs engine          │-----┃ gocryptfs cipherdir       ┃
│ (FUSE layer)              │     ┃ (encrypted data and IAM)  ┃
└───────────────────────────┘     ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Project layout

The application code is organized into small packages with distinct
responsibilities. HTTP routes and their dependencies live separately
from application services, while S3-specific logic and IAM are handled
by VersityGW.

Runtime management covers the gocryptfs and VersityGW lifecycles and
watchdog, security handles passphrase encryption and master-password
verification, and dedicated packages contain request and response
schemas and middleware.

```text
app/
├── dependencies/   FastAPI request dependencies
├── middleware/     HTTP middleware
├── pydantic/       Shared Pydantic types and validation
├── routers/        HTTP API routes
├── runtime/        gocryptfs, VersityGW, and watchdog lifecycle
├── schemas/        API request and response schemas
├── security/       Passphrase encryption and password verification
└── services/       Application operations and orchestration
```
