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

![version](https://img.shields.io/badge/version-0.6.0-2f81f7)
[![license](https://img.shields.io/badge/license-Apache--2.0-2f81f7)](./LICENSE)

If you like it, star it ⭐ — it helps discoverability. Thank you!

## References

- Encrypted filesystem: [gocryptfs](https://github.com/rfjakob/gocryptfs)
- S3-compatible gateway: [VersityGW](https://github.com/versity/versitygw)
- Architectural decisions: [ADR.md](./ADR.md)

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
│ FastAPI application     │─────── OpenAPI provides gocryptfs
│ (REST API)              │        lifecycle management
└─────────────────────────┘
             │
┌─────────────────────────┐
│ Decrypted data and IAM  │
│ (gocryptfs mountpoint)  │                External
└─────────────────────────┘                Volumes
             │
┌─────────────────────────┐       ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
│ Watchdog                │-------┃ Detachable secrets      ┃
│ (mount supervisor)      │       ┃ (gocryptfs passphrase)  ┃
└─────────────────────────┘       ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
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

- **Private storage** — storage for sensitive data where encryption and
access to decrypted contents remain under the owner's control.

- **Internal storage** — S3-compatible storage for applications, services,
and teams running on privately managed infrastructure.

- **Isolated environments** — local S3 storage for disconnected,
restricted, or otherwise self-contained infrastructure.

- **Backup and archival storage** — encrypted S3 storage for backups,
snapshots, exports, and long-term data retention.

## What is protected

The protection model covers physical access to stored data, storage
volumes, or the host system. Encryption remains independent of the S3
layer and application-level access controls.

- **Stolen host or unauthorized disk access.** The `cipherdir` contains
encrypted data only. Physical access to the host or storage, raw disk
access, filesystem recovery tools, or direct inspection of the encrypted
volume do not expose plaintext file contents or names.

- **Leaked volume data.** The `cipherdir` and `secrets` volumes are
protected independently. A copied or exposed `cipherdir` remains
encrypted without the corresponding `gocryptfs` passphrase, while the
passphrase stored in `secrets` is itself encrypted and cannot be used
without the `master password`. Even possession of both volumes is
insufficient to access the stored data without the `master password`.

- **Unexpected runtime conditions.** A `watchdog` monitors the
application process, the `secrets` volume, and the encrypted storage.
If a critical condition is detected, it unmounts the decrypted
filesystem and stops the S3 gateway.

- **Container loss or replacement.** Persistent data and secrets are
stored outside the application container, allowing the container to be
replaced without affecting the stored data. The `cipherdir` can also be
mounted directly with `gocryptfs` using the decrypted passphrase,
providing access to its POSIX files and directories independently
of the application.

## What is not protected against

The protection model does not cover compromised runtime environments
or recovery from a lost master password.

- **Runtime host or container compromise.** While the filesystem is
mounted, decrypted data exists inside the container. An attacker with
sufficient privileges on the host or inside the container may be able
to access the decrypted filesystem directly.

- **Forgotten master password.** The `master password` is not stored
anywhere. If lost, the encrypted passphrase cannot be unlocked and the
storage cannot be recovered.

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

## License

This project is licensed under the **Apache License 2.0**
(`Apache-2.0`).

You may use, modify, and distribute this software in accordance with
the terms of the Apache License 2.0.

See [LICENSE](./LICENSE) for the full license text.

Copyright (c) 2026 Artem Abramov


```text
app/
├── main.py                   # FastAPI setup, middleware, routers
├── config.py                 # settings loaded from .env
├── constants.py
├── context.py                # request context: ID and timing
├── errors.py                 # management API HTTP errors
├── handlers.py               # exception handlers
├── io.py                     # async filesystem I/O
├── locks.py                  # async locks for lifecycle operations
├── log.py                    # logging setup and context filter
├── version.py
├── dependencies/
│   └── require_gocryptfs.py  # gocryptfs state checks
├── pydantic/
│   └── master_password.py    # master password validation
├── routers/                  # gocryptfs management endpoints
├── services/                 # gocryptfs lifecycle operations
├── schemas/                  # API request/response models
├── runtime/
│   ├── cipherdir.py          # gocryptfs init, mount, unmount
│   ├── versity.py            # VersityGW credentials, process control
│   └── watchdog.py           # emergency unmount on runtime failure
├── security/
│   ├── encryption.py         # scrypt + AES-GCM passphrase encryption
│   └── randoms.py
└── middleware/               # CORS, logging, context, security headers
```
