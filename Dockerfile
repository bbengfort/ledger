# Dynamic builds
ARG XX_IMAGE=tonistiigi/xx
ARG BUILDER_IMAGE=golang:1.26-bookworm
ARG FINAL_IMAGE=debian:bookworm-slim

# Build stage
FROM --platform=${BUILDPLATFORM} ${XX_IMAGE} AS xx
FROM --platform=${BUILDPLATFORM} ${BUILDER_IMAGE} AS builder

# Copy XX scripts to the build stage
COPY --from=xx / /

# Build args
ARG GIT_REVISION=""

# Platform args
ARG TARGETOS
ARG TARGETARCH
ARG TARGETPLATFORM

# Prepare for cross-compilation
RUN apt-get update && apt-get install -y clang lld
RUN xx-apt install -y libc6-dev gcc

# Use modules for dependencies
WORKDIR $GOPATH/src/go.bengfort.dev/ledger

COPY go.mod .
COPY go.sum .

ENV CGO_ENABLED=1
ENV GO111MODULE=on
RUN go mod download
RUN go mod verify

# Copy source code
COPY pkg/ pkg/
COPY cmd/ cmd/

# Build the Ledger binary
RUN GOOS=${TARGETOS} GOARCH=${TARGETARCH} xx-go build -o /go/bin/ledger -ldflags="-X 'go.bengfort.dev/ledger/pkg.GitVersion=${GIT_REVISION}'" ./cmd/ledger && xx-verify /go/bin/ledger

# Bundle/minify web assets into pkg/web/dist (esbuild Go API; no Node/npm in image)
# RUN rm -rf pkg/web/dist
# RUN /go/bin/ledger staticfiles -o pkg/web/dist

# Final stage
FROM ${FINAL_IMAGE} AS final

LABEL maintainer="Benjamin Bengfort <benjamin@bengfort.com>"
LABEL description="Ledger Financial Analysis Service"

# Ensure ca-certificates are installed for external API calls
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy the Ledger binary from the builder stage
COPY --from=builder /go/bin/ledger /usr/local/bin/ledger

# Copy compiled static assets (see cmd/build-assets)
# COPY --from=builder /go/src/go.bengfort.dev/ledger/pkg/web/dist /var/www/ledger/static

ENV LEDGER_STATIC_SERVE=true
ENV LEDGER_STATIC_URL=/static
ENV LEDGER_STATIC_ROOT=/var/www/ledger/static

EXPOSE 8000

CMD [ "/usr/local/bin/ledger", "serve" ]
