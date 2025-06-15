from flask import Blueprint, render_template, request, jsonify, session
from services.content_generator import ContentGeneratorService
from services.intelligent_chat import IntelligentChatService
from enums.social_dimensions import SOCIAL_DIMENSIONS
from enums.professional_styles import PROFESSIONAL_COLOR_PALETTES, PROFESSIONAL_DESIGN_STYLES
import uuid

chat_bp = Blueprint('chat', __name__)

# Instancia global del servicio de chat inteligente
intelligent_chat = IntelligentChatService()

@chat_bp.route('/api/formats')
def get_formats():
    """Obtiene los formatos de redes sociales disponibles"""
    return jsonify(SOCIAL_DIMENSIONS)

@chat_bp.route('/api/content-types')
def get_content_types():
    """Obtiene los tipos de contenido disponibles"""
    content_types = [
        {"id": "tip", "name": "💡 Tip/Consejo profesional", "emoji": "💡"},
        {"id": "quote", "name": "✨ Quote inspiracional", "emoji": "✨"},
        {"id": "estadistica", "name": "📊 Estadística/Datos", "emoji": "📊"},
        {"id": "lista", "name": "🎯 Lista de consejos", "emoji": "🎯"},
        {"id": "hecho", "name": "🔥 Hecho curioso/Did you know", "emoji": "🔥"},
        {"id": "tutorial", "name": "📋 Paso a paso/Tutorial", "emoji": "📋"},
        {"id": "concepto", "name": "🧠 Concepto/Definición técnica", "emoji": "🧠"}
    ]
    return jsonify(content_types)

@chat_bp.route('/api/styles')
def get_styles():
    """Obtiene estilos de diseño profesionales"""
    styles = []
    for name, style in PROFESSIONAL_DESIGN_STYLES.items():
        styles.append({
            "id": name,
            "name": name,
            "description": style["description"],
            "characteristics": style["characteristics"]
        })
    
    return jsonify(styles)

@chat_bp.route('/api/color-palettes')
def get_color_palettes():
    """Obtiene paletas de colores profesionales"""
    palettes = []
    for name, palette in PROFESSIONAL_COLOR_PALETTES.items():
        palettes.append({
            "id": name,
            "name": name,
            "description": palette["description"],
            "primary": palette["primary"],
            "gradient": palette["gradient"],
            "best_for": palette["best_for"]
        })
    
    return jsonify(palettes)

@chat_bp.route('/api/test-deepseek', methods=['POST'])
def test_deepseek():
    """Prueba la conexión con DeepSeek"""
    try:
        content_service = ContentGeneratorService()
        result = content_service.test_deepseek_connection()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/api/generate-idea', methods=['POST'])
def generate_idea():
    """Genera ideas usando IA"""
    try:
        content_service = ContentGeneratorService()
        result = content_service.generate_ai_idea_sync()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/api/random-ideas')
def get_random_ideas():
    """Obtiene ideas predefinidas aleatorias"""
    ideas = [
        {
            "tipo": "💡 Tip",
            "tema": "Inteligencia Artificial", 
            "titulo": "5 errores que cometen los developers al usar IA",
            "razon": "Muy actual y útil para profesionales",
            "content_type": "tip"
        },
        {
            "tipo": "📊 Estadística",
            "tema": "Remote Work",
            "titulo": "73% de las empresas mantendrán trabajo híbrido en 2025",
            "razon": "Tendencia post-pandemia relevante",
            "content_type": "estadistica"
        },
        {
            "tipo": "🔥 Hecho Curioso",
            "tema": "Programación",
            "titulo": "Python fue nombrado por Monty Python, no por la serpiente",
            "razon": "Dato curioso que pocos conocen",
            "content_type": "hecho"
        },
        {
            "tipo": "🎯 Lista",
            "tema": "Productividad",
            "titulo": "7 herramientas de IA que todo profesional debe conocer",
            "razon": "Combina tendencias actuales con utilidad práctica",
            "content_type": "lista"
        },
        {
            "tipo": "✨ Quote",
            "tema": "Emprendimiento",
            "titulo": "El fracaso es solo feedback disfrazado",
            "razon": "Motivacional y relacionable para emprendedores",
            "content_type": "quote"
        },
        {
            "tipo": "🧠 Concepto",
            "tema": "Desarrollo de Software",
            "titulo": "¿Qué es SOLID? Los 5 principios explicados fácil",
            "razon": "Concepto fundamental que todo programador debe conocer",
            "content_type": "concepto"
        },
        {
            "tipo": "🧠 Concepto",
            "tema": "Inteligencia Artificial",
            "titulo": "Red Neuronal vs Cerebro Humano: ¿En qué se parecen?",
            "razon": "Analogía perfecta para explicar IA de forma simple",
            "content_type": "concepto"
        }
    ]
    
    import random
    return jsonify(random.sample(ideas, min(3, len(ideas))))

