# Distributed Test Execution Orchestrator ⚙️

A lightweight control-plane and worker system for **scheduling, provisioning, executing, and collecting results** for distributed HIL/SIL test benches. Designed for reliability, scalability, and CI integration.

---

## Overview

This project provides:

* **Orchestrator API** — reservation lifecycle, execution lifecycle, bench status, artifact access.
* **Scheduler** — assigns benches based on policies and submits tasks to the queue.
* **Worker Pool** — processes tasks: provision, run tests, collect artifacts, teardown.
* **Runner Adapters** — pluggable execution backends (Local, EC2, EKS, On-prem).
* **CLI** — developer tool to reserve benches, trigger execution, fetch logs, and check status.
* **Persistence & Queue** — durable reservation/execution state + decoupled task dispatch.

---

## Key Features ✨

* Bench reservation & release
* Automated provisioning → execution → teardown
* Structured logs, metrics, tracing (OpenTelemetry)
* Artifact upload to S3/EFS
* RBAC-secured API (OIDC/JWT)
* CI hooks for automated test runs
* Idempotent operations with retries & DLQ
* Extensible runner adapter model

---

## High-Level Architecture

* API Orchestrator (control plane)
* Scheduler
* Worker Pool
* Queue (SQS/RabbitMQ)
* Persistence layer (DynamoDB/Postgres)
* Artifact storage (S3/EFS)
* CLI
* CI integrations

---

## Directory Layout

```
test-execution-orchestrator/
├─ api/
├─ workers/
├─ adapters/
├─ cli/
├─ tests/
├─ docs/
├─ deployment/
├─ docker/
└─ README.md
```

---

## Getting Started 🚀

1. Clone the repository
2. Set environment variables (`local`, `dev`, etc.)
3. Start the API and workers using docker-compose or local runtime
4. Use the CLI for bench reservation, test execution, and log retrieval

---

## Core Commands (CLI)

* `reserve` — request a bench
* `release` — release a bench
* `run` — trigger a test execution
* `status` — view execution progress
* `logs` — stream or fetch logs

---

## Environments

* `local` (mocked adapters)
* `dev` (shared infra)
* `staging`
* `prod`

Each environment defines its own endpoints, queues, IAM roles, and feature flags.

---

## Contributing

* Follow coding guidelines and SOLID principles
* Ensure unit tests and integration tests pass
* Submit ADRs for major architectural decisions

---

## Status

This project is under active development. Refer to `docs/ARCHITECTURE.md` and sprint plan for current progress.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---
