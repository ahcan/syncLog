import pika

pika.BasicProperties
class RabbitQueue:
    def __init__(self, route_key):
        self.routing_key = route_key

    def __connect__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.queue = self.channel.queue_declare(queue= self.routing_key)

    def push_queue(self, message):
        self.__connect__()
        self.channel.basic_publish(exchange='',
            routing_key = self.routing_key,
            properties=pika.BasicProperties(delivery_mode=2,),
            body = message)
        self.connection.close()
        return ""

    def get_queue(self):
        self.__connect__()
        self.channel = self.connection.channel()
        result = []
        for i in range(self.queue.method.message_count):
            body = self.channel.basic_get(queue=self.routing_key, no_ack=True) # get queue basic with single queue
            result.append(body)
        self.connection.close()
        return result
