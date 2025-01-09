bcftools +split -i 'GT="alt" & FILTER="PASS"' -Oz -o results/variant_calling/haplotypecaller/joint_variant_calling/split results/variant_calling/haplotypecaller/joint_variant_calling/joint_germline_recalibrated.vcf.gz

for vcf in $(ls results/variant_calling/haplotypecaller/joint_variant_calling/split/*.vcf.gz); do
    # GQ>=20, DP>=10, and het 0.2<AB<0.8
    bcftools +fill-tags $vcf -Ou -- -t FORMAT/VAF | \
    bcftools filter -e 'FMT/DP<10 | GQ<20 | (GT="het" & (VAF < 0.2 | VAF > 0.8))' -Oz -o "${vcf%.vcf.gz}.hardfilter.vcf.gz"
    tabix -p vcf ${vcf%.vcf.gz}.hardfilter.vcf.gz
done
