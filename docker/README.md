# Docker Sandboxing & Observability

Contains the throwaway container isolation harness:
- `Dockerfile.sandbox`: Minimal Python/Linux image with `strace`.
- `entrypoint.sh`: Supervisor isolating logs strictly to `/obs/` for stdio cleanliness.
- `sink.py`: In-container HTTP sink on `127.0.0.1:8080`.
