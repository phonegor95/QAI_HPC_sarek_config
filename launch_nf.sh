#!/bin/bash
nextflow run phonegor95/sarek -profile docker \
    -process.executor local \
    --input samplesheet.csv \
    --igenomes_base /mnt/8TB-HDD/hongyongfeng/igenomes_base \
    --outdir results \
    -c executor.config \
    -bg \
    -resume
