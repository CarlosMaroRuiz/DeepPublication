from flask import Flask, render_template, request, jsonify, send_file, session
from flask_socketio import SocketIO, emit
import os
from routes.chat_routes import chat_bp
from services.content_generator import ContentGeneratorService
from services.intelligent_chat import IntelligentChatService
import asyncio
import threading

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    
    # Configurar SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Registrar blueprints
    app.register_blueprint(chat_bp)
    
    # Instancia global del chat inteligente
    intelligent_chat = IntelligentChatService()
    
    # Ruta principal
    @app.route('/')
    def index():
        return render_template('chat.html')
    
    # Configurar SocketIO events
    @socketio.on('connect')
    def handle_connect():
        print('Cliente conectado')
        emit('status', {'msg': 'Conectado al servidor'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Cliente desconectado')
    
    @socketio.on('generate_content')
    def handle_generate_content(data):
        """Maneja la generación de contenido en tiempo real"""
        try:
            content_service = ContentGeneratorService()
            
            # Ejecutar generación en un hilo separado
            def run_generation():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Emitir estado inicial
                    socketio.emit('generation_status', {
                        'status': 'started',
                        'message': '🚀 Iniciando generación...'
                    })
                    
                    # Ejecutar generación
                    result = loop.run_until_complete(
                        content_service.generate_content_async(data, socketio)
                    )
                    
                    if result['success']:
                        socketio.emit('generation_complete', {
                            'success': True,
                            'html_file': result['html_file'],
                            'image_file': result['image_file'],
                            'message': '🎉 Contenido generado exitosamente!'
                        })
                    else:
                        socketio.emit('generation_complete', {
                            'success': False,
                            'error': result['error'],
                            'message': '❌ Error en la generación'
                        })
                        
                except Exception as e:
                    socketio.emit('generation_complete', {
                        'success': False,
                        'error': str(e),
                        'message': f'❌ Error inesperado: {str(e)}'
                    })
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_generation)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            emit('generation_complete', {
                'success': False,
                'error': str(e),
                'message': f'❌ Error inesperado: {str(e)}'
            })
    
    # ================================
    # NUEVOS EVENTOS PARA CHAT INTELIGENTE
    # ================================
    
    @socketio.on('start_intelligent_chat')
    def handle_start_intelligent_chat():
        """Inicia chat inteligente via SocketIO"""
        try:
            # Generar user_id único para esta sesión
            import uuid
            user_id = str(uuid.uuid4())
            session['chat_user_id'] = user_id
            
            def run_chat_start():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    result = loop.run_until_complete(
                        intelligent_chat.start_conversation(user_id)
                    )
                    
                    socketio.emit('chat_response', {
                        'success': True,
                        'user_id': user_id,
                        'is_bot': True,
                        **result
                    })
                    
                except Exception as e:
                    socketio.emit('chat_response', {
                        'success': False,
                        'error': str(e),
                        'is_bot': True,
                        'message': 'Lo siento, hubo un error iniciando el chat. ¿Quieres intentar de nuevo?'
                    })
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_chat_start)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            emit('chat_response', {
                'success': False,
                'error': str(e),
                'is_bot': True,
                'message': 'Error iniciando chat inteligente'
            })
    
    @socketio.on('send_chat_message')
    def handle_send_chat_message(data):
        """Maneja mensajes del chat inteligente"""
        try:
            message = data.get('message', '')
            user_id = session.get('chat_user_id')
            
            if not user_id:
                emit('chat_response', {
                    'success': False,
                    'error': 'No hay sesión de chat activa',
                    'is_bot': True,
                    'message': 'Lo siento, necesitas iniciar una nueva conversación.'
                })
                return
            
            if not message:
                emit('chat_response', {
                    'success': False,
                    'error': 'Mensaje vacío',
                    'is_bot': True,
                    'message': 'Por favor escribe algo para continuar.'
                })
                return
            
            def run_chat_message():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    result = loop.run_until_complete(
                        intelligent_chat.process_user_response(user_id, message, socketio)
                    )
                    
                    if result.get('completed'):
                        # Chat completado, iniciar generación
                        socketio.emit('chat_response', {
                            'success': True,
                            'is_bot': True,
                            'message': result['message'],
                            'completed': True
                        })
                        
                        # Si hay resultado de generación, emitirlo
                        if 'generation_result' in result:
                            gen_result = result['generation_result']
                            socketio.emit('generation_complete', {
                                'success': gen_result['success'],
                                'html_file': gen_result.get('html_file'),
                                'image_file': gen_result.get('image_file'),
                                'type': gen_result.get('type', 'chat'),
                                'message': '🎉 ¡Tu contenido personalizado está listo!'
                            })
                    else:
                        # Continuar conversación
                        socketio.emit('chat_response', {
                            'success': True,
                            'is_bot': True,
                            **result
                        })
                    
                except Exception as e:
                    socketio.emit('chat_response', {
                        'success': False,
                        'error': str(e),
                        'is_bot': True,
                        'message': f'Lo siento, hubo un error: {str(e)}'
                    })
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_chat_message)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            emit('chat_response', {
                'success': False,
                'error': str(e),
                'is_bot': True,
                'message': 'Error procesando mensaje'
            })
    
    @socketio.on('reset_intelligent_chat')
    def handle_reset_intelligent_chat():
        """Reinicia el chat inteligente"""
        try:
            user_id = session.get('chat_user_id')
            
            if user_id and user_id in intelligent_chat.chat_states:
                del intelligent_chat.chat_states[user_id]
            
            # Limpiar sesión
            session.pop('chat_user_id', None)
            
            emit('chat_reset', {
                'success': True,
                'message': 'Chat reiniciado correctamente'
            })
            
        except Exception as e:
            emit('chat_reset', {
                'success': False,
                'error': str(e)
            })
    
    # Ruta para servir archivos generados
    @app.route('/download/<filename>')
    def download_file(filename):
        try:
            return send_file(filename, as_attachment=True)
        except FileNotFoundError:
            return jsonify({'error': 'Archivo no encontrado'}), 404
    
    app.socketio = socketio
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)