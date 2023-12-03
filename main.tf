variable "aws_account" {}
variable "region" {}
variable "secrets_path" {}
variable "linkedin_token" {}
variable "linkedin_user" {}
variable "telegram_chat_id" {}
variable "telegram_token" {}
variable "sentry_dsn" {}

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
  function_name    = "linkedin_bot"
  role             = aws_iam_role.lambda_role.arn
  filename         = "${path.module}/out/lambda.zip"
  handler          = "handler.main"
  runtime          = "python3.11"
  depends_on       = [aws_iam_role_policy_attachment.attach_policy_to_role]
  source_code_hash = data.archive_file.zip_of_lambda_code.output_base64sha256
  environment {
    variables = {
      LINKEDIN_TOKEN   = var.linkedin_token
      LINKEDIN_USER    = var.linkedin_user
      TELEGRAM_CHAT_ID = var.telegram_chat_id
      TELEGRAM_TOKEN   = var.telegram_token
      SENTRY_DSN       = var.sentry_dsn
    }
  }
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
        },
        {
          "Effect": "Allow",
          "Action": [
            "dynamodb:GetItem",
            "dynamodb:UpdateItem",
            "dynamodb:Query",
            "dynamodb:Scan"
          ],
          "Resource": "${aws_dynamodb_table.quotes-table.arn}"
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

resource "aws_dynamodb_table" "quotes-table" {
  name         = "quotes"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "msg"

  attribute {
    name = "msg"
    type = "S"
  }
}

resource "aws_cloudwatch_event_rule" "event_rule" {
  name                = "linkedin_bot_event_rule"
  schedule_expression = "cron(34 8 ? * * *)"
}

resource "aws_lambda_permission" "event_rule_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.event_rule.arn
}


resource "aws_cloudwatch_event_target" "event_target" {
  rule      = aws_cloudwatch_event_rule.event_rule.name
  target_id = "linkedin_bot_event_rule_target"
  arn       = aws_lambda_function.lambda.arn
}

resource "aws_lambda_function_event_invoke_config" "lambda_error_handling_config" {
  function_name                = aws_lambda_function.lambda.function_name
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 0
}
