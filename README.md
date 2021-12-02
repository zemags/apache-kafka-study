```bash
mkdir kafka
tar -xvzf kafka.tgz -C kafka
```

#### концепции (продюсер - брокер - консьюмер)
- кафка - распределенная паблиш-сабскрайб сообщений система
- брокер - получает сообщений от продюссеров раскидывает на консьюмеров
- кластер брокеров - несколько брокеров, в случае падения чтобы были запасные, либо разные критерии по типу заданий для каждого брокера
    - брокера синхранизируеются с помозью zookeeper
- zookeeper - контролит брокеров, знает всех брокеров, мэнэджерит конфиги для топиков и партиций
    - кластер зоокиперов - zookeeper cluster (ensemble) - несколько штук
        - quorum - определяет при сколькои неработающих кластеров все падает, целое число
            - нужно чтобы было нечетное число серверов в зукипире
            - quorum = (кол-во сервисов + 1)/2

#### множественные кластеры кафки, то что выше но допустим этих  сущеностей больше
- повышает ээфективность и понижает нагрузку

#### дефолт порты
- зукипер localhost:2181
- кафка localhost:9092
- на каждый зукипер или кафка инстанс свой конфиг

#### кафка топики
- у каждого топика свое имя
- топик это куда помещаются сообщения в порядке прибытия на выход в порядке очереди
- у каждого сообщения свой номер
- старые сообщения дропаются если time expired

#### структура сообщения
- timestamp
- offset number уникальное между партициями
- key - опционально
- value - последовательность байтов
- идея держать сообщения как можно меньше, чтобы достигнуть эффективности кластера апачи

#### топики и партиции
- топик может быть в разных брокерах одновременно
	- это для того чтобы если брокер упал, то другой смог работать с топиком
- партиция - то из чего состоит топик
	- могут быть несколько, и каждая часть партиции на разных брокерах одновременно
	- делять на партиции чтобы, брокеры могли работать быстро с жесктим диском, если дробим топик

#### рассеявать сообщения между партициями
- каждый продюсер может писать в свою партицию, продюсер выбирает
- в случае падения исчезнут сообщения если нет репликации

#### лидер партиции и фоловеры
- лидер брокер создают партицию и клонирует ее на другие брокеры фоловеры, они его реплецируют, чтобы без падний надо чтобы каждое сообщение дважды и были три брокера
- фактор репликации, копии плюс оригинал

#### контроллер и обязанности
- кто решает какой брокер будет лидером, а какие фоловеры
- какой брокер применять на себя реплику партиции если брокер упал и тд
	- это все делает контроллер
	- контроллер - это брокер в кластере, у него просто обязанности для мэнджеринга

#### как продюсер пишет сообщение в топик
- каждый продюсер может писать в разные партиции топика

#### как консьюмер читает сообщения из топика
- читает с партиций(которые могут быть на разных брокерах)
	- ожидания новое сообщения
	- или с самого начала

```bash
kafka/config/producer.properties - start producer
kafka/config/server.properties - server options
kafka/config/zookeeper.properties - run zookeeper
```
```bash
kafka/bin/zookeeper-server-start.sh config/zookeeper.properties - запуск до кафки, слушает 0.0.0.0:2181
kafka/bin/kafka-server-start.sh config/server.properties - запуск кафки
```
	- broker=0 - айди брокера в кластере, слушает 0.0.0.0:9092 дефолтно, можно поменять в kafka/config/server.properties
	- /tmp/kafka-logs - логи сообщений которые в брокере, можно поменять в kafka/config/server.properties

#### kafka/logs/server.log - логи кафки и зоокипера после запуска

#### создание нового топика кафки
- sh bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic cities --partitions 1 --replication-factor 1
	- partitions - это для параллелизма, в папке /tmp/kafka-logs/cities-0, если бы было партиций 2 то было бы еще cities-1

#### описание топика
bin/kafka-topics.sh --describe --zookeeper localhost:2181 --topic cities - просмотр инфы о топике
	 - replicationfactor - реплика сервера дефолт 1

#### коннект к брокеру и создание топика - паблишер
	- bin/kafka-console-producer.sh --broker-list localhost:9092 --topic cities

#### консьюмер
	- bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic cities
	- bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic cities --from-begining чтение с самого начала

- продюссеры не знаю о других продюссерах
- все консьюмеры получат сообщения если продюссер отправил
- каждый консьюмер принадлежит группе консьюмеров

#### где хранятся все сообщения в папке партиции cities-0
- в /tmp/kafka-logs/cities-0/00000(много нулей).log

#### создание трех партиций для нового топика animals
- если послать три сообщения то каждое будет в своей партиции например animals-0, итд
```bash
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic animals --partitions 3 --replication-factor 1
```

#### получение сообщений для конкретной партиции,  данном примере будет одно из трех сообщений
```bash
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092
--partition 1 --topic animals --from-beginning
```

