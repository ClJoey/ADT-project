import os

def limpiar_descargas(path):
    if not os.path.exists(path):
        os.makedirs(path)

    for f in os.listdir(path):
        os.remove(os.path.join(path, f))