variable "payload_path" {
  default = "build.zip"
}

variable "function_description" {
  default = "moneybot lambda function"
}

variable "function_timeout" {
  default = 10
}

variable "handler" {
  default = "main.event_handler"
}