### создание трех брокеров на одной машине
- копируем config/server.properties три раза, и называем
	- в итоге будет
	- server0.properties, оставим broker.id=0 тотже,  меняем log.dirs=/tmp/kafka-logs-0, оставим listeners=PLAINTEXT://:9092
	- server1.properties, меняем broker.id=1, log.dirs=/tmp/kafka-logs-1, listeners=PLAINTEXT://:9093
	- server2.properties, меняем broker.id=2, log.dirs=/tmp/kafka-logs-2, listeners=PLAINTEXT://:9094

- запуск всех трех
```bash
bin/kafka-topics.sh \
--bootstrap-server localhost:9092, localhost:9093, localhost:9094 \
--create \
--replication-factor 1 \
--partitions 5 \
--topic cars
```
#### создание продюсера
```bash
bin/kafka-console-producer.sh \
--bootstrap-server localhost:9092, localhost:9093, localhost:9094 \
--topic cars
```
#### создание консьюмера
```bash
bin/kafka-console-consumer.sh \
--bootstrap-server localhost:9092, localhost:9093, localhost:9094 \
--topic cars
```
#### просмотр - в итоге разные партиции на разных брокерах
```bash
bin/kafka-topics.sh \
--bootstrap-server localhost:9092, localhost:9093, localhost:9094 \
--describe \
--topic cars
```

#### создание почти непадающей системы
```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server0.properties
bin/kafka-server-start.sh config/server1.properties
bin/kafka-server-start.sh config/server2.properties
bin/kafka-topics.sh \
	--bootstrap-server localhost:9092, localhost:9093, localhost:9094 \
	--create \
	--replication-factor 3 \
	--partitions 7 \
	--topic months
```
- в каждом брокере как минимум 7 партиций, всего 7 * 3 = 21
- один брокер только в качестве лидера, другие фоловят

```bash
bin/kafka-topics.sh \
	--bootstrap-server localhost:9092, localhost:9093, localhost:9094 \
	--list
bin/kafka-topics.sh \
	--bootstrap-server localhost:9092, localhost:9093, localhost:9094 \
	--describe \
	--topic months
bin/kafka-console-consumer.sh \
	--bootstrap-server localhost:9092, localhost:9093, localhost:9094 \
	--topic months
bin/kafka-console-producer.sh \
	--broker-list localhost:9092, localhost:9093, localhost:9094 \
	--topic months
```
- порядок поступления и выхода один и тот же - очередь


```bash
- bin/kafka-console-consumer.sh \
	--bootstrap-server localhost:9092, localhost:9093, localhost:9094 \
	--topic months
	--from-beginning
```
- в разном порядке будет выход сообщений от брокеров


```bash
- bin/kafka-console-consumer.sh \
	--bootstrap-server localhost:9092, localhost:9093, localhost:9094 \
	--topic months \
	--partition 3 \
	--from-beginning

- bin/kafka-console-consumer.sh \
	--bootstrap-server localhost:9092, localhost:9093, localhost:9094 \
	--topic months \
	--partition 3 \
	--offset 1
```

- если один брокер упал, все ок, так же будет, упавший лидер переназначится на оставшиеся два
- если упадет второй, то третий вернет значения, но будут предупреждения что два брокера лежат

### группы консьюмеров
- все тоже самое, но один брокер, а дальше создадим топик
```bash 
bin/kafka-topics.sh \
	--bootstrap-server localhost:9092 \
	--create \
	--replication-factor 1 \
	--partitions 5 \
	--topic numbers
```
- запуск продюсера и консьюмера

- просмотр груп консьюмеров - опять же все это если чтото падает, каждый консьюмер получит сообщение от продюсера
```bash
- bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
```
```bash
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group console-consumer-99251 --describe
(console-consumer-99251 из команды списка полученных выше, в качестве примера)
```

- запуск второго консьюмера в той же группе консьюмеров
```bash
- bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic numbers --group numbers-group --from-beginning
```

- если консьюмеров больше чем партиций, то кто-то из консьюмеров будет idle

### нагрузочное тестирование, production ready
```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server0.properties
bin/kafka-server-start.sh config/server1.properties
bin/kafka-server-start.sh config/server2.properties
bin/kafka-topics.sh \
	--bootstrap-server localhost:9092 \
	--create \
	--replication-factor 3 \
	--partitions 100 \
	--topic perf
bin/kafka-console-consumer.sh \
--bootstrap-server localhost:9092 \
--topic 

bin/kafka-producer-perf-test.sh \
--topic perf \
--num-records 1000 \ колько всего сообщений будет создано
--throughput 100 \ в секунду сколько
--record-size 1000 \ размер каждого сообщения 1 кб
--producer-props bootstrap.servers=localhost:9092
```

- тест консьюмера
```bash
bin/kafka-consumer-perf-test.sh \
--broker-list localhost:9092 \
--topic perf \
--messages 10000
```

- LAG - количество сообщений, когда консьюмер не успел еще прочитать из партиции