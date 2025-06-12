import asyncio
import os
import traceback
import time
from pathlib import Path
from core.deepseek_reseaner import DeepSeekReseaoner
from enums.social_dimensions import SOCIAL_DIMENSIONS
from services.html_converter import HTMLConverterService
from prompts.Prompt_Gen_Idea import prompt_gen_idea

class ContentGeneratorService:
    def __init__(self):
        self.reasoner = DeepSeekReseaoner()
        self.html_converter = HTMLConverterService()
        self.templates_folder = "./plantillas"
        
    def test_deepseek_connection(self):
        """Prueba la conexión con DeepSeek"""
        try:
            test_response = self.reasoner.chat(
                message="Hola",
                system_prompt="Responde solo: 'Conexión OK'",
                max_tokens=10,
                maintain_history=False
            )
            
            if test_response and test_response.get("success"):
                return {
                    'success': True,
                    'message': 'Conexión con DeepSeek: OK',
                    'response': test_response.get('response', 'N/A')
                }
            else:
                return {
                    'success': False,
                    'message': 'Conexión con DeepSeek: FALLO',
                    'error': test_response.get('error', 'Respuesta vacía')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': 'Error probando DeepSeek',
                'error': f"{type(e).__name__}: {str(e)}"
            }
    
    def generate_ai_idea_sync(self):
        """Genera idea usando IA (versión síncrona para API)"""
        try:
            prompt = prompt_gen_idea.prompt
            system_prompt = prompt_gen_idea.system_promt
            
            response = self.reasoner.chat(
                message=prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=1000,
                maintain_history=False
            )
            
            if response and response.get("success"):
                return {
                    'success': True,
                    'ideas': response["response"]
                }
            else:
                return {
                    'success': False,
                    'error': response.get('error', 'Respuesta vacía')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_content_async(self, params, socketio=None):
        """Genera contenido de forma asíncrona con actualización en tiempo real"""
        try:
            if socketio:
                socketio.emit('generation_status', {
                    'status': 'loading_templates',
                    'message': '📁 Cargando plantillas...'
                })
            
            templates = self.load_templates()
            
            if socketio:
                socketio.emit('generation_status', {
                    'status': 'creating_prompts',
                    'message': f'🛠️ Creando prompts... ({len(templates)} plantillas cargadas)'
                })
            
            system_prompt = self.create_system_prompt()
            user_prompt = self.create_content_prompt(templates, params)
            
            total_chars = len(system_prompt) + len(user_prompt)
            
            if socketio:
                socketio.emit('generation_status', {
                    'status': 'calling_deepseek',
                    'message': f'🤖 Llamando a DeepSeek... ({total_chars} caracteres)',
                    'estimated_time': '2-5 minutos' if total_chars > 2000 else '30-90 segundos'
                })
            
            # Intentos múltiples con timeouts progresivos
            max_attempts = 3
            timeouts = [180, 240, 300]  # 3, 4, 5 minutos
            
            for attempt in range(max_attempts):
                try:
                    timeout_seconds = timeouts[attempt]
                    
                    if socketio:
                        socketio.emit('generation_status', {
                            'status': 'generating',
                            'message': f'🔄 Intento {attempt + 1}/{max_attempts} (timeout: {timeout_seconds//60} minutos)'
                        })
                    
                    response = await asyncio.wait_for(
                        asyncio.to_thread(
                            self.reasoner.chat,
                            message=user_prompt,
                            system_prompt=system_prompt,
                            temperature=0.3,
                            max_tokens=4000,
                            maintain_history=False
                        ),
                        timeout=timeout_seconds
                    )
                    
                    if response.get("success") and response.get("response"):
                        break
                        
                except asyncio.TimeoutError:
                    if socketio:
                        socketio.emit('generation_status', {
                            'status': 'timeout',
                            'message': f'❌ TIMEOUT en intento {attempt + 1} ({timeout_seconds//60} min)'
                        })
                    
                    if attempt == max_attempts - 1:
                        return await self._generate_fallback_content(params, socketio)
                    continue
            
            if not response.get("success") or not response.get("response"):
                return await self._generate_fallback_content(params, socketio)
            
            if socketio:
                socketio.emit('generation_status', {
                    'status': 'processing',
                    'message': '🧹 Procesando respuesta de DeepSeek...'
                })
            
            html_content = self._clean_html_response(response["response"])
            
            if not html_content.strip():
                return await self._generate_fallback_content(params, socketio)
            
            # Guardar HTML
            html_filename = f"{params['nombre_archivo']}.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            if socketio:
                socketio.emit('generation_status', {
                    'status': 'converting',
                    'message': '🖼️ Convirtiendo a imagen...'
                })
            
            # Convertir a imagen
            image_filename = f"{params['nombre_archivo']}.png"
            conversion_success = await self.html_converter.convert_to_image(
                html_content, image_filename, params['formato']
            )
            
            if conversion_success:
                return {
                    'success': True,
                    'html_file': html_filename,
                    'image_file': image_filename,
                    'type': 'premium'  # Generado con IA
                }
            else:
                return {
                    'success': False,
                    'error': 'Error en la conversión a imagen'
                }
                
        except Exception as e:
            if socketio:
                socketio.emit('generation_status', {
                    'status': 'error',
                    'message': f'❌ Error inesperado: {str(e)}'
                })
            
            return await self._generate_fallback_content(params, socketio)
    
    async def _generate_fallback_content(self, params, socketio=None):
        """Genera contenido HTML básico cuando DeepSeek falla"""
        try:
            if socketio:
                socketio.emit('generation_status', {
                    'status': 'fallback',
                    'message': '🛡️ Usando modo fallback...'
                })
            
            dimensions = SOCIAL_DIMENSIONS[params['formato']]
            fallback_html = self._create_basic_html_template(params, dimensions)
            
            # Guardar HTML de respaldo
            html_filename = f"{params['nombre_archivo']}_fallback.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(fallback_html)
            
            # Convertir a imagen
            image_filename = f"{params['nombre_archivo']}_fallback.png"
            success = await self.html_converter.convert_to_image(
                fallback_html, image_filename, params['formato']
            )
            
            if success:
                return {
                    'success': True,
                    'html_file': html_filename,
                    'image_file': image_filename,
                    'type': 'fallback'  # Generado con plantilla básica
                }
            else:
                return {
                    'success': False,
                    'error': 'Error incluso en modo fallback'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error crítico en fallback: {str(e)}'
            }
    
    def _clean_html_response(self, html_content):
        """Limpia la respuesta HTML de DeepSeek"""
        if '```html' in html_content:
            html_content = html_content.split('```html')[1].split('```')[0].strip()
        elif '```' in html_content:
            html_content = html_content.split('```')[1].split('```')[0].strip()
        elif '<!DOCTYPE' in html_content:
            html_content = html_content.strip()
        elif '<html' in html_content.lower():
            start = html_content.lower().find('<html')
            if start != -1:
                html_content = html_content[start:].strip()
        
        return html_content
    
    def load_templates(self):
        """Carga plantillas HTML"""
        templates = []
        folder_path = Path(self.templates_folder)
        
        if not folder_path.exists():
            return templates
        
        for html_file in folder_path.glob("*.html"):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    templates.append({
                        'filename': html_file.name,
                        'content': content[:600]  # Reducir tamaño
                    })
            except Exception as e:
                print(f"⚠️ Error leyendo {html_file}: {e}")
        
        return templates
    
    def create_system_prompt(self):
        """System prompt específico para contenido social"""
        return """Eres un experto en creación de contenido visual para redes sociales que genera código HTML válido.

TAREA PRINCIPAL:
Generar código HTML completo y funcional para posts de redes sociales.

ESPECIALIZACIÓN:
- Posts atractivos para Instagram, LinkedIn, Twitter
- Diseños que generen engagement y shares
- Contenido profesional pero accesible
- Tipografía legible en dispositivos móviles
- Explicaciones técnicas simplificadas y visuales

PROCESO OBLIGATORIO:
1. Analiza las plantillas de diseño proporcionadas
2. Combina elementos para crear contenido único
3. Adapta el diseño al formato de red social específico
4. Para conceptos: usa analogías visuales y ejemplos claros

REGLAS TÉCNICAS ESTRICTAS:
- Responde ÚNICAMENTE con código HTML válido y completo
- Usa EXCLUSIVAMENTE Tailwind CSS (CDN)
- Incluye DOCTYPE html, head completo y body
- Diseño centrado y equilibrado
- Tipografía grande y legible
- Sin JavaScript
- Sin imágenes externas
- Optimizado para la red social especificada
- NO incluir explicaciones antes o después del HTML
- NO usar markdown o comentarios fuera del HTML

FORMATO DE RESPUESTA OBLIGATORIO:
- Primera línea: <!DOCTYPE html>
- Última línea: </html>
- Sin texto adicional antes o después del HTML
- Sin bloques de código markdown (```)

IMPORTANTE: Tu respuesta debe ser HTML puro, sin explicaciones."""
    
    def create_content_prompt(self, templates, params):
        """Prompt específico para contenido social"""
        dimensions = SOCIAL_DIMENSIONS[params['formato']]
        
        # Solo usar 1 plantilla para reducir tamaño del prompt
        template_content = ""
        if templates:
            template_content = f"\n--- TEMPLATE DE REFERENCIA ---\n"
            template_content += templates[0]['content']
        
        # Prompt específico según tipo de contenido
        content_specs = self._get_content_specifications(params)
        
        return f"""Genera un post HTML completo para {dimensions['name']} ({dimensions['width']}x{dimensions['height']}px).

{template_content}

CONTENIDO REQUERIDO:
{content_specs}

ESPECIFICACIONES TÉCNICAS:
- Tema: {params['tema']}
- Estilo: {params['estilo']}
- Colores: {params['colores']}
- Dimensiones exactas: {dimensions['width']}x{dimensions['height']}px

ESTRUCTURA HTML OBLIGATORIA:
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{params['nombre_archivo']}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body style="width: {dimensions['width']}px; height: {dimensions['height']}px; margin: 0; padding: 0;">
    <!-- TU CONTENIDO AQUÍ -->
</body>
</html>
```

REGLAS ESTRICTAS:
- Responde ÚNICAMENTE con HTML válido y completo
- Usa SOLO Tailwind CSS (CDN incluido)
- Centrado vertical y horizontal
- Tipografía legible para móvil
- Sin scroll, contenido debe caber en las dimensiones exactas
- NO incluyas explicaciones, solo código HTML"""
    
    def _get_content_specifications(self, params):
        """Especificaciones según tipo de contenido"""
        content_type = params['content_type']
        
        if content_type == "tip":
            return f"TIP: {params.get('titulo', 'Consejo profesional')}\nDescripción: {params.get('descripcion', 'Consejo útil')}"
        elif content_type == "quote":
            autor_text = f"- {params.get('autor', '')}" if params.get('autor') else ""
            return f"QUOTE: {params.get('frase', 'Frase inspiracional')}\nAutor: {autor_text}"
        elif content_type == "estadistica":
            return f"ESTADÍSTICA: {params.get('numero', '85%')}\nDescripción: {params.get('descripcion', 'Estadística relevante')}"
        elif content_type == "lista":
            return f"LISTA: {params.get('titulo', 'Lista de consejos')}\nTipo: {params.get('descripcion', 'Lista útil')}"
        elif content_type == "hecho":
            return f"HECHO: {params.get('titulo', '¿Sabías que...?')}\nContenido: {params.get('descripcion', 'Dato curioso')}"
        elif content_type == "tutorial":
            return f"TUTORIAL: {params.get('titulo', 'Cómo hacer...')}\nPasos: {params.get('pasos', '4')}"
        elif content_type == "concepto":
            ejemplo_text = ""
            if params.get('incluir_ejemplo'):
                ejemplo_text = "\nIncluir ejemplo práctico"
            return f"CONCEPTO: {params.get('concepto', 'Concepto técnico')}\nDescripción: {params.get('descripcion', 'Explicación técnica')}\nNivel: {params.get('nivel', 'intermedio')}{ejemplo_text}"
        
        return f"CONTENIDO: {params.get('tema', 'Contenido general')}"
    
    def _create_basic_html_template(self, params, dimensions):
        """Crea plantilla HTML básica sin IA"""
        content_type = params['content_type']
        
        # Contenido específico según tipo
        if content_type == "tip":
            main_content = f"""
            <div class="text-blue-600 text-sm font-semibold mb-2">💡 TIP PROFESIONAL</div>
            <h1 class="text-2xl font-bold mb-4 text-gray-800">{params.get('titulo', 'Consejo Profesional')}</h1>
            <p class="text-gray-600 text-base leading-relaxed">{params.get('descripcion', 'Consejo útil para profesionales')}</p>
            """
        elif content_type == "quote":
            main_content = f"""
            <div class="text-6xl text-gray-300 mb-4">"</div>
            <p class="text-xl font-medium text-gray-800 italic mb-4">{params.get('frase', 'Frase inspiracional')}</p>
            {f'<div class="text-gray-600">- {params.get("autor", "")}</div>' if params.get('autor') else ''}
            """
        elif content_type == "estadistica":
            main_content = f"""
            <div class="text-5xl font-bold text-blue-600 mb-4">{params.get('numero', '85%')}</div>
            <p class="text-lg text-gray-700">{params.get('descripcion', 'Estadística relevante')}</p>
            <div class="text-sm text-gray-500 mt-4">📊 ESTADÍSTICA</div>
            """
        elif content_type == "concepto":
            nivel_emoji = {"basico": "🌱", "intermedio": "🚀", "avanzado": "⚡"}
            nivel_text = {"basico": "Nivel Básico", "intermedio": "Nivel Intermedio", "avanzado": "Nivel Avanzado"}
            emoji = nivel_emoji.get(params.get('nivel', 'intermedio'), '🚀')
            nivel = nivel_text.get(params.get('nivel', 'intermedio'), 'Nivel Intermedio')
            
            main_content = f"""
            <div class="text-purple-600 text-sm font-semibold mb-2">🧠 CONCEPTO TECH</div>
            <h1 class="text-3xl font-bold mb-4 text-gray-800">{params.get('concepto', 'Concepto Técnico')}</h1>
            <p class="text-gray-600 text-base leading-relaxed mb-4">{params.get('descripcion', 'Explicación técnica simplificada')}</p>
            <div class="text-sm text-purple-500 font-medium">{emoji} {nivel}</div>
            """
        else:
            main_content = f"""
            <h1 class="text-2xl font-bold mb-4 text-gray-800">{params.get('titulo', params.get('tema', 'Contenido'))}</h1>
            <p class="text-gray-600">{params.get('descripcion', 'Contenido sobre ' + params.get('tema', 'tema'))}</p>
            """
        
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{params.get('nombre_archivo', 'post')}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body style="width: {dimensions['width']}px; height: {dimensions['height']}px; margin: 0; padding: 0;">
    <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-white p-8">
        <div class="text-center max-w-md">
            {main_content}
            <div class="mt-6 text-xs text-gray-400">{params.get('tema', 'Social Content')}</div>
        </div>
    </div>
</body>
</html>"""