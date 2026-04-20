#importamos la funcion pytest para realizar las pruebas unitarias
import pytest

#importo la funcion validar_mensaje para probarla
from funcion_validacion import ref_validar_mensaje as r

def test_validar_mensaje():

    #caso de prueba 1: mensaje vacio
    assert r("") == False

    #caso de prueba 2: mensaje con solo espacios
    assert  r("   ") == False

    #caso de prueba 3: mensaje con mas de 200 caracteres
    mensaje_largo = "a" * 201
    assert  r(mensaje_largo) == False

    #caso de prueba 4: mensaje valido
    assert  r("Hola, este es un mensaje valido.") == True
