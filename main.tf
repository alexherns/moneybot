module "lambda" {
  source                = "./modules/scheduled_lambda"
  app_region            = "${var.app_region}"
  auth_profile          = "${var.auth_profile}"
  auth_credentials_file = "${var.auth_credentials_file}"
  frequency             = "${var.frequency}"
  api_key               = "${var.api_key}"
  api_secret            = "${var.api_secret}"
  function_name         = "${var.function_name}"
  event_json            = "${var.event_json}"
}
