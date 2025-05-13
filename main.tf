#  Terraform Setup for Rearc Data Quest - Part 3

#This Terraform script builds the infrastructure to automate the final stage of the Rearc Data Quest. It sets up an S3 → SQS → Lambda pipeline to trigger Spark-based analytics.



##  What This Terraform Project Does

# Uses an existing S3 bucket: `my-bls-data-sync`
# Creates an **SQS queue** (`datausa-analytics-trigger`) that gets notified whenever a new JSON is uploaded to `datausa/` prefix in S3
# Creates a **Lambda function** triggered by that queue
# Grants the Lambda permissions to read from S3 and SQS, and log to CloudWatch



## Files and Structure


# main.tf                  # Terraform configuration (infra setup)
# analytics_lambda.zip     # Zipped Lambda function code (includes lambda_function.py)
# lambda_function.py      # Python code for analytics (you zip this file)




## Terraform Breakdown

### 1. Provider and Bucket


provider "aws" {
  region = "us-east-1"
}

locals {
  existing_bucket_name = "my-bls-data-sync"
}



### 2. SQS Queue and S3 Notification


resource "aws_sqs_queue" "data_queue" {
  name = "datausa-analytics-trigger"
}

resource "aws_sqs_queue_policy" "s3_to_sqs_policy" {
  queue_url = aws_sqs_queue.data_queue.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "s3.amazonaws.com"
        },
        Action = "sqs:SendMessage",
        Resource = aws_sqs_queue.data_queue.arn,
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = "arn:aws:s3:::${local.existing_bucket_name}"
          }
        }
      }
    ]
  })
}

resource "aws_s3_bucket_notification" "s3_to_sqs" {
  bucket = local.existing_bucket_name

  queue {
    id            = "json-upload-event"
    queue_arn     = aws_sqs_queue.data_queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "datausa/"
    filter_suffix = ".json"
  }

  depends_on = [aws_sqs_queue_policy.s3_to_sqs_policy]
}




### 3. IAM Role and Policy for Lambda


resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda_policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = ["s3:GetObject", "s3:ListBucket"],
        Resource = [
          "arn:aws:s3:::${local.existing_bucket_name}",
          "arn:aws:s3:::${local.existing_bucket_name}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"],
        Resource = aws_sqs_queue.data_queue.arn
      }
    ]
  })
}


### 4. Lambda Function to Run Analytics

resource "aws_lambda_function" "analytics_lambda" {
  function_name = "analytics-from-sqs"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300 

  filename         = "analytics_lambda.zip"
  source_code_hash = filebase64sha256("part_4_log_results.zip")
}




### 5. Connect Lambda to SQS


resource "aws_lambda_event_source_mapping" "sqs_to_lambda" {
  event_source_arn = aws_sqs_queue.data_queue.arn
  function_name    = aws_lambda_function.analytics_lambda.arn
  batch_size       = 1
  enabled          = true
}


