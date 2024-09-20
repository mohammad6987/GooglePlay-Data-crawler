import json
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from datetime import datetime
from confluent_kafka import Consumer, KafkaException
from confluent_kafka.admin import AdminClient,NewTopic
import os
import time
#database and kafka configurations + list of some apps that will be moved to database during first initialize
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'dbtest'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}
KAFKA_PARAMS = {
    'bootstrap.servers': os.getenv('KAFKA_BROKER' , 'localhost:9092'),
    'group.id': 'app_processing_group',
    'auto.offset.reset': 'earliest'
}
apps_to_insert = [
        ('com.instagram.android', 'Instagram'),
        ('org.telegram.messenger', 'Telegram'),
        ('com.whatsapp', 'WhatsApp Messenger'),
        ('ir.mci.ecareapp', 'MyMCI'),
        ('com.zhiliaoapp.musically' , 'Tik Tok'),
        ('ir.sep.sesoot', '724'),
        ('com.shatelland.namava.mobile' , 'Namava'),
        ('net.telewebion' , 'Telewebion'),
        ('com.BrainLadder.AmirzaGP' , 'آمیرزا'),
        ('com.myirancell' , 'اسمش سخت بود'),
        ('com.plus9.fandogh' , 'فندق'),
        ('com.facebook.katana' , 'FaceBook'),
        ('crossword.hajibadoomgame.persianwordconnect','حدس کلمات'),
        ('com.supercell.clashofclans' , 'Clash of Clans'),
        ('com.supercell.clashroyale' , 'Clash Royale'),
        ('com.supercell.boombeach' , 'Boom Beach'),
        ('com.viber.voip' , 'Viber'),
        ('com.nekki.shadowfight' , 'Shadow Fight 2'),
        ('com.nekki.shadowfight3' , 'Shadow Fight 3'),
        ('com.nekki.vector' , 'Vector'),
        ('com.activision.callofduty.warzone' , 'Call of Duty®: Warzone™ Mobile'),
        ('com.activision.callofduty.shooter','Call of Duty: Mobile'),

        # add more apps here for static instert during initialization 
    ]

