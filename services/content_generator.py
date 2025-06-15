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
        self.premium_templates_folder = "./plantillas_premium"
        
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
    
    def get_intelligent_recommendations(self, params):
        """Obtiene recomendaciones basadas en IA y contexto"""
        try:
            content_type = params.get('content_type', 'tip')
            tema = params.get('tema', '')
            formato = params.get('formato', 'instagram_square')
            
            # Detectar industria automáticamente
            industry_keywords = {
                'tech': ['programación', 'desarrollo', 'código', 'software', 'tech', 'ia', 'inteligencia artificial'],
                'finance': ['finanzas', 'inversión', 'dinero', 'banco', 'crypto', 'trading'],
                'creative': ['diseño', 'arte', 'creatividad', 'marketing', 'branding'],
                'healthcare': ['salud', 'medicina', 'bienestar', 'fitness', 'nutrición'],
                'education': ['educación', 'aprendizaje', 'curso', 'tutorial', 'enseñanza'],
                'business': ['negocio', 'empresa', 'emprendimiento', 'startup', 'ventas']
            }
            
            detected_industry = 'general'
            for industry, keywords in industry_keywords.items():
                if any(keyword in tema.lower() for keyword in keywords):
                    detected_industry = industry
                    break
            
            # Mapeo de recomendaciones
            industry_recommendations = {
                'tech': {
                    'color_palette': 'Verde tech',
                    'design_style': 'Moderno',
                    'confidence': 0.8
                },
                'finance': {
                    'color_palette': 'Azul profesional',
                    'design_style': 'Profesional',
                    'confidence': 0.9
                },
                'creative': {
                    'color_palette': 'Púrpura moderno',
                    'design_style': 'Colorido',
                    'confidence': 0.8
                },
                'healthcare': {
                    'color_palette': 'Verde tech',
                    'design_style': 'Minimalista',
                    'confidence': 0.7
                },
                'business': {
                    'color_palette': 'Azul profesional',
                    'design_style': 'Profesional',
                    'confidence': 0.8
                }
            }
            
            recommendations = industry_recommendations.get(detected_industry, {
                'color_palette': 'Azul profesional',
                'design_style': 'Moderno',
                'confidence': 0.5
            })
            
            # Ajustes específicos por plataforma
            if formato == 'linkedin_post':
                recommendations['design_style'] = 'Profesional'
                recommendations['confidence'] += 0.1
            elif formato == 'instagram_square':
                recommendations['design_style'] = 'Colorido'
                recommendations['confidence'] += 0.1
            
            return recommendations
            
        except Exception as e:
            return {
                'color_palette': 'Azul profesional',
                'design_style': 'Moderno',
                'confidence': 0.3,
                'error': str(e)
            }
    
    async def generate_content_async(self, params, socketio=None):
        """Genera contenido de forma asíncrona con actualización en tiempo real"""
        try:
            if socketio:
                socketio.emit('generation_status', {
                    'status': 'loading_templates',
                    'message': '📁 Cargando plantillas premium...'
                })
            
            templates = self.load_templates()
            
            if socketio:
                socketio.emit('generation_status', {
                    'status': 'creating_prompts',
                    'message': f'🛠️ Creando prompts profesionales... ({len(templates)} plantillas cargadas)'
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
                    'message': '🛡️ Usando modo fallback premium...'
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
        """Carga plantillas HTML premium y básicas"""
        templates = []
        
        # Cargar plantillas premium primero (mayor prioridad)
        premium_folder = Path(self.premium_templates_folder)
        basic_folder = Path(self.templates_folder)
        
        for folder_info in [
            (premium_folder, 'premium'), 
            (basic_folder, 'basic')
        ]:
            folder_path, folder_type = folder_info
            
            if folder_path.exists():
                for html_file in folder_path.glob("*.html"):
                    try:
                        with open(html_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            templates.append({
                                'filename': html_file.name,
                                'type': folder_type,
                                'content': content[:800]  # Más contenido para mejor contexto
                            })
                    except Exception as e:
                        print(f"⚠️ Error leyendo {html_file}: {e}")
        
        # Si no hay plantillas premium, usar solo las básicas
        if not templates:
            print("⚠️ No se encontraron plantillas premium, usando básicas")
        
        return templates
    
    def create_system_prompt(self):
        """System prompt mejorado para diseños profesionales"""
        return """Eres un DIRECTOR CREATIVO SENIOR de una agencia premium especializada en contenido social para Fortune 500.

MISIÓN: Crear diseños que compitan con Apple, Stripe, Airbnb y Tesla en calidad visual.

ESTÁNDARES PREMIUM OBLIGATORIOS:
🎨 DISEÑO:
- Minimalismo inteligente (espacio en blanco = lujo)
- Jerarquía visual perfecta (título → subtítulo → cuerpo → CTA)
- Paletas armoniosas (máximo 3 colores + neutros)
- Tipografía moderna (Inter, SF Pro, system-ui)
- Elementos alineados a grilla invisible

⚡ TÉCNICO:
- Responsive perfecto (móvil first)
- Accesibilidad WCAG AA (contraste 4.5:1+)
- Microinteracciones sutiles (hover, focus)
- Optimización para screenshot/sharing

🎯 PSICOLOGÍA VISUAL:
- Escaneabilidad en 3 segundos
- Jerarquía de información clara
- Llamada a acción evidente
- Credibilidad través diseño

INSPIRACIÓN DIRECTA:
- Apple.com marketing pages
- Stripe.com landing sections  
- Linear.app visual style
- Figma community top designs
- Dribbble shots with 10k+ likes

PROCESO OBLIGATORIO:
1. Analizar brief → Definir objetivo visual
2. Seleccionar paleta estratégica → Crear jerarquía tipográfica
3. Estructurar layout responsive → Añadir elementos premium
4. Pulir detalles microinteracciones → Validar legibilidad

RESPUESTA REQUERIDA:
- HTML completo válido (DOCTYPE + estructura)
- Tailwind CSS exclusivamente
- Fonts Google (Inter, Poppins, Roboto) 
- Sin JavaScript ni imágenes externas
- Dimensiones exactas especificadas
- Sin explicaciones, SOLO código HTML

CALIDAD TARGET: Indistinguible de trabajo de agencia $500/hora."""

    def create_content_prompt(self, templates, params):
        """Prompt específico mejorado para contenido social"""
        dimensions = SOCIAL_DIMENSIONS[params['formato']]
        
        # Sistema de paletas profesionales
        color_schemes = {
            "Azul profesional": {
                "primary": "#1E40AF", "secondary": "#3B82F6", "accent": "#60A5FA",
                "background": "#F8FAFC", "text": "#1E293B", "description": "Confianza corporativa"
            },
            "Verde tech": {
                "primary": "#059669", "secondary": "#10B981", "accent": "#34D399", 
                "background": "#F0FDF4", "text": "#064E3B", "description": "Innovación sostenible"
            },
            "Púrpura moderno": {
                "primary": "#7C3AED", "secondary": "#A855F7", "accent": "#C084FC",
                "background": "#FAF5FF", "text": "#581C87", "description": "Creatividad premium"
            },
            "Naranja energético": {
                "primary": "#EA580C", "secondary": "#FB923C", "accent": "#FDBA74",
                "background": "#FFF7ED", "text": "#9A3412", "description": "Energía positiva"
            },
            "Gradiente sunset": {
                "primary": "#EC4899", "secondary": "#F59E0B", "accent": "#EF4444",
                "background": "linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)", "text": "#92400E", "description": "Warmth premium"
            },
            "Monocromático": {
                "primary": "#111827", "secondary": "#374151", "accent": "#6B7280",
                "background": "#F9FAFB", "text": "#111827", "description": "Elegancia atemporal"
            }
        }
        
        selected_scheme = color_schemes.get(params['colores'], color_schemes["Azul profesional"])
        
        # Plantillas de diseño específicas por tipo
        design_templates = {
            "tip": """
            DISEÑO TIP PROFESIONAL:
            - Header con badge "💡 PROFESSIONAL TIP"
            - Título principal en 32-40px, bold, color primary
            - Descripción en 18-20px, line-height 1.6
            - Card con sombra sutil y border radius 16px
            - Ícono/emoji de acento
            - Footer con branding sutil
            """,
            "quote": """
            DISEÑO QUOTE PREMIUM:
            - Comillas grandes como elemento decorativo (color accent, opacity 0.3)
            - Texto de la cita en 24-28px, italic, centrado
            - Autor en 16px, color secondary, bold
            - Fondo con gradiente sutil o patrón minimalista
            - Layout centrado verticalmente
            """,
            "estadistica": """
            DISEÑO ESTADÍSTICA IMPACTANTE:
            - Número principal en 48-64px, ultra-bold, color primary
            - Porcentaje/unidad en color accent
            - Descripción en 20px, color text, weight 500
            - Gráfico visual simple (barra, círculo)
            - Badge "📊 DATA INSIGHT"
            - Background con pattern sutil
            """,
            "concepto": """
            DISEÑO CONCEPTO TÉCNICO:
            - Header con nivel de dificultad (badges)
            - Concepto principal en 28-32px, gradient text
            - Explicación en párrafos bien espaciados
            - Ejemplo en código box (si aplica)
            - Iconografía tech moderna
            - Layout en cards o sections
            """,
            "lista": """
            DISEÑO LISTA PROFESIONAL:
            - Header con "🎯 TOP TIPS"
            - Elementos numerados o con viñetas premium
            - Cada item en card separada con ícono
            - Jerarquía visual clara
            - Espaciado generoso entre elementos
            """,
            "hecho": """
            DISEÑO DATO CURIOSO:
            - Badge "🔥 DID YOU KNOW?"
            - Hecho principal destacado
            - Información adicional como soporte
            - Elementos visuales que refuercen la sorpresa
            - Layout que invite a compartir
            """,
            "tutorial": """
            DISEÑO TUTORIAL STEP-BY-STEP:
            - Header con "📋 HOW TO"
            - Pasos numerados claramente
            - Cada paso en sección diferenciada
            - Progreso visual (barra o círculos)
            - Call-to-action final
            """
        }
        
        content_template = design_templates.get(params['content_type'], design_templates["tip"])
        
        # Especificaciones por red social
        platform_specs = {
            "instagram_square": "Instagram Feed - Diseño cuadrado, elementos centrados, tipografía grande para móvil",
            "instagram_story": "Instagram Stories - Diseño vertical, información en tercios, touch-friendly",
            "linkedin_post": "LinkedIn - Estilo corporativo profesional, información clara, CTA sutil",
            "twitter_post": "Twitter - Información concisa, tipografía legible en timeline",
            "facebook_post": "Facebook - Diseño horizontal, amigable, call-to-action claro"
        }
        
        platform_context = platform_specs.get(params['formato'], "Red social profesional")
        
        # Contenido específico
        content_specs = self._get_enhanced_content_specifications(params)
        
        # Incluir mejores plantillas como referencia
        template_examples = ""
        if templates:
            premium_templates = [t for t in templates if t.get('type') == 'premium']
            if premium_templates:
                template_examples = f"\n--- REFERENCIA PREMIUM ---\n"
                template_examples += premium_templates[0]['content'][:500]
        
        return f"""BRIEF DE DISEÑO PROFESIONAL:

📋 ESPECIFICACIONES TÉCNICAS:
- Plataforma: {platform_context}
- Dimensiones: {dimensions['width']}x{dimensions['height']}px exactos
- Formato: {dimensions['name']}

🎨 PALETA CROMÁTICA PROFESIONAL:
- Primary: {selected_scheme['primary']} ({selected_scheme['description']})
- Secondary: {selected_scheme['secondary']}
- Accent: {selected_scheme['accent']}
- Background: {selected_scheme['background']}
- Text: {selected_scheme['text']}

📐 TEMPLATE DE DISEÑO:
{content_template}

📝 CONTENIDO A INCLUIR:
{content_specs}

🎯 ESTILO VISUAL: {params['estilo']}
- Tema principal: {params['tema']}
- Tono: Profesional pero accesible
- Target: {self._get_target_audience(params)}

{template_examples}

⚡ REQUERIMIENTOS TÉCNICOS:
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{params.get('titulo', params['tema'])}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .container {{ width: {dimensions['width']}px; height: {dimensions['height']}px; }}
    </style>
</head>
<body class="m-0 p-0 overflow-hidden">
    <div class="container mx-auto">
        <!-- TU DISEÑO PREMIUM AQUÍ -->
    </div>
</body>
</html>
```

🎨 INSPIRACIÓN: Diseño nivel Behance Top Shot, calidad agencia premium.

GENERA ÚNICAMENTE EL HTML COMPLETO. Sin explicaciones adicionales."""

    def _get_enhanced_content_specifications(self, params):
        """Especificaciones de contenido mejoradas"""
        content_type = params['content_type']
        
        if content_type == "tip":
            return f"""
            TIP PROFESIONAL: {params.get('titulo', 'Consejo de experto')}
            Descripción: {params.get('descripcion', 'Insight valioso para profesionales')}
            
            ELEMENTOS REQUERIDOS:
            - Badge "💡 PRO TIP" en la esquina superior
            - Título impactante y accionable
            - Descripción clara con beneficio específico
            - Call-to-action sutil ("Guarda este tip")
            - Iconografía moderna relacionada al tema
            """
        elif content_type == "quote":
            autor_text = f"- {params.get('autor', 'Autor Anónimo')}" if params.get('autor') else "- Sabiduría Popular"
            return f"""
            QUOTE INSPIRACIONAL: "{params.get('frase', 'La excelencia es un hábito, no un acto.')}"
            Autor: {autor_text}
            
            ELEMENTOS REQUERIDOS:
            - Comillas decorativas de gran tamaño
            - Texto de cita como elemento principal
            - Autor con tipografía distinguida
            - Elemento visual que refuerce el mensaje
            - Layout que invite a compartir
            """
        elif content_type == "estadistica":
            return f"""
            ESTADÍSTICA IMPACTANTE: {params.get('numero', '85%')}
            Contexto: {params.get('descripcion', 'De los profesionales exitosos aplican esta práctica')}
            
            ELEMENTOS REQUERIDOS:
            - Número estadístico como hero element
            - Visualización gráfica simple (progreso, chart)
            - Descripción que dé contexto y relevancia
            - Badge "📊 DATA INSIGHT"
            - Fuente de datos (si aplica)
            """
        elif content_type == "concepto":
            nivel_badges = {"basico": "🌱 BEGINNER", "intermedio": "🚀 INTERMEDIATE", "avanzado": "⚡ ADVANCED"}
            nivel_badge = nivel_badges.get(params.get('nivel', 'intermedio'), '🚀 INTERMEDIATE')
            
            return f"""
            CONCEPTO TÉCNICO: {params.get('concepto', 'Concepto Fundamental')}
            Nivel: {nivel_badge}
            Explicación: {params.get('descripcion', 'Explicación clara y práctica')}
            Incluir ejemplo: {params.get('incluir_ejemplo', True)}
            
            ELEMENTOS REQUERIDOS:
            - Título del concepto prominente
            - Badge de nivel de dificultad
            - Explicación en lenguaje claro
            - Ejemplo práctico (si se solicita)
            - Iconografía tech moderna
            """
        elif content_type == "lista":
            return f"""
            LISTA PROFESIONAL: {params.get('titulo', 'Lista de consejos')}
            Tipo: {params.get('descripcion', 'Lista útil para profesionales')}
            
            ELEMENTOS REQUERIDOS:
            - Header "🎯 TOP TIPS" 
            - Elementos numerados o con viñetas
            - Cada item destacado visualmente
            - Iconografía consistente
            - Jerarquía clara de información
            """
        elif content_type == "hecho":
            return f"""
            HECHO CURIOSO: {params.get('titulo', '¿Sabías que...?')}
            Contenido: {params.get('descripcion', 'Dato fascinante')}
            
            ELEMENTOS REQUERIDOS:
            - Badge "🔥 DID YOU KNOW?"
            - Hecho principal como protagonista
            - Información que genere sorpresa
            - Elementos visuales que refuercen el dato
            - Layout viral para compartir
            """
        elif content_type == "tutorial":
            return f"""
            TUTORIAL: {params.get('titulo', 'Cómo hacer...')}
            Pasos: {params.get('pasos', '4')} pasos
            
            ELEMENTOS REQUERIDOS:
            - Header "📋 HOW TO"
            - Pasos numerados claramente
            - Progreso visual (1/4, 2/4, etc.)
            - Cada paso diferenciado
            - Call-to-action al final
            """
        
        return f"CONTENIDO: {params.get('tema', 'Contenido profesional')}"
    
    def _get_target_audience(self, params):
        """Determina la audiencia objetivo basándose en el tema"""
        tema = params.get('tema', '').lower()
        
        if any(word in tema for word in ['programación', 'desarrollo', 'código', 'tech', 'software']):
            return "Desarrolladores y profesionales tech"
        elif any(word in tema for word in ['marketing', 'ventas', 'negocio', 'business']):
            return "Profesionales de marketing y ventas"
        elif any(word in tema for word in ['diseño', 'ux', 'ui', 'creatividad']):
            return "Diseñadores y creativos"
        elif any(word in tema for word in ['emprendimiento', 'startup', 'empresa']):
            return "Emprendedores y fundadores"
        elif any(word in tema for word in ['finanzas', 'inversión', 'dinero']):
            return "Profesionales financieros"
        elif any(word in tema for word in ['salud', 'fitness', 'bienestar']):
            return "Profesionales de la salud y wellness"
        elif any(word in tema for word in ['educación', 'enseñanza', 'curso']):
            return "Educadores y estudiantes"
        else:
            return "Profesionales y ejecutivos"
    
    def _get_content_specifications(self, params):
        """Especificaciones según tipo de contenido (método legacy)"""
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
        """Crea plantilla HTML básica mejorada sin IA"""
        content_type = params['content_type']
        
        # Contenido específico según tipo con mejor diseño
        if content_type == "tip":
            main_content = f"""
            <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm font-bold px-4 py-2 rounded-full mb-6 inline-block">
                💡 TIP PROFESIONAL
            </div>
            <h1 class="text-3xl font-bold mb-6 text-gray-800 leading-tight">{params.get('titulo', 'Consejo Profesional')}</h1>
            <p class="text-gray-600 text-lg leading-relaxed mb-6">{params.get('descripcion', 'Consejo útil para profesionales')}</p>
            <div class="text-blue-500 text-sm font-semibold">💾 Guarda este tip</div>
            """
        elif content_type == "quote":
            main_content = f"""
            <div class="text-8xl text-blue-500 opacity-20 mb-6">"</div>
            <p class="text-2xl font-medium text-gray-800 italic mb-6 leading-relaxed">{params.get('frase', 'Frase inspiracional')}</p>
            <div class="w-16 h-1 bg-gradient-to-r from-blue-500 to-purple-500 mx-auto mb-4"></div>
            {f'<div class="text-gray-600 font-semibold">— {params.get("autor", "Anónimo")}</div>' if params.get('autor') else ''}
            """
        elif content_type == "estadistica":
            main_content = f"""
            <div class="bg-blue-100 text-blue-600 text-sm font-bold px-4 py-2 rounded-full mb-6 inline-block">
                📊 DATA INSIGHT
            </div>
            <div class="text-6xl font-black text-blue-600 mb-4">{params.get('numero', '85%')}</div>
            <div class="w-full bg-gray-200 rounded-full h-4 mb-6">
                <div class="bg-gradient-to-r from-blue-500 to-purple-600 h-4 rounded-full" style="width: {params.get('numero', '85').replace('%', '')}%"></div>
            </div>
            <p class="text-xl text-gray-700 leading-relaxed">{params.get('descripcion', 'Estadística relevante')}</p>
            """
        elif content_type == "concepto":
            nivel_emoji = {"basico": "🌱", "intermedio": "🚀", "avanzado": "⚡"}
            nivel_text = {"basico": "Nivel Básico", "intermedio": "Nivel Intermedio", "avanzado": "Nivel Avanzado"}
            emoji = nivel_emoji.get(params.get('nivel', 'intermedio'), '🚀')
            nivel = nivel_text.get(params.get('nivel', 'intermedio'), 'Nivel Intermedio')
            
            main_content = f"""
            <div class="bg-purple-100 text-purple-600 text-sm font-bold px-4 py-2 rounded-full mb-6 inline-block">
                🧠 CONCEPTO TECH
            </div>
            <h1 class="text-4xl font-bold mb-6 text-gray-800 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                {params.get('concepto', 'Concepto Técnico')}
            </h1>
            <p class="text-gray-600 text-lg leading-relaxed mb-6">{params.get('descripcion', 'Explicación técnica simplificada')}</p>
            <div class="bg-gray-100 rounded-lg p-4">
                <div class="text-purple-500 font-bold text-sm">{emoji} {nivel}</div>
            </div>
            """
        else:
            main_content = f"""
            <h1 class="text-3xl font-bold mb-6 text-gray-800">{params.get('titulo', params.get('tema', 'Contenido'))}</h1>
            <p class="text-gray-600 text-lg leading-relaxed">{params.get('descripcion', 'Contenido sobre ' + params.get('tema', 'tema'))}</p>
            """
        
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{params.get('nombre_archivo', 'post')}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
    </style>
</head>
<body style="width: {dimensions['width']}px; height: {dimensions['height']}px; margin: 0; padding: 0;">
    <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
        <div class="text-center max-w-2xl">
            {main_content}
            <div class="mt-8 text-xs text-gray-400 font-medium">{params.get('tema', 'Social Content')} • Professional Design</div>
        </div>
    </div>
</body>
</html>"""