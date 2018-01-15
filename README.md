# moneybot

## installation

It is suggested that you use [`virtualenvwrapper`](https://virtualenv.pypa.io) to install requirements

```sh
$ workon
$ mkvirtualenv moneybot
$ pip install -r requirements.txt
```


## setup

`$ export <Exchange>_API_KEY='<api_key>'`

`$ export <Exchange>_API_SECRET='<api_secret>'`

## execution

`$ python app/app.py <TRADE_TYPE> <EXCHANGE> <MARKET>`
