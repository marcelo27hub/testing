#funcion para validar mensaje

def validar_mensaje(mensaje):

    if not mensaje.strip() :
        return False
    
    
    if len(mensaje) > 200:
        return False
    
    return True

#funcion refactorizada 
def ref_validar_mensaje(texto: str) -> bool:
    mensaje = texto.strip()
    return bool(mensaje) and len(mensaje) <= 200