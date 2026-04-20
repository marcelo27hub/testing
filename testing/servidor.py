"""IP	La dirección de la casa
Puerto	La puerta específica de la casa
Cliente	Invitado que llama a la puerta
Servidor	Persona que abre la puerta y recibe al invitado"""
import socket #enchufe virtual 
import select #para monitorear multiples sockets
import threading

IP_LOCAL= '127.0.0.1' #solo mi computadora
PUERTO = 5000  # un canal de comunicación específico dentro de una computadora.


def difundir_en_chat(mensaje,clientes, lista_de_sockets, quien_envio=None):
    # Para cada cliente conectado
    for c in list(clientes.keys()):
        # Si este cliente no es el que envió el mensaje
        if c != quien_envio:
            try:
                #mandamos los bytes del cliente al chat
                c.send(mensaje)
            except (ConnectionResetError, OSError):
                try:
                    #desactivo completamente la conexion, no puede enviar ni recibir datos
                    c.shutdown(socket.SHUT_RDWR)
                    # Si falla, cerrar la conexión de este cliente
                    c.close()
                    # Sacarlo de la lista de sockets que monitoreamos
                except (ConnectionResetError, OSError):
                    pass
                #si falla el envio o si ya estaban cerrados los eliminamos del servidor
                if c in lista_de_sockets:
                    lista_de_sockets.remove(c)
                clientes.pop(c, None)
                    
                    
def apagar_servidor(servidor_socket, lista_de_sockets, clientes, activo):
    print("\nApagando servidor, cerrando conexiones...")

    activo["value"] = False  # Detener el ciclo principal del servidor
    #para cerrar a todos los clientes
    for c in list(clientes.keys()):
        try:
            c.send("\n Servidor se está apagando.".encode('utf-8'))
            c.shutdown(socket.SHUT_RDWR)
            c.close()
        except (ConnectionResetError, OSError):
            pass

    clientes.clear()  # Limpiar la lista de clientes
    lista_de_sockets.clear()  # Limpiar la lista de sockets

    try:
        servidor_socket.close()
    except (ConnectionResetError, OSError):
        pass
    print("Servidor cerrado correctamente.")


    #para iniciar el servidor
def iniciar_servidor():

    #asociamos (ipv4 + tcp un protocolo confiable que me garantiza seguridad
    # y que los mensajes me llegue en orden)
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #configuramos el servidor para que trabaje por si mismo y se reuse el ip y el puerto despues de cerrar el servidor
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

    #hacemos que nuestro servidor pueda escuchar nuevas clonexiones con una ip y un puerto 
    servidor_socket.bind((IP_LOCAL, PUERTO))

    #ponemos nuestro servidor en modo escucha
    servidor_socket.listen()

    lista_de_sockets = [servidor_socket] #lista de sockets que vamos a monitorear, empezamos con el servidor
    clientes = {} #diccionario para guardar los clientes conectados y sus nombres   
    activo = {"value": True}  # Variable para controlar el ciclo principal del servidor
    print(f"Servidor escuchando en {IP_LOCAL}: {PUERTO}...")


    #hilo de ejecucion en paralelo empieza desde comando servidor, y muere todo star()  que el hilo ya esta iniciado               
    # thread de comandos
    threading.Thread(
        args=(lambda: apagar_servidor(servidor_socket, clientes, lista_de_sockets, activo),),
        daemon=True
    ).start()
    try:
        while activo["value"]:
            try:

                sockets_listos, _, sockets_problematicos = select.select(lista_de_sockets, [], lista_de_sockets, 1) #revisar los que tienen datos para leer y los que tienen errores
            except(KeyboardInterrupt, OSError):
                break   

            #iterar por todos los sockets listos
            for socket_notificado in sockets_listos:
                #para los que se quieren conectar
                if socket_notificado == servidor_socket: # Si el socket listo es el servidor, significa que un nuevo cliente quiere conectarse

                        nuevo_cliente, direccion = servidor_socket.accept()
                        print(f"Nuevo cliente conectado desde {direccion[0]}:{direccion[1]}")

                        nuevo_cliente.send("Bienvenido! Escribí tu nombre de usuario: ".encode('utf-8'))
                        lista_de_sockets.append(nuevo_cliente)
                        clientes[nuevo_cliente] = None  #el nombre aun no lo sabemos
                        

                # Procesamos mensajes de clientes ya conectados
                else:
                    try:
                        mensaje = socket_notificado.recv(1024)
                        if not mensaje:
                            lista_de_sockets.remove(socket_notificado)
                            clientes.pop(socket_notificado, None)
                            continue

                        if clientes.get(socket_notificado) is None:  # Si el cliente aún no ha enviado su nombre
                            nombre = mensaje.decode().strip()

                            if not nombre:
                                continue

                            clientes[socket_notificado] = nombre
                            socket_notificado.send(f"\nBienvenido {nombre}".encode())
                            mensaje_union = f"{nombre} se unió al chat"
                            print(mensaje_union)
                            difundir_en_chat(mensaje_union.encode(), clientes, lista_de_sockets, socket_notificado)

                        else:
                            nombre = clientes[socket_notificado]
                            texto = mensaje.decode().strip()

                            print(f"{nombre}: {texto}") 

                            # manejar comando primero
                            if texto.lower() == "/salir":
                                print(f"{nombre} salió del chat")

                                clientes.pop(socket_notificado, None)
                                if socket_notificado in lista_de_sockets:
                                    lista_de_sockets.remove(socket_notificado)

                                socket_notificado.close()

                                difundir_en_chat(
                                    f"{nombre} salió del chat".encode(),
                                    clientes,
                                    lista_de_sockets,
                                    socket_notificado
                                )

                            else:
                                difundir_en_chat(
                                    f"{nombre}: {texto}".encode(),
                                    clientes,
                                    lista_de_sockets,
                                    socket_notificado
                                )

                    except (ConnectionResetError, OSError):
                        if socket_notificado in lista_de_sockets:
                            lista_de_sockets.remove(socket_notificado)
                        clientes.pop(socket_notificado, None)  


    except KeyboardInterrupt:

        print("\nServidor interrumpido por el usuario.") 

if __name__ == "__main__":  
    iniciar_servidor() 

