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

variable "exchange" {
  default = "BINANCE"
}

# Algorithm configuration

variable "trade_type" {
  default = "MACD_TRADES"
}

variable "market" {
  default = "ETH/BTC"
}

variable "frequency" {
  default = 5
}
