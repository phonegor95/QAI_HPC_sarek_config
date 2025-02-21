#!/bin/bash
nextflow run phonegor95/sarek -profile singularity \
    --input samplesheet.csv \
    --igenomes_base /mnt/SA127/methylation/references \
    --outdir results \
    -c executor.config \
    -bg \
    -resume