def connect_to_db():
    #establish a connection to the database
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("Connection to PostgreSQL successful.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

def save_app_info_in_database(app_info, conn):
    #save application information into the database.
    try:
        cursor = conn.cursor()
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = '''
        INSERT INTO apps_info_history (
            app_id, title, min_installs, score, ratings, reviews_count, updated, version, ad_supported, time_stamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        if(app_info['app_id'] == None):
            print('Null value for app_id, aborintg this app insertion',flush=True)
            return
        cursor.execute(query, [
            app_info['app_id'], app_info['title'], app_info['min_installs'],
            app_info['score'], app_info['ratings'], app_info['reviews_count'],
            app_info['updated'], app_info['version'], app_info['ad_supported'], current_timestamp
        ])
        #update values in apps_info table to new values from currnt crawl
        query = '''
        INSERT INTO apps_info (
            app_id, app_name, min_installs, score, ratings, reviews_count, updated, version, ad_supported
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (app_id) DO UPDATE
        SET app_name = EXCLUDED.app_name,
            min_installs = EXCLUDED.min_installs,
            score = EXCLUDED.score,
            ratings = EXCLUDED.ratings,
            reviews_count = EXCLUDED.reviews_count,
            updated = EXCLUDED.updated,
            version = EXCLUDED.version,
            ad_supported = EXCLUDED.ad_supported

        '''
        cursor.execute(query, [
            app_info['app_id'], app_info['title'], app_info['min_installs'],
            app_info['score'], app_info['ratings'], app_info['reviews_count'],
            app_info['updated'], app_info['version'], app_info['ad_supported']
        ])
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error saving app info to PostgreSQL: {e}")


def save_app_reviews_in_database(app_reviews, app_id, conn):
    #at first check for table if it is avaiable or not
    try:
        cursor = conn.cursor()
        create_table_query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {table_name} (
            review_id VARCHAR PRIMARY KEY,
            userName VARCHAR, 
            content TEXT,
            score FLOAT,
            at VARCHAR,
            thumbsUpCount INT
        )
        """).format(table_name=sql.Identifier(app_id))
        cursor.execute(create_table_query)
        
        #empty the table before inserting new reviews
        truncate_table_query = sql.SQL("TRUNCATE TABLE {table_name}").format(table_name=sql.Identifier(app_id))
        cursor.execute(truncate_table_query)
        
        #insert reviews into the table
        insert_query = sql.SQL("""
        INSERT INTO {table_name} (review_id, userName, score, content, at, thumbsUpCount)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (review_id) DO UPDATE
        SET thumbsUpCount = EXCLUDED.thumbsUpCount
        """).format(table_name=sql.Identifier(app_id))
        
        for review in app_reviews:
            #print(review)  #uncomment this line for debug purposes?
            cursor.execute(insert_query, [
                review.get('reviewId'),
                review.get('userName'),
                review.get('score'),
                review.get('content'),
                review.get('at'),  
                review.get('thumbsUpCount'),
            ])
        
        conn.commit()
        print(f"Reviews for app ID {app_id} saved to PostgreSQL." ,flush=True)
    
    except psycopg2.Error as e:
        print(f"Error saving reviews to PostgreSQL: {e}" , flush=True)


def handle_message(message, conn):
    #sending data to specific functions related to their topic
    try:
        message_data = json.loads(message.value().decode('utf-8'))
        action = message_data.get('action')
        
        if action == 'save_app_info':
            save_app_info_in_database(message_data, conn)
        
        elif action == 'save_app_reviews':
            save_app_reviews_in_database(message_data['reviews'], message_data['app_id'], conn)
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON message: {e}" , flush=True)

def create_topics(admin_client , topics):
  try:
    #creating kafka topics if they already doesn't exist
    new_topics = [NewTopic(topic, num_partitions=1, replication_factor=1) for topic in topics]
    admin_client.create_topics(new_topics)
    print(f"Topics created: {', '.join(topics)}" , flush=True)
    return True
  except KafkaException as e:
    print(f"Error creating Kafka topics: {e}" , flush=True)
    return False
  


def init_query(conn, app_data):
    #craeting essentail tables in the database if they don't exist in the begening of service
    try: 
        cursor = conn.cursor()
        create_apps_info_table = """
        CREATE TABLE IF NOT EXISTS apps_info (
            app_id VARCHAR PRIMARY KEY,
            app_name VARCHAR,
            min_installs BIGINT,
            score REAL, 
            ratings INT,
            reviews_count INT,
            updated INT,
            version VARCHAR,
            ad_supported BOOLEAN
        );
        """

        create_apps_info_history_table = """
        CREATE TABLE IF NOT EXISTS apps_info_history (
            id SERIAL PRIMARY KEY,
            app_id VARCHAR,
            title VARCHAR,
            min_installs BIGINT,
            score REAL, 
            ratings INT,
            reviews_count INT,
            updated INT,
            version VARCHAR,
            ad_supported BOOLEAN,
            time_stamp TIMESTAMP
        );
        """

        cursor.execute(create_apps_info_table)
        cursor.execute(create_apps_info_history_table)

        insert_query = """
        INSERT INTO apps_info (app_id, app_name)
        VALUES %s
        ON CONFLICT (app_id) DO NOTHING;
        """
        #inserting all reserved apps at once into the database
        execute_values(cursor, insert_query, app_data)
        conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}" , flush=True)
    

    
def main():
    print('starting dbms service',flush=True)
    conn = connect_to_db()
    if conn is None:
        print("Exiting due to connection issues.",flush=True)
        return
    init_query(conn , apps_to_insert)
    topics = ['app_info_topic', 'app_reviews_topic']
    try:
        admin_client = AdminClient({'bootstrap.servers': KAFKA_PARAMS['bootstrap.servers']})
        create_topics(admin_client= admin_client, topics=topics) 
        time.sleep(10)#waiting for the changes to be applied on kafka broker
        consumer = Consumer(**KAFKA_PARAMS)
        print('created consumer' , flush=True)
        consumer.subscribe(topics)
        print('subscribed to topics' , flush=True)
        while True:
            msg = consumer.poll()
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            print('got new message' , flush=True)
            handle_message(msg, conn)
            
    
    except KeyboardInterrupt:
        print("Interrupted by user")
    
    finally:
        consumer.close()
        conn.close()
        print('all connections are closed')

if __name__ == '__main__':
    main()
