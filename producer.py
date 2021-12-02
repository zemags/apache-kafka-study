import time

from faker import Faker
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=[
    'localhost:9092', 'localhost:9093', 'localhost:9094'
])
fake = Faker()

for _ in range(100):
    name = fake.name()
    producer.send('names', name.encode('utf-8'))
    print(name)

time.sleep(20)
