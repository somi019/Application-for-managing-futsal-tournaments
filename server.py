import socket
import sqlite3
import json
from threading import Thread

class Server:
        def __init__(self,host='localhost',port=8001):
            self.host = host
            self.port = port
            self.db_path = "liga.db"
            self.conn = sqlite3.connect('liga.db')
            self.create_tables()
        
        def create_tables(self):
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS utakmice(
                    id INTEGER PRIMARY KEY,
                    datum TEXT,
                    vreme TEXT,
                    tim1 TEXT,
                    tim2 TEXT,
                    rezultat TEXT
                )
                '''
            )
            self.conn.commit()
            
        def handle_client(self,client_socket):
            with sqlite3.connect(self.db_path) as conn:
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    req = json.loads(data)
                    if req['action'] == 'add_game':
                        self.add_game(conn,req['data'])
                    elif req['action'] == 'get_games':
                        games = self.get_games(conn)
                        client_socket.send(json.dumps(games).encode('utf-8'))
                except Exception as e:
                    print(f"Error : {e}")
                finally:
                    client_socket.close()
        
        def add_game(self,conn,data):
            cursor = conn.cursor()
            cursor.execute('INSERT INTO utakmice (datum,vreme,tim1,tim2,rezultat) VALUES (?,?,?,?,?)',(data['datum'],data['vreme'],data['tim1'],data['tim2'],data['rezultat']))
            conn.commit()

        def get_games(self,conn):
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM utakmice')
            return cursor.fetchall()

        def start(self):
            server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            server_socket.bind((self.host,self.port))
            server_socket.listen(5)
            print(f"Server is listening on {self.host} : {self.port}")
            
            while True:
                client_socket,addr = server_socket.accept()
                print(f"Connection from {addr}")
                client_handler = Thread(target = self.handle_client,args=(client_socket,))
                client_handler.start()

if __name__ == "__main__":
    server = Server()
    server.start()