# ================================
# NUEVAS RUTAS PARA CHAT INTELIGENTE
# ================================

@chat_bp.route('/api/chat/start', methods=['POST'])
def start_intelligent_chat():
    """Inicia una nueva conversación de chat inteligente"""
    try:
        # Generar o usar user_id de la sesión
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())
        
        user_id = session['user_id']
        
        # Usar async_to_sync para llamar función async desde ruta síncrona
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(intelligent_chat.start_conversation(user_id))
            return jsonify({
                'success': True,
                'user_id': user_id,
                **result
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/api/chat/message', methods=['POST'])
def send_chat_message():
    """Envía un mensaje al chat inteligente"""
    try:
        data = request.get_json()
        
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'No hay sesión activa'
            }), 400
        
        user_id = session['user_id']
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Mensaje vacío'
            }), 400
        
        # Procesar mensaje
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                intelligent_chat.process_user_response(user_id, message)
            )
            return jsonify({
                'success': True,
                'user_id': user_id,
                **result
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/api/chat/status/<user_id>')
def get_chat_status(user_id):
    """Obtiene el estado actual del chat"""
    try:
        if user_id in intelligent_chat.chat_states:
            state = intelligent_chat.chat_states[user_id]
            return jsonify({
                'success': True,
                'active': True,
                'step': state['step'],
                'responses_count': len(state['responses'])
            })
        else:
            return jsonify({
                'success': True,
                'active': False
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/api/chat/reset', methods=['POST'])
def reset_chat():
    """Reinicia la conversación del chat"""
    try:
        data = request.get_json()
        user_id = data.get('user_id') or session.get('user_id')
        
        if user_id and user_id in intelligent_chat.chat_states:
            del intelligent_chat.chat_states[user_id]
        
        return jsonify({
            'success': True,
            'message': 'Chat reiniciado'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/health')
def health_check():
    """Endpoint de salud"""
    return jsonify({'status': 'healthy', 'service': 'Social Content Generator'})



@chat_bp.route('/api/intelligent-recommendations', methods=['POST'])
def get_intelligent_recommendations():
    """Obtiene recomendaciones de diseño basadas en contexto"""
    try:
        data = request.get_json()
        content_service = ContentGeneratorService()
        recommendations = content_service.get_intelligent_recommendations(data)
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/api/design-preview', methods=['POST'])
def get_design_preview():
    """Genera preview rápido del diseño sin generar imagen"""
    try:
        data = request.get_json()
        content_service = ContentGeneratorService()
        
        # Crear prompt simplificado para preview
        system_prompt = "Genera HTML minimalista para preview rápido. Solo estructura básica con colores y tipografía."
        
        preview_params = {
            'content_type': data.get('content_type', 'tip'),
            'tema': data.get('tema', 'Preview'),
            'formato': 'instagram_square',
            'colores': data.get('colores', 'Azul profesional'),
            'estilo': data.get('estilo', 'Moderno'),
            'nombre_archivo': 'preview_temp'
        }
        
        # Usar método simplificado
        dimensions = SOCIAL_DIMENSIONS['instagram_square']
        html_content = content_service._create_basic_html_template(preview_params, dimensions)
        
        return jsonify({
            'success': True,
            'html_preview': html_content,
            'message': 'Preview generado'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/api/templates/premium')
def get_premium_templates():
    """Lista plantillas premium disponibles"""
    try:
        content_service = ContentGeneratorService()
        templates = content_service.load_templates()
        
        premium_templates = [t for t in templates if t.get('type') == 'premium']
        
        return jsonify({
            'success': True,
            'templates': premium_templates,
            'count': len(premium_templates)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500