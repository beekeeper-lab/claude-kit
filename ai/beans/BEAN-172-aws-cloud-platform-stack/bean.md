# BEAN-172: AWS Cloud Platform Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-172 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The existing DevOps stack is platform-agnostic and doesn't provide AWS-specific service guidance. Teams deploying to AWS need guidance on core services, the Well-Architected Framework, cost optimization, and security best practices.

## Goal

Add a complete AWS cloud platform stack to the ai-team-library following the established stack template pattern.

## Scope

### In Scope
- Core AWS services (IAM, VPC, Lambda, ECS, RDS, S3)
- AWS Well-Architected Framework pillars
- Cost optimization strategies
- Security best practices (least privilege, encryption, logging)
- Stack file following standardized template

### Out of Scope
- Other cloud platforms (Azure, GCP)
- Modifications to the existing DevOps stack
- Application code changes

## Acceptance Criteria

- [ ] `ai-team-library/stacks/aws-cloud-platform/` directory exists with properly formatted stack file
- [ ] Stack file follows the standardized template pattern (Defaults table+alternatives, Do/Don't, Common Pitfalls, Checklist)
- [ ] Covers core services, Well-Architected Framework, cost optimization, and security
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

AWS is the dominant cloud platform. This provides AWS-specific guidance complementing the platform-agnostic DevOps stack.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998e291e7e85ee65ed40ac3 |
| **Card Name** | AWS Cloud Platform Stack |
| **Card URL** | https://trello.com/c/drLH9MTS/47-aws-cloud-platform-stack |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
