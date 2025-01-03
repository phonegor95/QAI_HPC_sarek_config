#!/bin/bash
nextflow run nf-core/sarek -profile conda \
    --input /mnt/SA127/methylation/20250102_WGS/samplesheet.csv \
    --outdir /mnt/SA127/methylation/20250102_WGS/results \
    -c executor.config \
    -params-file nf-params.json \
    -bg \
    -resume