import os, redis, psycopg2
from flask import Flask

app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379)

def db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

@app.route("/")
def index():
    hits = r.incr("hits")
    with db() as conn, conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS visits(id serial, ts timestamptz default now())")
        cur.execute("INSERT INTO visits DEFAULT VALUES")
        cur.execute("SELECT count(*) FROM visits")
        total = cur.fetchone()[0]
    return f"Redis hits: {hits} | Postgres visits: {total}\n"

@app.route("/health")
def health():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
