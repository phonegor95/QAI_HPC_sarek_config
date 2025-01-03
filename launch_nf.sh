#!/bin/bash
nextflow run nf-core/sarek -profile conda \
    --input /mnt/SA127/methylation/20250102_WGS/samplesheet.csv \
    --outdir /mnt/SA127/methylation/20250102_WGS/results \
    --aligner bwa-mem2 \
    --trim_fastq true \
    --joint_germline true \
    --save_trimmed true \
    --tools haplotypecaller \
    --genome GATK.GRCh38 \
    --email hongyongfeng@hkqai.hk \
    -c executor.config \
    -params-file nf-params.json \
    -bg \
    -resume