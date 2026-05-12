# main.tf
# ─────────────────────────────────────────────────────────────────────────────
# DataOps AWS Infrastructure
# Provisions S3 data landing bucket, IAM roles for Snowflake and Lambda,
# and a Lambda function for pipeline event triggers.
# ─────────────────────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state — keeps state in S3 so the team shares it
  backend "s3" {
    bucket = "company-terraform-state"
    key    = "dataops/infra/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# ── S3 Data Landing Bucket ───────────────────────────────────────────────────

resource "aws_s3_bucket" "data_landing" {
  bucket = "${var.env}-data-landing-${var.project}"
  tags   = local.common_tags
}

resource "aws_s3_bucket_versioning" "data_landing" {
  bucket = aws_s3_bucket.data_landing.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "data_landing" {
  bucket = aws_s3_bucket.data_landing.id

  rule {
    id     = "expire-raw-after-90-days"
    status = "Enabled"
    filter { prefix = "raw/" }
    expiration { days = 90 }
  }
}

# Block all public access — data buckets are never public
resource "aws_s3_bucket_public_access_block" "data_landing" {
  bucket                  = aws_s3_bucket.data_landing.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ── IAM Role: Snowflake Storage Integration ──────────────────────────────────

resource "aws_iam_role" "snowflake_storage" {
  name = "${var.env}-snowflake-storage-role"
  tags = local.common_tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { AWS = var.snowflake_aws_account_arn }
      Action    = "sts:AssumeRole"
      Condition = {
        StringEquals = {
          "sts:ExternalId" = var.snowflake_external_id
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "snowflake_s3_access" {
  name = "snowflake-s3-access"
  role = aws_iam_role.snowflake_storage.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:ListBucket",
        ]
        Resource = [
          aws_s3_bucket.data_landing.arn,
          "${aws_s3_bucket.data_landing.arn}/*",
        ]
      }
    ]
  })
}

# ── Lambda: S3 Event Trigger ─────────────────────────────────────────────────

resource "aws_iam_role" "lambda_exec" {
  name = "${var.env}-lambda-pipeline-trigger"
  tags = local.common_tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "pipeline_trigger" {
  function_name = "${var.env}-pipeline-trigger"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  filename      = "lambda_package.zip"
  tags          = local.common_tags

  environment {
    variables = {
      ENV        = var.env
      SNS_TOPIC  = aws_sns_topic.pipeline_alerts.arn
    }
  }
}

resource "aws_s3_bucket_notification" "trigger_on_upload" {
  bucket = aws_s3_bucket.data_landing.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.pipeline_trigger.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "raw/"
  }
}

# ── SNS: Pipeline Alerts ─────────────────────────────────────────────────────

resource "aws_sns_topic" "pipeline_alerts" {
  name = "${var.env}-pipeline-alerts"
  tags = local.common_tags
}

# ── Locals ───────────────────────────────────────────────────────────────────

locals {
  common_tags = {
    Project     = var.project
    Environment = var.env
    ManagedBy   = "terraform"
    Team        = "dataops"
  }
}
