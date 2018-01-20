# AWS configuration

variable "auth_credentials_file" {
  default = "~/.aws/credentials"
}

variable "auth_profile" {
  default = "moneybot_profile"
}

variable "app_region" {
  default = "us-east-1"
}

variable "function_name" {
  default = "moneybot"
}

# Exchange configuration

variable "api_key" {}

variable "api_secret" {}

# Algorithm configuration

variable "frequency" {
  default = 5
}

variable "event_json" {
  default = <<EOF
{
  "type": "MACD_TRADES",
  "market": "ETH/BTC",
  "exchange": "BINANCE"
}
EOF
}
