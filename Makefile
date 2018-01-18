pre-build:
	wget -O build.zip https://github.com/chennavarri/aws-lambda-pandas-sample/raw/master/lambda_function.zip

build:
	rm -rf dist/
	mkdir dist/
	cp main.py dist/
	cp -rf app dist/
	cp -rf ~/.virtualenvs/moneybot/lib/python2.7/site-packages/* dist/
	rm -rf dist/pandas*
	rm -rf dist/numpy*
	cd dist/ && zip -r9 ../build.zip *

install:
	pip install -r requirements.txt
