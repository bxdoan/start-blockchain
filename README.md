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

## Verify some end point in 1 node

`/transactions/new`
```bash
curl -X POST \
  http://localhost:5555/transactions/new \
  -H 'Content-Type: application/json' \
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

## Verify some end point in 2 nodes
Start 2 nodes:  http://localhost:5555/ and  http://localhost:5556/

Mining some new Blocks on node 2, to ensure the chain was longer. Afterward, I called GET /nodes/resolve on node 1,
where the chain was replaced by the Consensus Algorithm:

`:node1/nodes/register`
```bash
curl -X POST -I \
  http://localhost:5555/nodes/register\
  -H 'Accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
 "nodes" : ["http://localhost:5556"]
}'
```

`:node1/nodes/resolve`
```bash
curl -X GET -I \
  http://localhost:5555/nodes/resolve\
  -H 'Accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
 "nodes" : ["http://localhost:5556"]
}'
```