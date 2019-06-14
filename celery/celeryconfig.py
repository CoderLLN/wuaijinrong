from kombu import Exchange, Queue

# 配置时区
CELERY_TIMEZONE = 'Asia/Shanghai'
BROKER_URL = 'amqp://admin:123123@10.10.20.88//'
CELERY_RESULT_BACKEND = 'redis://10.10.20.88:6379/0'

# 定义一个媒体交换机
media_exchange = Exchange('media', type='direct')


# 创建三个队列，一个是默认队列，一个是video、一个image
CELERY_QUEUES = (
    Queue('slaver-0', media_exchange, routing_key='media.slaver-0'),
    Queue('slaver-1', media_exchange, routing_key='media.slaver-1'),
    Queue('slaver-2', media_exchange, routing_key='media.slaver-2'),
    Queue('slaver-3', media_exchange, routing_key='media.slaver-3')

)

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'

CELERYD_CONCURRENCY = 10

# 将任务映射到队列上
CELERY_ROUTES = ({'tasks.slaver_0_search': {
                        'queue': 'slaver-0',
                        'routing_key': 'media.slaver-0'
                 }},
                 {'tasks.slaver_1_search': {
                        'queue': 'slaver-1',
                        'routing_key': 'media.slaver-1'
                 }},
                 {'tasks.slaver_2_search': {
                        'queue': 'slaver-2',
                        'routing_key': 'media.slaver-2'
                 }},
                 {'tasks.slaver_3_search': {
                     'queue': 'slaver-3',
                     'routing_key': 'media.slaver-3'
                 }},
)

# 在出现worker接受到的message出现没有注册的错误时，使用下面一句能解决

CELERY_IMPORTS = ("tasks",)

