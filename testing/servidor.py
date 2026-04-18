"""IP	La dirección de la casa
Puerto	La puerta específica de la casa
Cliente	Invitado que llama a la puerta
Servidor	Persona que abre la puerta y recibe al invitado"""


import socket #enchufe virtual 
import select #para monitorear multiples sockets
import threading

IP_LOCAL= '127.0.0.1' #solo mi computadora
PUERTO = 5000  # un canal de comunicación específico dentro de una computadora.

#asociamos (ipv4 + tcp un protocolo confiable que me garantiza seguridad
# y que los mensajes me llegue en orden)
servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#configuramos el servidor para que trabaje por si mismo y se reuse el ip y el puerto despues de cerrar el servidor
servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

#hacemos que nuestro servidor pueda escuchar nuevas clonexiones con una ip y un puerto 
servidor_socket.bind((IP_LOCAL, PUERTO))

#ponemos nuestro servidor en modo escucha
servidor_socket.listen()


lista_de_sockets = [servidor_socket]  # lista de sockets a monitorizar
clientes = {}  #  nombre de usaurio
activo = True #el servidor ta encendido 



print(f"Servidor escuchando en {IP_LOCAL}: {PUERTO}...")

def difundir_en_chat(mensaje, quien_envio=None):
    # Para cada cliente conectado
    for cliente_socket in list(clientes.keys()):
        # Si este cliente no es el que envió el mensaje
        if cliente_socket != quien_envio:
            try:
                #mandamos los bytes del cliente al chat
                cliente_socket.send(mensaje)
            except:
                try:
                    #desactivo completamente la conexion, no puede enviar ni recibir datos
                    cliente_socket.shutdown(socket.SHUT_RDWR)
                    # Si falla, cerrar la conexión de este cliente
                    cliente_socket.close()
                    # Sacarlo de la lista de sockets que monitoreamos
                except:
                    pass
                #si falla el envio o si ya estaban cerrados los eliminamos del servidor
                if cliente_socket in lista_de_sockets:
                    lista_de_sockets.remove(cliente_socket)
                if cliente_socket in clientes:
                    del clientes[cliente_socket]
                    
                    
def apagar_servidor():
    #para apagar el servidor
    """Cierra todas las conexiones y el socket principal."""
    global activo 
    if not activo:
        return
    activo = False
    print("\nApagando servidor, cerrando conexiones...")
    #para cerrar a todos los clientes
    for cliente_socket in list(clientes.keys()):
        try:
            cliente_socket.send("\n Servidor se está apagando.".encode('utf-8'))
            cliente_socket.shutdown(socket.SHUT_RDWR)
            cliente_socket.close()
        except:
            pass
        if cliente_socket in lista_de_sockets:
            lista_de_sockets.remove(cliente_socket)
        if cliente_socket in clientes:
            del clientes[cliente_socket]

    try:
        servidor_socket.close()
    except:
        pass
    print("Servidor cerrado correctamente.")

def comandos_servidor():
    #para apagar por comando 
    """Permite apagar manualmente el servidor desde consola."""
    while True:
        try:
            cmd = input("Servidor (escribe 'salir' para apagar): ").strip().lower()
            if cmd == "salir":
                apagar_servidor()
                break
        except (EOFError, KeyboardInterrupt):
            apagar_servidor()
            break    
#hilo de ejecucion en paralelo empieza desde comando servidor, y muere todo star()  que el hilo ya esta iniciado               
threading.Thread(target=comandos_servidor, daemon=True).start()
try:
    while activo:
        
        sockets_listos, _, sockets_problematicos = select.select(lista_de_sockets, [], lista_de_sockets) #revisar los que tienen datos para leer y los que tienen errores
        
        #iterar por todos los sockets listos
        for socket_notificado in sockets_listos:
            #para los que se quieren conectar
            if socket_notificado == servidor_socket: # Si el socket listo es el servidor, significa que un nuevo cliente quiere conectarse
                try:
                    nuevo_cliente, direccion_del_cliente = servidor_socket.accept()
                except OSError:
                    continue
                nuevo_cliente.send("Bienvenido! Escribí tu nombre de usuario: ".encode('utf-8'))
                lista_de_sockets.append(nuevo_cliente)
                clientes[nuevo_cliente] = None  #el nombre aun no lo sabemos
                
                    
            
            # Procesamos mensajes de clientes ya conectados
            else:
                try:
                    mensaje = socket_notificado.recv(1024)
                    if not mensaje:
                        #el cliente se desconecto si no hay mensaje
                        nombre = clientes[socket_notificado] or "Cliente desconocido"
                        print(f"cliente {nombre} se deconecto! ")
                        #lo sacamos de la lista de sockets
                        if socket_notificado in lista_de_sockets:
                            lista_de_sockets.remove(socket_notificado)
                        if socket_notificado in clientes:
                            del clientes[socket_notificado]
                        difundir_en_chat(f"\n{nombre} se desconectó.".encode('utf-8'))
                        continue
                    #revisamos si el cliente aun no tiene nombre 
                    if clientes[socket_notificado] is None:
                        #cambiamos a string los bytes
                        nombre = mensaje.decode('utf-8').strip()
                        while not nombre:
                            socket_notificado.send("Debe escribir un nombre de usuario:\n".encode('utf-8'))
                            nombre = socket_notificado.recv(1024).decode('utf-8').strip()
                        clientes[socket_notificado] = nombre
                        direccion = socket_notificado.getpeername()
                        socket_notificado.send(f"¡Hola {nombre}! Ahora podés enviar mensajes.\nEscribe '/salir' para desconectarte.\n".encode('utf-8'))
                        mensaje_union = f"\n{nombre} se unió al chat."
                        difundir_en_chat(mensaje_union.encode('utf-8'), quien_envio=socket_notificado)
                        print(f"{mensaje_union} (desde {direccion[0]}:{direccion[1]})")
                    else:
                        #ya esta conectado al chat y ya tiene nombre
                        nombre = clientes[socket_notificado]
                        texto = mensaje.decode('utf-8').strip()
                        if texto.lower() == "/salir": #para que el cliente salga
                            socket_notificado.send("\nTe desconectaste del chat.\n".encode('utf-8'))
                            try:
                                socket_notificado.shutdown(socket.SHUT_RDWR)
                                socket_notificado.close()
                            except:
                                pass
                            if socket_notificado in lista_de_sockets:
                                lista_de_sockets.remove(socket_notificado)
                            if socket_notificado in clientes:
                                del clientes[socket_notificado]
                            mensaje_desconexion = f"\n{nombre} se desconectó."
                            difundir_en_chat(mensaje_desconexion.encode('utf-8'))
                            print(mensaje_desconexion)
                        else:
                            #si no se quiere salir pues sigue mandanos mensajes normales
                            difundir_en_chat(f"{nombre}: {texto}".encode('utf-8'), quien_envio = socket_notificado)
                            # Mostrar mensaje en servidor también
                            print(f"{nombre}: {texto}")
                except:
                    #si ocurre un error al recibir un mensaje o procesar mensaje
                    if socket_notificado in lista_de_sockets:
                        lista_de_sockets.remove(socket_notificado)
                    if socket_notificado in clientes:
                        del clientes[socket_notificado]
                    continue
                
                
        # Manejar sockets problemáticos
        for socket_notificado in sockets_problematicos:
            if socket_notificado in lista_de_sockets:
                lista_de_sockets.remove(socket_notificado)
            if socket_notificado in clientes:
                del clientes[socket_notificado]     

except KeyboardInterrupt:
    apagar_servidor()
                    