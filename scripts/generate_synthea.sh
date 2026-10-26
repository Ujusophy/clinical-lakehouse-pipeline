#!/usr/bin/env bash
# Generates 1,000 synthetic patients (seed 42) as CSV, then syncs to S3.
set -euo pipefail
: "${BUCKET:?Set BUCKET to your S3 bucket name}"
cd "${SYNTHEA_DIR:-$HOME/synthea}"
./run_synthea -s 42 -p 1000 Massachusetts \
  --exporter.csv.export=true --exporter.fhir.export=false
aws s3 sync output/csv/ "s3://${BUCKET}/landing/synthea/csv/" --region ca-central-1
