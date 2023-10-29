variable "aws_account" {}
variable "region" {}
variable "secrets_path" {}

provider "aws" {
  region                   = var.region
  shared_credentials_files = [var.secrets_path]
}

data "archive_file" "zip_of_lambda_code" {
  type        = "zip"
  output_path = "${path.module}/out/lambda.zip"
  source_dir  = "${path.module}/src"
}

resource "aws_lambda_function" "lambda" {
  function_name = "linkedin_bot"
  role          = aws_iam_role.lambda_role.arn
  filename      = "${path.module}/out/lambda.zip"
  handler       = "main.main"
  runtime       = "python3.11"
  depends_on    = [aws_iam_role_policy_attachment.attach_policy_to_role]
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "terraform_lambda_linkedin_bot_iam_policy"
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "logs:CreateLogStream",
                "logs:CreateLogGroup",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:${var.region}:${var.aws_account}:log-group:/aws/lambda/linkedin_bot:*"
            ],
            "Effect": "Allow"
        }
    ]
}
  EOF
}

resource "aws_iam_role" "lambda_role" {
  name               = "terraform_lambda_linkedin_bot_iam_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
      {
	  "Action": "sts:AssumeRole",
	  "Effect": "Allow",
	  "Principal": {
	      "Service": "lambda.amazonaws.com"
	  }
      }
  ]
}
  EOF
}

resource "aws_iam_role_policy_attachment" "attach_policy_to_role" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}
