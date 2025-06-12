import json
import asyncio
from typing import Dict, List, Any
from core.deepseek_reseaner import DeepSeekReseaoner
from services.content_generator import ContentGeneratorService

class IntelligentChatService:
    def __init__(self):
        self.reasoner = DeepSeekReseaoner()
        self.content_generator = ContentGeneratorService()
        
        # Estados del chat
        self.chat_states = {}
        
        # Preguntas progresivas del chatbot
        self.conversation_flow = {
            "greeting": {
                "message": "¡Hola! 👋 Soy tu asistente de contenido inteligente. Te haré algunas preguntas para crear el post perfecto para ti. ¿Estás listo para empezar?",
                "options": ["¡Sí, empecemos!", "Necesito más información", "¿Qué puedes crear?"],
                "next": "content_type"
            },
            "content_type": {
                "message": "¡Perfecto! 🎨 Primero, ¿qué tipo de contenido quieres crear?",
                "options": [
                    "💡 Un tip o consejo profesional",
                    "✨ Una frase inspiracional",
                    "📊 Una estadística impactante",
                    "🎯 Una lista de consejos",
                    "🔥 Un hecho curioso",
                    "📋 Un tutorial paso a paso",
                    "🧠 Explicar un concepto técnico",
                    "🎲 Sorpréndeme (elige tú)"
                ],
                "next": "topic_theme"
            },
            "topic_theme": {
                "message": "Excelente elección! 🎯 Ahora, ¿sobre qué tema o nicho quieres que sea tu contenido?",
                "examples": [
                    "Programación y desarrollo",
                    "Marketing digital",
                    "Inteligencia artificial",
                    "Emprendimiento",
                    "Productividad",
                    "Diseño gráfico",
                    "Redes sociales",
                    "Otro tema..."
                ],
                "next": "content_details"
            },
            "content_details": {
                "message": "¡Interesante tema! 📝 Ahora cuéntame más detalles sobre lo que quieres comunicar:",
                "prompts": [
                    "¿Cuál es el mensaje principal que quieres transmitir?",
                    "¿Hay algún dato específico o ejemplo que quieras incluir?",
                    "¿Qué problema resuelve o qué valor aporta tu contenido?"
                ],
                "next": "target_audience"
            },
            "target_audience": {
                "message": "Perfecto! 👥 ¿A quién va dirigido tu contenido?",
                "options": [
                    "🚀 Emprendedores y fundadores",
                    "💻 Desarrolladores y programadores",
                    "📈 Profesionales de marketing",
                    "🎨 Diseñadores y creativos",
                    "📊 Analistas y científicos de datos",
                    "🏢 Profesionales corporativos",
                    "🎓 Estudiantes y principiantes",
                    "🌐 Audiencia general"
                ],
                "next": "social_platform"
            },
            "social_platform": {
                "message": "¡Genial! 📱 ¿En qué red social vas a publicar este contenido?",
                "options": [
                    "📸 Instagram (feed cuadrado)",
                    "📱 Instagram Stories",
                    "💼 LinkedIn (post)",
                    "🔄 LinkedIn (carousel)",
                    "🐦 Twitter/X",
                    "📘 Facebook",
                    "🎯 Múltiples plataformas"
                ],
                "next": "visual_style"
            },
            "visual_style": {
                "message": "Casi terminamos! 🎨 ¿Qué estilo visual prefieres para tu post?",
                "options": [
                    "✨ Minimalista y limpio",
                    "🚀 Moderno y futurista",
                    "💼 Profesional y elegante",
                    "🌈 Colorido y vibrante",
                    "🌅 Con gradientes hermosos",
                    "🌙 Oscuro y sofisticado",
                    "⚡ Neón y llamativo",
                    "🎪 Sorpréndeme con algo único"
                ],
                "next": "final_confirmation"
            },
            "final_confirmation": {
                "message": "¡Perfecto! 🎉 Tengo toda la información necesaria. Voy a crear un diseño personalizado basándose en nuestra conversación. ¿Procedo con la generación?",
                "options": ["¡Sí, créalo ahora!", "Déjame revisar los detalles", "Cambiar algo"],
                "next": "generate"
            }
        }
    
    async def start_conversation(self, user_id: str) -> Dict[str, Any]:
        """Inicia una nueva conversación de chat inteligente"""
        self.chat_states[user_id] = {
            "step": "greeting",
            "responses": {},
            "conversation_history": [],
            "created_at": asyncio.get_event_loop().time()
        }
        
        greeting = self.conversation_flow["greeting"]
        return {
            "message": greeting["message"],
            "options": greeting.get("options", []),
            "step": "greeting",
            "is_question": True
        }
    
    async def process_user_response(self, user_id: str, response: str, socketio=None) -> Dict[str, Any]:
        """Procesa la respuesta del usuario y continúa la conversación"""
        
        if user_id not in self.chat_states:
            return await self.start_conversation(user_id)
        
        state = self.chat_states[user_id]
        current_step = state["step"]
        
        # Guardar respuesta del usuario
        state["responses"][current_step] = response
        state["conversation_history"].append({
            "step": current_step,
            "user_response": response,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Determinar siguiente paso
        if current_step in self.conversation_flow:
            next_step = self.conversation_flow[current_step].get("next")
            
            if next_step == "generate":
                # Generar contenido basado en toda la conversación
                return await self.generate_from_conversation(user_id, socketio)
            elif next_step and next_step in self.conversation_flow:
                state["step"] = next_step
                return await self.get_next_question(user_id, next_step)
        
        # Si llegamos aquí, algo salió mal
        return {
            "message": "Lo siento, hubo un error en la conversación. ¿Quieres empezar de nuevo?",
            "options": ["Empezar de nuevo"],
            "step": "error",
            "is_question": True
        }
    
    async def get_next_question(self, user_id: str, step: str) -> Dict[str, Any]:
        """Obtiene la siguiente pregunta basada en el paso actual"""
        
        if step not in self.conversation_flow:
            return {"error": "Paso no válido"}
        
        question_data = self.conversation_flow[step]
        state = self.chat_states[user_id]
        
        # Personalizar pregunta basada en respuestas anteriores
        message = await self.personalize_question(user_id, step, question_data)
        
        return {
            "message": message,
            "options": question_data.get("options", []),
            "examples": question_data.get("examples", []),
            "prompts": question_data.get("prompts", []),
            "step": step,
            "is_question": True
        }
    
    async def personalize_question(self, user_id: str, step: str, question_data: Dict) -> str:
        """Personaliza las preguntas basándose en respuestas anteriores"""
        
        state = self.chat_states[user_id]
        responses = state["responses"]
        
        base_message = question_data["message"]
        
        # Personalización específica por paso
        if step == "topic_theme" and "content_type" in responses:
            content_type = responses["content_type"].lower()
            if "tip" in content_type:
                base_message += "\n\nPor ejemplo: 'Productividad para desarrolladores' o 'Consejos de marketing en LinkedIn'"
            elif "frase" in content_type or "inspiracional" in content_type:
                base_message += "\n\nPor ejemplo: 'Motivación para emprendedores' o 'Superación personal'"
            elif "estadística" in content_type:
                base_message += "\n\nPor ejemplo: 'Datos sobre inteligencia artificial' o 'Estadísticas de redes sociales'"
        
        elif step == "content_details" and "topic_theme" in responses:
            tema = responses["topic_theme"]
            base_message = f"¡{tema} es un tema fascinante! 📝 Cuéntame más detalles específicos sobre lo que quieres comunicar:"
        
        elif step == "visual_style" and "social_platform" in responses:
            platform = responses["social_platform"].lower()
            if "instagram" in platform:
                base_message += "\n\nPara Instagram, recomiendo estilos visuales que destaquen en el feed."
            elif "linkedin" in platform:
                base_message += "\n\nPara LinkedIn, sugiero un estilo más profesional pero atractivo."
            elif "twitter" in platform:
                base_message += "\n\nPara Twitter/X, los diseños impactantes funcionan muy bien."
        
        return base_message
    
    async def generate_from_conversation(self, user_id: str, socketio=None) -> Dict[str, Any]:
        """Genera contenido basado en toda la conversación"""
        
        if user_id not in self.chat_states:
            return {"error": "No hay conversación activa"}
        
        state = self.chat_states[user_id]
        responses = state["responses"]
        
        try:
            # Crear parámetros basándose en la conversación
            params = await self.conversation_to_params(responses)
            
            if socketio:
                socketio.emit('chat_generation_started', {
                    'message': '🚀 ¡Perfecto! Ahora voy a crear tu diseño personalizado basándome en nuestra conversación...',
                    'user_id': user_id
                })
            
            # Generar contenido usando el servicio existente
            result = await self.content_generator.generate_content_async(params, socketio)
            
            # Limpiar estado del chat después de generar
            if user_id in self.chat_states:
                del self.chat_states[user_id]
            
            return {
                "message": "🎉 ¡Tu contenido personalizado está listo! Revisa el resultado y descárgalo cuando quieras.",
                "generation_result": result,
                "is_question": False,
                "completed": True
            }
            
        except Exception as e:
            return {
                "message": f"❌ Hubo un error generando tu contenido: {str(e)}. ¿Quieres intentar de nuevo?",
                "options": ["Intentar de nuevo", "Empezar conversación nueva"],
                "is_question": True,
                "error": str(e)
            }
    
    async def conversation_to_params(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """Convierte las respuestas de la conversación en parámetros para generar contenido"""
        
        # Mapear tipo de contenido
        content_type_map = {
            "tip": "tip",
            "consejo": "tip", 
            "frase": "quote",
            "inspiracional": "quote",
            "estadística": "estadistica",
            "lista": "lista",
            "hecho": "hecho",
            "curioso": "hecho",
            "tutorial": "tutorial",
            "concepto": "concepto",
            "técnico": "concepto"
        }
        
        # Determinar tipo de contenido
        content_type = "tip"  # default
        content_response = responses.get("content_type", "").lower()
        for key, value in content_type_map.items():
            if key in content_response:
                content_type = value
                break
        
        # Mapear formato de red social
        format_map = {
            "instagram": "instagram_square",
            "feed": "instagram_square",
            "stories": "instagram_story",
            "linkedin": "linkedin_post",
            "carousel": "linkedin_carousel", 
            "twitter": "twitter_post",
            "facebook": "facebook_post"
        }
        
        formato = "instagram_square"  # default
        platform_response = responses.get("social_platform", "").lower()
        for key, value in format_map.items():
            if key in platform_response:
                formato = value
                break
        
        # Mapear estilo visual
        style_map = {
            "minimalista": "Minimalista",
            "limpio": "Minimalista",
            "moderno": "Moderno",
            "futurista": "Moderno",
            "profesional": "Profesional",
            "elegante": "Elegante",
            "colorido": "Colorido",
            "vibrante": "Colorido",
            "gradientes": "Gradientes",
            "oscuro": "Oscuro",
            "sofisticado": "Oscuro",
            "neón": "Neón",
            "llamativo": "Neón"
        }
        
        estilo = "Moderno"  # default
        style_response = responses.get("visual_style", "").lower()
        for key, value in style_map.items():
            if key in style_response:
                estilo = value
                break
        
        # Generar parámetros específicos usando IA
        params = await self.generate_specific_params(responses, content_type)
        
        # Parámetros base
        base_params = {
            "content_type": content_type,
            "tema": responses.get("topic_theme", "Contenido profesional"),
            "estilo": estilo,
            "colores": "Azul profesional",  # Se puede mejorar con más lógica
            "formato": formato,
            "nombre_archivo": f"chat_generado_{int(asyncio.get_event_loop().time())}"
        }
        
        # Combinar parámetros base con específicos
        base_params.update(params)
        
        return base_params
    
    async def generate_specific_params(self, responses: Dict[str, str], content_type: str) -> Dict[str, Any]:
        """Usa IA para generar parámetros específicos basándose en la conversación"""
        
        conversation_summary = "\n".join([
            f"Tipo de contenido: {responses.get('content_type', '')}",
            f"Tema: {responses.get('topic_theme', '')}",
            f"Detalles: {responses.get('content_details', '')}",
            f"Audiencia: {responses.get('target_audience', '')}",
            f"Plataforma: {responses.get('social_platform', '')}",
            f"Estilo: {responses.get('visual_style', '')}"
        ])
        
        prompt = f"""Basándote en esta conversación con un usuario, genera parámetros específicos para crear contenido de tipo "{content_type}":

{conversation_summary}

Responde SOLO con un JSON válido con estos campos según el tipo de contenido:

Para "tip": {{"titulo": "...", "descripcion": "..."}}
Para "quote": {{"frase": "...", "autor": "..."}}
Para "estadistica": {{"numero": "...", "descripcion": "..."}}
Para "lista": {{"titulo": "...", "descripcion": "..."}}
Para "hecho": {{"titulo": "...", "descripcion": "..."}}
Para "tutorial": {{"titulo": "...", "pasos": "..."}}
Para "concepto": {{"concepto": "...", "descripcion": "...", "nivel": "intermedio", "incluir_ejemplo": true}}

Responde ÚNICAMENTE el JSON, sin explicaciones."""
        
        try:
            response = await asyncio.to_thread(
                self.reasoner.chat,
                message=prompt,
                system_prompt="Generas parámetros en formato JSON. Solo JSON válido, sin texto adicional.",
                temperature=0.7,
                max_tokens=500,
                maintain_history=False
            )
            
            if response.get("success"):
                json_str = response["response"].strip()
                # Limpiar el JSON si viene con markdown
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0].strip()
                
                return json.loads(json_str)
            
        except Exception as e:
            print(f"Error generando parámetros específicos: {e}")
        
        # Fallback parámetros por defecto
        fallback_params = {
            "tip": {"titulo": "Consejo Profesional", "descripcion": "Consejo útil basado en la conversación"},
            "quote": {"frase": "El éxito llega a quienes perseveran", "autor": ""},
            "estadistica": {"numero": "85%", "descripcion": "Estadística relevante"},
            "lista": {"titulo": "Lista de Consejos", "descripcion": "Lista útil"},
            "hecho": {"titulo": "¿Sabías que...?", "descripcion": "Dato curioso"},
            "tutorial": {"titulo": "Cómo hacer...", "pasos": "4"},
            "concepto": {"concepto": "Concepto Técnico", "descripcion": "Explicación técnica", "nivel": "intermedio", "incluir_ejemplo": True}
        }
        
        return fallback_params.get(content_type, {"titulo": "Contenido", "descripcion": "Descripción"})