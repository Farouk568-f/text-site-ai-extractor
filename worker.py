# worker.py
from redis import Redis
from rq import Worker, Queue # تم حذف Connection

# Define which queues this worker should listen to
listen = ['article_fetcher']

redis_conn = Redis.from_url('redis://localhost:6379')

if __name__ == '__main__':
    # لم نعد بحاجة إلى `with Connection(...)`
    print("✅ Worker is starting...")
    print(f"Listening on queues: {', '.join(listen)}")

    # قم بإنشاء قائمة من كائنات Queue
    queues = [Queue(name, connection=redis_conn) for name in listen]
    
    # مرر الاتصال مباشرة إلى العامل
    worker = Worker(queues, connection=redis_conn)
    
    # ابدأ العمل
    worker.work()