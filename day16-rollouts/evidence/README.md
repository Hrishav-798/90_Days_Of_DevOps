# Day 16 Evidence Logs: Kubernetes Deployments & Rollouts

This directory contains the verified terminal session outputs recorded during the **Day 16: Kubernetes Deployments & Rollouts** hands-on lab on the local `kind-winter-arc` Kubernetes cluster.

## 📋 Evidence Files Overview

| File | Description | Core Artifacts / Key Verification |
| :--- | :--- | :--- |
| [`rollout-success.txt`](rollout-success.txt) | Valid Image Update | Annotating change-cause, updating image to `nginx:1.28`, `kubectl rollout status` success, scaling old ReplicaSet to 0, and 3 Ready Pods. |
| [`rollout-history.txt`](rollout-history.txt) | Revision Tracking | Initial state (`<none>`), two revisions post-update, revision #2 Pod template inspection, and post-rollback revision history (revisions 1, 3, 4). |
| [`failed-rollout-events.txt`](failed-rollout-events.txt) | Broken Release Diagnosis | Updating to invalid image `nginx:1.99-broken`, Pod state transitions (`ErrImagePull` → `ImagePullBackOff`), `kubectl describe pod` event log showing Docker Hub `NotFound`. |
| [`rollback-verified.txt`](rollback-verified.txt) | Recovery & Rollback | Executing `kubectl rollout undo`, observing `last-applied-configuration` warning, successful rollback confirmation, ReplicaSet scale-down, and restoration of 3 healthy `nginx:1.28` Pods. |

## ℹ️ Lab Environment & Execution Metadata

- **Cluster Context:** `kind-winter-arc`
- **Target Namespace:** `default`
- **Deployment Name:** `nginx-deployment`
- **Container Name:** `nginx`
- **Desired Replicas:** 3
- **Initial Image:** `nginx:1.27`
- **Target Image:** `nginx:1.28`
- **Simulated Bad Image:** `nginx:1.99-broken`

## 📸 Note on Screenshot Evidence

> [!NOTE]
> All evidence in this folder consists of direct, verbatim terminal capture logs from the live local `kind` cluster session. Visual screenshot artifacts (`.png` / `.jpeg`) can be captured separately from the terminal during interactive runs if required for portfolio or presentation assets. To maintain absolute integrity and avoid fabricated graphics, only real terminal session logs are preserved here.
