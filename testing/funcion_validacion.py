#funcion para validar mensaje

def validar_mensaje(mensaje):

    if not mensaje.strip() :
        return False
    
    
    if len(mensaje) > 200:
        return False
    
    return True

