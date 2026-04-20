# librerias a usar
import threading
import time
import socket
from servidor import iniciar_servidor


HOST= 'localhost'
PORT = 5000


# funcion para recibir todo el mensaje del servidor
def recibir_todo(cliente):

    cliente.settimeout(1)  # Establecer un tiempo de espera para evitar bloqueos
    mensajes = ""
    try:
        while True:
            mensajes += cliente.recv(4096).decode()
    except:
        pass    
    return mensajes


# funcion para levantar mi servidor
def test_dos_clientes_se_conectan():
    """Prueba de integración: 
    levantar el servidor y verificar que
    dos clientes se conectan,
    uno envía un mensaje y 
    el otro lo recibe
    """

    hilo = threading.Thread(target=iniciar_servidor, daemon=True)
    hilo.start()
    time.sleep(1)  # Esperar un momento

    # cliente 1
    cliente1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente1.connect((HOST, PORT))

    # cliente 2
    cliente2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
    cliente2.connect((HOST, PORT))

    # cliente3
    cliente3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente3.connect((HOST, PORT))


    # recibir mensaje de bienvenida
    cliente1.recv(1024)
    cliente2.recv(1024)
    cliente3.recv(1024)

    # mandar nombre de usuario
    cliente1.send(b"marce")
    cliente2.send(b"ana")
    cliente3.send(b"pepe")

    time.sleep(1)  # Esperar un momento para que el servidor procese los nombres

    # recibir mensajes de bienvenida
    recibir_todo(cliente1)     
    recibir_todo(cliente2) 
    recibir_todo(cliente3) 


    # cliente 1 envia mensaje
    cliente1.send(b"Hola")
    time.sleep(1)


    
    cliente1.send(b"que tal?")  
    time.sleep(1)

    cliente1.send(b"soy marce")
    time.sleep(1)

    # cliente 2 deveria de recibir el mensaje de cliente 1
    mensaje2= recibir_todo(cliente2)
    mensaje3 = recibir_todo(cliente3)

    # verificamos que el mensaje de cliente1 llego a cliente2 y cliente3    
    assert "marce: Hola" in mensaje2
    assert "marce: Hola" in mensaje3

    assert "marce: que tal?" in mensaje2
    assert "marce: que tal?" in mensaje3

    assert "marce: soy marce" in mensaje2
    assert "marce: soy marce" in mensaje3

    # cerramos al cliente1
    cliente1.close()
    time.sleep(1)
    
    # cliente2 envia mensaje
    cliente2.send(b"sigo vivo")
    time.sleep(1)

    # cliente 3 deveria de recibir el mensaje de cliente2
    mensaje_post = recibir_todo(cliente3)

    # verificamos que el mensaje de cliente2 llego a cliente3
    assert "ana: sigo vivo" in mensaje_post



def test_mensaje_invalido():
    """Prueba de integración: 
    levantar el servidor y verificar que
    un cliente se conecta, 
    envía un mensaje inválido y 
    el servidor no lo difunde
    """

    hilo = threading.Thread(target=iniciar_servidor, daemon=True)
    hilo.start()
    time.sleep(1)

    # cliente 1
    cliente1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente1.connect((HOST, PORT))

    # recibir mensaje de bienvenida
    cliente1.recv(1024)

    # mandar nombre de usuario
    cliente1.send(b"marce")
    time.sleep(1)

    # recibir mensaje de bienvenida
    recibir_todo(cliente1)

    # cliente 1 envia mensaje invalido
    cliente1.send(b"   ")
    time.sleep(1)

    # cliente 1 deveria no recibir su propio mensaje
    mensaje = recibir_todo(cliente1)
    
    assert "marce:   " not in mensaje