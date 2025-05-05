# Chat Colaborativo en Tiempo Real con WebSocket

Este proyecto implementa un sistema de chat colaborativo en tiempo real utilizando WebSockets para permitir una comunicación bidireccional persistente entre cliente y servidor.

## Características

- Conexión en tiempo real utilizando WebSockets
- Asignación automática de nombres de usuario si no se proporciona uno
- Notificaciones cuando usuarios se unen o abandonan el chat
- Historial de mensajes (últimos 50 mensajes)
- Visualización clara de qué usuario envía cada mensaje
- Reconexión automática en caso de desconexión

## Tecnologías utilizadas

- **Backend**: Python con la biblioteca `websockets`
- **Frontend**: HTML, CSS y JavaScript vanilla

## Requisitos

- Python 3.7 o superior
- Biblioteca `websockets` de Python

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/tu-usuario/chat-websocket.git
   cd chat-websocket
   ```

2. Instala las dependencias necesarias:
   ```
   pip install websockets
   ```

## Uso

1. Inicia el servidor WebSocket:
   ```
   python server.py
   ```
   El servidor se iniciará en `ws://0.0.0.0:8765`

2. Abre el archivo `index.html` en tu navegador o sirve los archivos estáticos con un servidor web simple:
   ```
   # Usando Python para servir archivos estáticos
   python -m http.server 8000
   ```
   Luego abre en tu navegador: `http://localhost:8000`

3. Ingresa un nombre de usuario y comienza a chatear

## Estructura del proyecto

- `server.py`: Servidor WebSocket implementado en Python
- `index.html`: Página web que contiene la interfaz de usuario del chat

## Flujo de comunicación

1. El cliente se conecta al servidor WebSocket
2. El cliente envía su nombre de usuario
3. El servidor registra al cliente y envía una notificación a todos los usuarios
4. El servidor envía el historial de mensajes al nuevo cliente
5. Los mensajes enviados por cualquier cliente son distribuidos a todos los clientes conectados
6. Al desconectarse, el servidor envía una notificación a todos los usuarios

## Desarrollo con Scrum

Este proyecto fue desarrollado utilizando la metodología Scrum:
- Se estableció un tablero Trello para seguimiento de tareas
- Se realizaron sprints semanales
- Se mantuvieron reuniones diarias de coordinación
- Se utilizó Git para control de versiones
