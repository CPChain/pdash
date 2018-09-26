## Introduction

PDash supports stream data transaction to meet the requirment of IOT data exchange. To achive this goal, kafka is introduced
in proxy for stream providing and consuming. Seller could ask proxy for a stream channel and publish data via this channel, then buyer pays to subscribe the channel and get the data. Restful and websocket APIs are provided for customers to publish/subscribe stream data.

## Restful API

- publish

    http://\<ip:port>/\<stream channel id> POST

    example: curl -X POST -d \<stream data> http://\<ip:port>/\<stream channel id>

- subscribe

    http://\<ip:port>/\<stream channel id> GET

    example: curl http://\<ip:port>/\<stream channel id>

## Websock API

- publish

    ws://\<ip:port>/\<stream channel id>?action=subscribe

    python example: cpchain/example/stream/produce_ws.py
- subscribe

    ws://\<ip:port>/\<stream channel id>?action=publish

    python example: cpchain/example/stream/consume_ws.py
