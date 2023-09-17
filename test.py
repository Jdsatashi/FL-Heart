import redis

r = redis.Redis.from_url('redis://localhost:6379/0')

try:
    ping = r.ping()
    print(f'Connected to Redis Server: {ping}')
except Exception as e:
    print(f'Error connecting to Redis: {e}')
