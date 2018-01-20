variable "app_region" {}
variable "auth_profile" {}
variable "auth_credentials_file" {}
variable "trade_type" {}
variable "market" {}
variable "exchange" {}
variable "api_key" {}
variable "api_secret" {}
variable "frequency" {}
variable "function_name" {}

provider "aws" {
  region                  = "${var.app_region}"
  shared_credentials_file = "${var.auth_credentials_file}"
  profile                 = "${var.auth_profile}"
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "main" {
  name = "${var.function_name}-lambda-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "main" {
  name = "${var.function_name}-lambda-policy"
  role = "${aws_iam_role.main.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect":"Allow",
            "Action":[
                "ssm:GetParameters"
            ],
            "Resource": "arn:aws:ssm:${var.app_region}:${data.aws_caller_identity.current.account_id}:parameter/EXCHANGE_API_*"
        },
        {
            "Effect":"Allow",
            "Action":[
                "kms:Decrypt"
            ],
            "Resource": "arn:aws:kms:${var.app_region}:${data.aws_caller_identity.current.account_id}:key/*"
        }
    ]
}
EOF
}

resource "aws_lambda_function" "main" {
  filename         = "${var.payload_path}"
  function_name    = "${var.function_name}"
  description      = "${var.function_description}"
  handler          = "${var.handler}"
  role             = "${aws_iam_role.main.arn}"
  memory_size      = 128
  runtime          = "python2.7"
  timeout          = "${var.function_timeout}"
  source_code_hash = "${base64sha256(file("${var.payload_path}"))}"

  # environment {
  #   variables = {
  #     "EXCHANGE_API_KEY"    = "${var.api_key}"
  #     "EXCHANGE_API_SECRET" = "${var.api_secret}"
  #   }
  # }
}

resource "aws_cloudwatch_event_rule" "main" {
  name                = "${var.function_name}-event-rule"
  schedule_expression = "cron(1/${var.frequency} * * * ? *)"
}

resource "aws_cloudwatch_event_target" "main" {
  rule = "${aws_cloudwatch_event_rule.main.name}"
  arn  = "${aws_lambda_function.main.arn}"

  input = <<EOF
{
  "type": "${var.trade_type}",
  "exchange": "${var.exchange}",
  "market": "${var.market}"
}
EOF
}

resource "aws_lambda_permission" "main" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.main.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.main.arn}"
}

resource "aws_ssm_parameter" "api_key" {
  name  = "EXCHANGE_API_KEY"
  type  = "SecureString"
  value = "${var.api_key}"
}

resource "aws_ssm_parameter" "api_secret" {
  name  = "EXCHANGE_API_SECRET"
  type  = "SecureString"
  value = "${var.api_secret}"
}
