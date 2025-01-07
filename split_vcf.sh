bcftools +split -i 'GT="alt" & FILTER="PASS"' -Oz -o results/variant_calling/haplotypecaller/joint_variant_calling/split results/variant_calling/haplotypecaller/joint_variant_calling/joint_germline_recalibrated.vcf.gz

for vcf in $(ls results/variant_calling/haplotypecaller/joint_variant_calling/split/*.vcf.gz); do
    bcftools stats $vcf > ${vcf%.vcf.gz}.bcftools_stats.txt
done