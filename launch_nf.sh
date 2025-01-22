#!/bin/bash
nextflow run nf-core/sarek -profile conda \
    --input samplesheet.csv \
    --igenomes_base /mnt/8TB-HDD/hongyongfeng/igenomes_base \
    --outdir results \
    -c executor.config \
    -params-file nf-params.json \
    -bg \
    -resume
