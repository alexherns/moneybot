module "lambda" {
  source                = "./modules/scheduled_lambda"
  app_region            = "${var.app_region}"
  auth_profile          = "${var.auth_profile}"
  auth_credentials_file = "${var.auth_credentials_file}"
  trade_type            = "${var.trade_type}"
  market                = "${var.market}"
  exchange              = "${var.exchange}"
  frequency             = "${var.frequency}"
  api_key               = "${var.api_key}"
  api_secret            = "${var.api_secret}"
}
