#!/bin/bash
nextflow run nf-core/sarek -profile conda \
    --input samplesheet.csv \
    --outdir results \
    -c executor.config \
    -params-file nf-params.json \
    -bg \
    -resume
