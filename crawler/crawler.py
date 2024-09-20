import json
import psycopg2
from psycopg2 import sql
from google_play_scraper import app, reviews, Sort
from confluent_kafka import Producer
import os
import time
#database and kafka configurations
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'dbtest'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}
KAFKA_PARAMS = {
    'bootstrap.servers': os.getenv('KAFKA_BROKER' , 'localhost:9092'),
}
KAFKA_TOPICS = {
    'app_info': 'app_info_topic',
    'app_reviews': 'app_reviews_topic'
}
SMALL_PARAMS = {
    'break.cycle' : os.getenv('CYCLE_BREAK' , 900)
}

def connect_to_db():
    #establish a connection to the postgreSQL database
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("Connection to PostgreSQL successful.", flush=True)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}", flush=True)
        return None

def get_apps_from_database(conn, table_name):
    #retrieve app details from the database
    try:
        with conn.cursor() as cursor:
            query = sql.SQL('SELECT app_name, app_id FROM {table};').format(
                table=sql.Identifier(table_name)
            )
            cursor.execute(query)
            results = cursor.fetchall()
            return [{'app_name': row[0], 'app_id': row[1]} for row in results]
    except psycopg2.Error as e:
        print(f"Error retrieving apps from database: {e}", flush=True)
        return []

def get_app_info(app_id):
    #fetch app information from Google Play
    try:
        app_info = app(app_id, lang='en', country='us')
        print(f"Got app info {app_id}", flush=True)
        return app_info
    except Exception as e:
        print(f"Error fetching app info: {e}" , flush=True)
        return {}

def get_app_reviews(app_id):
    #fetch last 1000 reviews for each app
    try:
        app_reviews = reviews(app_id, lang='en', country='us', sort=Sort.NEWEST, count=1000)
        print(f"Got app reviews for {app_id}" , flush=True)
        return app_reviews
    except Exception as e:
        print(f"Error fetching app reviews: {e}")
        return [[], []]  

def send_to_kafka(producer, topic, message):
   
    try:
        producer.produce(topic, key=str(message['app_id']), value=json.dumps(message))
        producer.flush()
        print(f"Message sent to Kafka topic '{topic}'" , flush=True)
    except Exception as e:
        print(f"Error sending message to Kafka: {e}", flush=True)

def main():
    print("Main function started")
    conn = connect_to_db()
    if conn is None:
        return

    apps_list = get_apps_from_database(conn, 'apps_info')
    #print(apps_list)  #uncomment this line to see list of registerd apps in the database
    kafka_producer = Producer(**KAFKA_PARAMS)

    for app_data in apps_list:
        app_id = app_data['app_id']
        app_info = get_app_info(app_id)
        time.sleep(3)
        app_reviews = get_app_reviews(app_id)
        time.sleep(3)
        #create messages for kafka
        app_info_message = {
            'action': 'save_app_info',
            'app_id': app_info.get('appId'),
            'title': app_info.get('title'),
            'min_installs': app_info.get('realInstalls'),
            'score': app_info.get('score'),
            'ratings': app_info.get('ratings'),
            'reviews_count': app_info.get('reviews'),
            'updated': app_info.get('updated'),
            'version': app_info.get('version'),
            'ad_supported': app_info.get('adSupported')
        }

        app_reviews_message = {
            'action': 'save_app_reviews',
            'app_id': app_id,
            'reviews': [
                {
                    'reviewId': review.get('reviewId'),
                    'userName': review.get('userName'),
                    'score': review.get('score'),
                    'content': review.get('content'),
                    'at': review.get('at').isoformat(),
                    'thumbsUpCount': review.get('thumbsUpCount')
                }
                for review in app_reviews[0]
            ]
        }

        #send messages to kafka broker
        send_to_kafka(kafka_producer, KAFKA_TOPICS['app_info'], app_info_message)
        send_to_kafka(kafka_producer, KAFKA_TOPICS['app_reviews'], app_reviews_message)
        time.sleep(5) #time laps between loops to reduce queues workload
    print('end of crawl' , flush=True)
    conn.close()
    
def schedule_tasks():  
    
    print("Scheduler started.", flush=True)
    cycle = SMALL_PARAMS['break.cycle']
    print(f'cycle = {cycle}')
    while True:
        try:
            main()
            time.sleep(cycle)
        except KeyboardInterrupt:
            break    


if __name__ == '__main__':
    schedule_tasks()
