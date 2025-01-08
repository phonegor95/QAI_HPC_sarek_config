# QAI HPC nf-core/sarek config

### data/sample/
put all raw data per sample in data/sample/r'(L\d+)(?:_[^_]+)?_(1|2)\.fq\.gz$'

### metadata.csv header
patient,sample,sex,status

### samplesheet
```
python generate_samplesheet.py -r data -m metadata.csv
```
### launch
```
conda activate
sh launch.sh
```
