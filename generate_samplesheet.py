import os
import csv
import re
import logging
import argparse

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Generate Nextflow sample sheet from FASTQ files.')
    parser.add_argument('-r', '--root', type=str, default='.', help='Root directory containing sample subdirectories.')
    parser.add_argument('-m', '--metadata', type=str, help='Path to metadata CSV file (optional).')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output.')
    args = parser.parse_args()

    root_dir = args.root

    # Configure logging
    logging.basicConfig(
        filename='samplesheet_generation.log',
        filemode='w',
        level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if args.verbose:
        # Add console handler for verbose mode
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)

    # Define output CSV file
    output_csv = 'samplesheet.csv'

    # Define CSV headers
    headers = ['patient', 'sex', 'status', 'sample', 'lane', 'fastq_1', 'fastq_2']

    # Initialize a list to hold CSV rows
    rows = []

    # Regular expression to parse the filename
    # This regex captures:
    # - Group 1: lane (e.g., L2, L01)
    # - Group 2: pair (1 or 2)
    filename_pattern = re.compile(
        r'^[A-Z]\d+_(L\d+)_[^_]+_(1|2)\.fq\.gz$'
    )

    # Load metadata if provided
    metadata_dict = {}
    if args.metadata:
        try:
            import pandas as pd
            metadata_df = pd.read_csv(args.metadata)
            # Assuming metadata CSV has 'sample' (same as patient), 'sex', 'status' columns
            metadata_dict = metadata_df.set_index('sample').to_dict('index')
            logging.info(f"Metadata loaded from '{args.metadata}'.")
        except Exception as e:
            logging.error(f"Failed to load metadata from '{args.metadata}': {e}")
            print(f"Error: Failed to load metadata from '{args.metadata}'. Check 'samplesheet_generation.log' for details.")
            exit(1)

    # Define functions to extract sex and status
    def extract_sex(sample):
        if args.metadata:
            return metadata_dict.get(sample, {}).get('sex', '')
        else:
            # Default value if metadata not provided
            return 'XY'

    def extract_status(sample):
        if args.metadata:
            return metadata_dict.get(sample, {}).get('status', '0')
        else:
            # Default value if metadata not provided
            return '0'

    # Iterate over each subdirectory in the root directory
    for patient in os.listdir(root_dir):
        patient_path = os.path.join(root_dir, patient)
        if os.path.isdir(patient_path):
            logging.info(f"Processing patient directory: {patient}")
            # List all .fq.gz files in the patient directory
            files = [f for f in os.listdir(patient_path) if f.endswith('.fq.gz')]

            # Dictionary to hold FastQ pairs, keyed by a unique identifier (e.g., part before _1/_2)
            fastq_pairs = {}

            for file in files:
                match = filename_pattern.match(file)
                if match:
                    lane = match.group(1)  # e.g., L2, L01
                    pair = match.group(2)  # '1' or '2'

                    # Unique identifier for pairing (e.g., full filename without _1/_2 and extension)
                    # Example: V300063450_L2_B5GHUMxpmRAAACAAA-572
                    pair_id_match = re.match(r'^([A-Z]\d+_L\d+_[^_]+)', file)
                    if pair_id_match:
                        pair_id = pair_id_match.group(1)
                    else:
                        logging.warning(f"Could not extract pair ID from filename '{file}' in '{patient}'. Skipping.")
                        print(f"Warning: Could not extract pair ID from filename '{file}' in '{patient}'. Skipping.")
                        continue

                    if pair_id not in fastq_pairs:
                        fastq_pairs[pair_id] = {'lane': lane, 'fastq_1': '', 'fastq_2': ''}

                    if pair == '1':
                        if fastq_pairs[pair_id]['fastq_1']:
                            logging.warning(f"Multiple _1 files found for pair ID '{pair_id}' in '{patient}'. Previous: '{fastq_pairs[pair_id]['fastq_1']}', New: '{file}'. Skipping '{file}'.")
                            print(f"Warning: Multiple _1 files found for pair ID '{pair_id}' in '{patient}'. Skipping '{file}'.")
                        else:
                            fastq_pairs[pair_id]['fastq_1'] = os.path.join(args.root, patient, file)
                            logging.info(f"Found fastq_1 for pair ID '{pair_id}': {fastq_pairs[pair_id]['fastq_1']}")
                    elif pair == '2':
                        if fastq_pairs[pair_id]['fastq_2']:
                            logging.warning(f"Multiple _2 files found for pair ID '{pair_id}' in '{patient}'. Previous: '{fastq_pairs[pair_id]['fastq_2']}', New: '{file}'. Skipping '{file}'.")
                            print(f"Warning: Multiple _2 files found for pair ID '{pair_id}' in '{patient}'. Skipping '{file}'.")
                        else:
                            fastq_pairs[pair_id]['fastq_2'] = os.path.join(args.root, patient, file)
                            logging.info(f"Found fastq_2 for pair ID '{pair_id}': {fastq_pairs[pair_id]['fastq_2']}")
                else:
                    logging.warning(f"Filename '{file}' in '{patient}' does not match the expected pattern and will be skipped.")
                    print(f"Warning: Filename '{file}' in '{patient}' does not match the expected pattern and will be skipped.")

            # Create CSV rows from the fastq_pairs dictionary
            for pair_id, data in fastq_pairs.items():
                fastq_1 = data.get('fastq_1', '')
                fastq_2 = data.get('fastq_2', '')
                lane = data.get('lane', '')

                if fastq_1 and fastq_2:
                    row = {
                        'patient': patient,                # Patient identifier (subdirectory name)
                        'sex': extract_sex(patient),        # Dynamic extraction or default
                        'status': extract_status(patient),  # Dynamic extraction or default
                        'sample': patient,                 # Sample set to patient name
                        'lane': lane,
                        'fastq_1': fastq_1,
                        'fastq_2': fastq_2
                    }
                    rows.append(row)
                    logging.info(f"Added sample: {patient} with pair ID: {pair_id}, lane: {lane}")
                else:
                    missing = 'fastq_1' if not fastq_1 else 'fastq_2'
                    logging.warning(f"Incomplete FastQ pair for pair ID '{pair_id}' in '{patient}'. Missing '{missing}'. Skipping this entry.")
                    print(f"Warning: Incomplete FastQ pair for pair ID '{pair_id}' in '{patient}'. Missing '{missing}'. Skipping this entry.")

    # Write to CSV
    try:
        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"Sample sheet '{output_csv}' has been generated successfully.")
        logging.info(f"Sample sheet '{output_csv}' generated with {len(rows)} entries.")
    except Exception as e:
        logging.error(f"Failed to write to CSV file '{output_csv}': {e}")
        print(f"Error: Failed to write to CSV file '{output_csv}'. Check 'samplesheet_generation.log' for details.")

    print("Check 'samplesheet_generation.log' for any warnings or skipped entries.")

if __name__ == "__main__":
    main()
