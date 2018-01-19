# moneybot

## installation

It is suggested that you use [`virtualenvwrapper`](https://virtualenv.pypa.io) to install requirements

```sh
$ workon
$ mkvirtualenv moneybot
$ pip install -r requirements.txt
```

## running locally

### setup

`$ export _API_KEY='<api_key>'`

`$ export _API_SECRET='<api_secret>'`

### execution

`$ python app/app.py <TRADE_TYPE> <EXCHANGE> <MARKET>`

## deploy

### setup

First install terraform: 

`$ brew install terraform`

Next, run terraform initialization:

`$ make pre-deploy`

### configuration

In order to deploy into your aws infrastructure, you'll need to have the aws command line tools installed and initial setup run.
Once you've properly set up `aws` you'll need to configure terraform for your environment and algorithm.
You can either edit the existing `main.variables.tf` or create a custom `.auto.tfvars` file in this directory which
will automatically override the defaults set in `main.variables.tf`. 

Example `my_moneybot_algo.auto.tfvars`:

```
"auth_profile" = "<your_aws_profile>"
"api_key" = "<your_exchange_api_key>"
"api_secret" = "<your_exchange_api_secret>"
"exchange" = "<CRYPTO_EXCHANGE_ALL_CAPS>
"trade_type" = "<TRADE_TYPE_SEE_MAIN.PY>"
"market" = "<QUOTE_CURRENCY/BASE_CURRENCY>"
"frequency" = "<TRADE_FREQUENCY_IN_MINUTES>"
```

Coming soon: config-level optimizations so that you can fine-tune parameter settings

Note: currently BINANCE remains the only tested exchange. Certain exchanges, like GEMINI are known to not work with this tool, 
as they do not provide API access to OHLCV charts.

### using terraform

Finally, you are ready to deploy:

`$ make build && make deploy`

To tear down the bot run:

`$ make destroy`

## disclaimer

Bot-trading is dangerous. I make no claims about the performance of the example algorithms or the tooling provided for executing them, nor am I responsible for any gains or losses made while using this tool. Have fun, be safe.
