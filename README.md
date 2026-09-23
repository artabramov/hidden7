# Hidden — encrypted self-hosted S3 storage

Hidden is S3-compatible object storage for sensitive data on privately
managed infrastructure. It provides filesystem-level encryption
independently of the S3 layer while maintaining full S3 compatibility.

Built on `gocryptfs` and `VersityGW`, the system combines encrypted
storage with an S3-compatible gateway. `VersityGW` provides the S3 API,
IAM, and WebGUI, while `FastAPI` manages the storage lifecycle through
an OpenAPI interface.

It runs as a `Docker` container with persistent state stored in two
volumes: `cipherdir` for encrypted data and a bind-mounted `secrets`
volume for internal secrets. The `secrets` volume can reside on
removable media or a separate remote host.

The `cipherdir` is mounted through `gocryptfs` using an encrypted
passphrase stored in `secrets` and unlocked with a `master password`.
When unmounted, the data remains encrypted and inaccessible.

The encrypted filesystem uses a `POSIX` layout, storing S3 objects as
regular files and directories together with IAM data. This allows files
and directories to be transferred directly into or out of the storage
without conversion.

For emergency recovery, the `cipherdir` can be mounted directly with
`gocryptfs` using the decrypted passphrase. The data is not locked into
the application and can be accessed or exported independently.

## How it works

S3 data and IAM state reside within the encrypted filesystem. Decrypted
data is available only while the filesystem is mounted and is accessible
externally only through the S3 API.

Initialization, mounting, unmounting, and other operations on the
encrypted storage require both the `secrets` volume to be available and
the `master password` to be provided. If either is unavailable, the
storage remains protected.

As an additional protection layer, a `watchdog` monitors critical
runtime conditions. If the application process fails, the `secrets`
volume becomes unavailable, or the storage itself becomes inaccessible,
it automatically unmounts the decrypted filesystem and stops the S3
gateway.

```text
        Container                          External
        Internals                          Interfaces

┌─────────────────────────┐
│ VersityGW               │------- S3-compatible API and WebGUI
│ (S3, IAM, WebGUI)       │        provide storage and IAM access
└─────────────────────────┘
             │
┌─────────────────────────┐
│ FastAPI application     │─────── REST API provides encrypted
│ (management layer)      │        storage lifecycle management
└─────────────────────────┘
             │
┌─────────────────────────┐
│ Decrypted data and IAM  │
│ (gocryptfs mountpoint)  │                External
└─────────────────────────┘                Volumes
             │
┌─────────────────────────┐       ┌─────────────────────────┐
│ Watchdog                │-------│ Detachable secrets      │
│ (mount supervisor)      │       │ (gocryptfs passphrase)  │
└─────────────────────────┘       └─────────────────────────┘
             │
┌─────────────────────────┐       ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
│ FUSE layer              │-------┃ Encrypted storage       ┃
│ (gocryptfs engine)      │       ┃ (gocryptfs cipherdir)   ┃
└─────────────────────────┘       ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Use cases

Hidden is designed for scenarios where data must remain protected
independently of the storage service and underlying infrastructure.
Typical use cases include:

**Private storage** — storage for sensitive data where encryption and
access to decrypted contents remain under the owner's control.

**Internal storage** — S3-compatible storage for applications, services,
and teams running on privately managed infrastructure.

**Isolated environments** — local S3 storage for disconnected,
restricted, or otherwise self-contained infrastructure.

**Backup and archival storage** — encrypted S3 storage for backups,
snapshots, exports, and long-term data retention.

## Integration and migration

Existing applications and tools can access the storage through the
standard S3 API without requiring proprietary clients or data formats.
The underlying POSIX layout also allows files and directories to be
transferred directly when needed.

Existing datasets can be imported without conversion, while stored data
can be exported in the same way. This supports migration between Hidden
and conventional filesystems, initial data seeding, and recovery outside
the application.

The S3 interface can be used with existing backup software, applications,
scripts, and other S3-compatible tools, allowing the storage to be
integrated into existing workflows.
