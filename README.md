# Rearc Data Quest Challenge - Solution

This repository contains the end-to-end solution for the Rearc Data Quest coding challenge. It includes Lambda functions, PySpark analytics, and Terraform infrastructure as code.

---

#Folder Structure

data/                  # Local copies of dataset files from S3 (used in Part 3)
lambda_functions/      # Contains source code for Lambda functions (Part 1 and 2)
part_3_ipynb/          # Jupyter notebook with Part 3 analytics using PySpark
/main.tf             # Terraform code to set up SQS, S3 event notifications, and Lambda trigger


---

## Lambda Functions (`lambda_functions/`)

### `part_1_source_code.py`

- This Lambda function **syncs data** from the [BLS API open dataset](https://download.bls.gov/pub/time.series/pr/) into an S3 bucket: `my-bls-data-sync`.
- Synced files can be viewed in the public S3 location:  
  [Browse Synced BLS Data](https://us-east-1.console.aws.amazon.com/s3/buckets/my-bls-data-sync?region=us-east-1&prefix=pub/time.series/pr/&showversions=false)

###  `part_2_source_code.py`

- This Lambda function fetches data from the [Data USA Population API](https://datausa.io/api/data?drilldowns=Nation&measures=Population)
- It stores the result as a JSON file in:  
  `s3://my-bls-data-sync/datausa/population_data.json`
- [Browse Population Data in S3](https://us-east-1.console.aws.amazon.com/s3/buckets/my-bls-data-sync?region=us-east-1&prefix=datausa/&showversions=false)

---

## Part 3 - PySpark Analysis (`part_3_ipynb/`)

- The Jupyter notebook performs **three main analytics tasks** using PySpark.
- For this challenge, the following files were downloaded from S3 to local disk:
  - `data/pr.data.0.Current`
  - `data/population_data.json`
- All processing logic is written using **PySpark**, covering:
  1. Population mean and stddev (2013–2018)
  2. Best year by value sum per series ID
  3. Joining series ID = `PRS30006032` + period = `Q01` with population data

---

## ⚙️ Infrastructure as Code (`/`)

The Terraform configuration includes:

- Creation of an **SQS queue** named `datausa-analytics-trigger`
- **S3 → SQS event notifications** when a JSON is uploaded to `datausa/` prefix
- A **Lambda function** triggered by the SQS queue that logs the analysis steps (from the notebook)
- Also includes a zipped Lambda function file `part_4_log_results.zip`, which logs the simulated query results based on the Part 3 notebook logic


---

