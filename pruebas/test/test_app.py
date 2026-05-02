#importamos pytest 
import pytest

"""para realizar las pruebas unitarias. Cada función de prueba verifica 
un caso específico de la función sumar, asegurando que el resultado sea el esperado."""
from test_app import sumar

#creamos funciones para probar la función sumar con diferentes casos de prueba.
def test_sumar():
    assert sumar(2, 2) == 4

def test_sumar_negativos():
    assert sumar(-1, -1) == -2

def test_sumar_cero():
    assert sumar(0, 5) == 5

def test_sumar_decimales():
    assert sumar(1.5, 2.5) == 4.0