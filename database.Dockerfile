FROM postgres@sha256:eee6c6e1b0894fa4fe0075eb054af9fd1cf39a35321c2d4110626cfe506411fb
# This image always starts as postgres; the root-to-postgres helper is unnecessary.
# Removing the vulnerable executable fixes the final filesystem instead of suppressing CVEs.
RUN rm /usr/local/bin/gosu
# Apply Alpine security fixes published after the pinned base image (see ADR-018).
RUN apk upgrade --no-cache
USER 70:70
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD ["pg_isready", "-U", "postgres"]
