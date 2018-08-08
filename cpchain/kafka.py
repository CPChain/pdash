import logging
from confluent_kafka import Producer, Consumer, KafkaError, KafkaException

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self, boot_servers, client_id):
        conf = {
            'bootstrap.servers': boot_servers,
            'client.id': client_id,
            'default.topic.config': {'acks': 'all'}
            }

        self.producer = Producer(conf)

    def produce(self, topic, data):

        def delivery_report(err, msg):
            """ Called once for each message produced to indicate delivery result.
                Triggered by poll() or flush(). """
            if err is not None:
                logger.debug("Failed to deliver message: %s: %s" % (str(msg), str(err)))
            else:
                logger.debug("Message %s produced to %s %s" % (msg.value(), msg.topic(), msg.partition()))

        # Trigger any available delivery report callbacks from previous produce() calls
        self.producer.poll(0)

        # Asynchronously produce a message, the delivery report callback
        # will be triggered from poll() above, or flush() below, when the message has
        # been successfully delivered or failed permanently.
        self.producer.produce(topic, data, callback=delivery_report)

    def flush(self):
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
        self.producer.flush()


class KafkaConsumer:
    def __init__(self, boot_servers, group_id):
        conf = {'bootstrap.servers': boot_servers,
                'group.id': group_id,
                'default.topic.config': {
                    'auto.offset.reset': 'smallest'
                    }
                }

        self.consumer = Consumer(conf)
        self.running = True

    def consume(self, topics, msg_process_callback):
        try:
            self.consumer.subscribe(topics)

            while self.running:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaException(msg.error())

                msg_process_callback(msg.value())

        finally:
            self.consumer.close()

    def stop(self):
        self.running = False
