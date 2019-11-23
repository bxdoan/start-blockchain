# start-blockchain
This learning blockchain by practise using falcon framework

ref. https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

## Prepared
setup `.env` file

```bash
cp .env.sample .env
pipenv install
```

## Start the service

```bash
./run.sh start
```

## Stop the service

```bash
./run.sh stop
```

## Verify some end point

`/transactions/new`
```bash
curl -X POST \
  http://localhost:5555/transactions/new \
  -H 'Accept: */*' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 67' \
  -H 'Content-Type: application/json' \
  -H 'Host: localhost:5555' \
  -H 'Postman-Token: d655aa3f-8604-4658-82b9-27516a124be9,377db97b-dfcb-471f-9199-328161936bbb' \
  -H 'User-Agent: PostmanRuntime/7.19.0' \
  -H 'cache-control: no-cache' \
  -d '{
 "sender": "my address",
 "recipient": "someone else'\''s address",
 "amount": 5
}'
```

`/mine`
```bash
curl -X GET -I http://localhost:5555/mine 
```

`/chain`
```bash
curl -X GET -I http://localhost:5555/chain 
```