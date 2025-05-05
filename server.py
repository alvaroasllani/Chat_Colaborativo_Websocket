#!/usr/bin/env python

import asyncio
import json
import logging
import websockets
import uuid
import datetime
import time

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Almacenamiento de conexiones activas (cliente_id -> websocket)
CONNECTED_CLIENTS = {}

# Contador global para asignar nombres de usuario automáticamente
USUARIOS_COUNTER = 0

# Historial de mensajes (máximo 50 mensajes)
MESSAGE_HISTORY = []
MAX_HISTORY = 50

# Control de tiempo de inactividad
LAST_ACTIVITY_TIME = time.time()
INACTIVITY_TIMEOUT = 600  # 10 minutos en segundos

async def register_client(websocket, client_id, username):
    """Registra un nuevo cliente"""
    global LAST_ACTIVITY_TIME, USUARIOS_COUNTER
    
    # Actualizar tiempo de actividad
    LAST_ACTIVITY_TIME = time.time()
    
    # Si no se proporciona un nombre de usuario, asignar uno automáticamente
    if not username:
        USUARIOS_COUNTER += 1
        username = f"USUARIO_{USUARIOS_COUNTER}"
    
    CONNECTED_CLIENTS[client_id] = {"websocket": websocket, "username": username}
    
    # Notificar a todos los clientes que se ha unido un nuevo usuario
    join_message = {
        "type": "system",
        "content": f"{username} se ha unido al chat!",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "username": "System"
    }
    
    # Guardar en historial
    MESSAGE_HISTORY.append(join_message)
    if len(MESSAGE_HISTORY) > MAX_HISTORY:
        MESSAGE_HISTORY.pop(0)
    
    # Enviar notificación a todos
    await notify_all_clients(join_message)
    
    # Enviar historial al nuevo cliente
    await send_message_history(websocket)
    
    # Devolver el nombre asignado para que el cliente lo sepa
    return username

async def unregister_client(client_id):
    """Elimina un cliente desconectado"""
    if client_id in CONNECTED_CLIENTS:
        username = CONNECTED_CLIENTS[client_id]["username"]
        del CONNECTED_CLIENTS[client_id]
        
        # Notificar a todos que un usuario se ha desconectado
        leave_message = {
            "type": "system",
            "content": f"{username} ha abandonado el chat.",
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "username": "System"
        }
        
        # Guardar en historial
        MESSAGE_HISTORY.append(leave_message)
        if len(MESSAGE_HISTORY) > MAX_HISTORY:
            MESSAGE_HISTORY.pop(0)
        
        # Notificar a todos
        await notify_all_clients(leave_message)

async def send_message_history(websocket):
    """Envía el historial de mensajes a un cliente"""
    history_message = {
        "type": "history",
        "messages": MESSAGE_HISTORY
    }
    await websocket.send(json.dumps(history_message))

async def notify_all_clients(message):
    """Envía un mensaje a todos los clientes conectados"""
    if CONNECTED_CLIENTS:
        await asyncio.gather(
            *[client_data["websocket"].send(json.dumps(message))
              for client_data in CONNECTED_CLIENTS.values()]
        )

async def chat_handler(websocket, path):
    """Manejador principal de la conexión WebSocket"""
    global LAST_ACTIVITY_TIME
    
    client_id = str(uuid.uuid4())
    username = None
    
    try:
        # Primer mensaje: obtener nombre de usuario
        message = await websocket.recv()
        data = json.loads(message)
        
        # Obtener el nombre de usuario, podría estar vacío
        username = data.get("username", "")
        
        # Registrar el cliente y obtener el nombre asignado (podría ser automático)
        username = await register_client(websocket, client_id, username)
        
        # Informar al cliente su nombre asignado
        if not data.get("username"):
            welcome_message = {
                "type": "system",
                "content": f"Se te ha asignado el nombre: {username}",
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "username": "System"
            }
            await websocket.send(json.dumps(welcome_message))
        
        # Bucle principal de mensajes
        async for message in websocket:
            try:
                # Actualizar tiempo de actividad
                LAST_ACTIVITY_TIME = time.time()
                
                data = json.loads(message)
                
                # Crear objeto de mensaje
                chat_message = {
                    "type": "chat",
                    "content": data["content"],
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                    "username": username
                }
                
                # Guardar en historial
                MESSAGE_HISTORY.append(chat_message)
                if len(MESSAGE_HISTORY) > MAX_HISTORY:
                    MESSAGE_HISTORY.pop(0)
                
                # Enviar a todos los clientes
                await notify_all_clients(chat_message)
                
            except json.JSONDecodeError:
                logging.error("Error al decodificar JSON")
            except Exception as e:
                logging.error(f"Error al procesar mensaje: {e}")
    
    except websockets.exceptions.ConnectionClosedError:
        logging.info(f"Conexión cerrada con cliente {client_id}")
    finally:
        # Desregistrar cliente al desconectarse
        await unregister_client(client_id)

async def check_inactivity():
    """Verifica si el servidor ha estado inactivo por mucho tiempo"""
    while True:
        await asyncio.sleep(30)  # Verificar cada 30 segundos
        
        current_time = time.time()
        elapsed_time = current_time - LAST_ACTIVITY_TIME
        
        # Si no hay clientes conectados y el tiempo de inactividad excede el límite
        if not CONNECTED_CLIENTS and elapsed_time > INACTIVITY_TIMEOUT:
            logging.info(f"Cerrando servidor después de {int(elapsed_time)} segundos de inactividad")
            # Salir de la aplicación
            import sys
            sys.exit(0)
        
        # Mostrar info de tiempo de inactividad cuando se acerca al límite
        if elapsed_time > INACTIVITY_TIMEOUT * 0.8:  # Al 80% del tiempo límite
            logging.info(f"Servidor inactivo por {int(elapsed_time)} segundos. Se cerrará después de {INACTIVITY_TIMEOUT} segundos de inactividad si no hay conexiones.")

async def main():
    # Iniciar servidor WebSocket
    host = "0.0.0.0"  # Acepta conexiones de cualquier IP
    port = 8765
    
    # Iniciar tarea de verificación de inactividad
    inactivity_task = asyncio.create_task(check_inactivity())
    
    async with websockets.serve(chat_handler, host, port):
        print(f"Servidor de chat iniciado en ws://{host}:{port}")
        print(f"El servidor se cerrará automáticamente después de {INACTIVITY_TIMEOUT} segundos de inactividad si no hay usuarios conectados")
        
        try:
            await asyncio.Future()  # Ejecutar indefinidamente
        except asyncio.CancelledError:
            logging.info("Servidor detenido manualmente")
        finally:
            inactivity_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())