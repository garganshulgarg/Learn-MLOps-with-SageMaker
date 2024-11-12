import pandas as pd
import numpy as np
import argparse
import os
from sklearn.preprocessing import OrdinalEncoder

def _parse_args():
    """
    Parses command-line arguments for data file paths and feature configurations.
    - filepath: Directory containing the input dataset.
    - filename: Name of the dataset file.
    - outputpath: Directory to store the output processed files.
    - categorical_features: Comma-separated list of categorical features.
    """
    parser = argparse.ArgumentParser()

    # Input directory and file paths
    parser.add_argument('--filepath', type=str, default='/opt/ml/processing/input/')
    parser.add_argument('--filename', type=str, default='bank-additional-full.csv')
    
    # Output directory path
    parser.add_argument('--outputpath', type=str, default='/opt/ml/processing/output/')
    
    # List of categorical features for encoding
    parser.add_argument('--categorical_features', type=str, default='y, job, marital, education, default, housing, loan, contact, month, day_of_week, poutcome')

    return parser.parse_known_args()

if __name__ == "__main__":
    # Parse input arguments
    args, _ = _parse_args()

    # Load the dataset from the specified input path
    df = pd.read_csv(os.path.join(args.filepath, args.filename))

    # Clean column names: replace dots with underscores and remove trailing underscores
    df = df.replace(regex=r'\.', value='_')
    df = df.replace(regex=r'\_$', value='')

    # Add indicator columns:
    # - 'no_previous_contact': Indicates if 'pdays' equals 999 (no previous contact).
    # - 'not_working': Indicates if the job is "student", "retired", or "unemployed".
    df["no_previous_contact"] = (df["pdays"] == 999).astype(int)
    df["not_working"] = df["job"].isin(["student", "retired", "unemployed"]).astype(int)

    # Drop non-informative or unnecessary columns
    df = df.drop(['duration', 'emp_var_rate', 'cons_price_idx', 'cons_conf_idx', 'euribor3m', 'nr_employed'], axis=1)

    # Apply one-hot encoding to all categorical features in the dataframe
    df = pd.get_dummies(df)

    # Split the dataset into training (70%), validation (20%), and test (10%) sets
    train_data, validation_data, test_data = np.split(
        df.sample(frac=1, random_state=42),
        [int(0.7 * len(df)), int(0.9 * len(df))]
    )

    # Save the training set with target label ('y_yes') as the first column
    pd.concat([train_data['y_yes'], train_data.drop(['y_yes', 'y_no'], axis=1)], axis=1) \
        .to_csv(os.path.join(args.outputpath, 'train/train_script.csv'), index=False, header=False)

    # Save the validation set with 'y_yes' as the first column
    pd.concat([validation_data['y_yes'], validation_data.drop(['y_yes', 'y_no'], axis=1)], axis=1) \
        .to_csv(os.path.join(args.outputpath, 'validation/validation_script.csv'), index=False, header=False)

    # Save the test set with 'y_yes' as the label file, and the remaining features as input data
    test_data['y_yes'].to_csv(os.path.join(args.outputpath, 'test/test_script_y.csv'), index=False, header=False)
    test_data.drop(['y_yes', 'y_no'], axis=1) \
        .to_csv(os.path.join(args.outputpath, 'test/test_script_x.csv'), index=False, header=False)

    print("## Processing completed. Exiting.")
