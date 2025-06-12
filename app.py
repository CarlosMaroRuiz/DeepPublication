import os
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright
from core.deepseek_reseaner import DeepSeekReseaoner  # Tu clase
import time
import traceback
import random
from enums.social_dimensions import SOCIAL_DIMENSIONS

class SocialContentGenerator:
    def __init__(self):
        self.reasoner = DeepSeekReseaoner()
        self.templates_folder = None
        
        # Dimensiones para redes sociales
        self.social_dimensions = SOCIAL_DIMENSIONS
        
    def print_banner(self):
        """Banner para contenido de redes sociales"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║             📱 GENERADOR DE CONTENIDO SOCIAL                 ║
║                   Instagram • LinkedIn • Twitter            ║
╠══════════════════════════════════════════════════════════════╣
║  Crea posts visuales impactantes para redes sociales        ║
║  Tips • Quotes • Estadísticas • Conceptos • Tutoriales      ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def print_menu(self):
        """Menú principal adaptado para redes sociales"""
        menu = """
┌─────────────────────────────────────┐
│           CONTENIDO SOCIAL          │
├─────────────────────────────────────┤
│  1. 💡 Tip/Consejo profesional      │
│  2. ✨ Quote inspiracional          │
│  3. 📊 Estadística/Datos            │
│  4. 🎯 Lista de consejos            │
│  5. 🔥 Hecho curioso/Did you know   │
│  6. 📋 Paso a paso/Tutorial         │
│  7. 🧠 Concepto/Definición técnica  │
│  8. 🚀 Múltiples posts              │
│  9. 🎲 Generar idea aleatoria       │
│  10. ⚡ Modo rápido (sin plantillas)│
│  11. 📁 Cambiar plantillas          │
│  12. 📱 Ver formatos disponibles    │
│  13. 🔧 Diagnóstico DeepSeek        │
│  14. ❌ Salir                       │
└─────────────────────────────────────┘

💡 MODOS DISPONIBLES:
   🔥 COMPLETO (1-9): Usa plantillas + IA de calidad
      • Tiempo: 2-5 minutos (esperará pacientemente)
      • Calidad: Máxima, diseños únicos y profesionales
      • Control: Te pregunta si quieres esperar o usar fallback
   
   ⚡ RÁPIDO (10): Prompts simples, sin plantillas
      • Tiempo: 30-90 segundos
      • Calidad: Buena, diseños funcionales
      • Ideal para: Cuando necesitas algo ya

   🔧 DIAGNÓSTICO (13): Prueba problemas con DeepSeek
      • Identifica problemas de conexión o configuración
      • Tests de generación HTML
      • Recomendaciones específicas
        """
        print(menu)

    def get_social_format(self):
        """Seleccionar formato de red social"""
        print("\n📱 FORMATOS DISPONIBLES:")
        print("─" * 40)
        
        formats = list(self.social_dimensions.keys())
        for i, format_key in enumerate(formats, 1):
            info = self.social_dimensions[format_key]
            print(f"   {i}. {info['name']} ({info['width']}x{info['height']})")
        
        try:
            choice = int(input("\nSelecciona el formato (número): ")) - 1
            if 0 <= choice < len(formats):
                return formats[choice]
            else:
                return 'instagram_square'  # Default
        except:
            return 'instagram_square'  # Default

    def get_content_parameters(self, content_type):
        """Parámetros específicos según tipo de contenido"""
        print(f"\n🎨 CONFIGURANDO: {content_type.upper()}")
        print("=" * 50)
        
        params = {'content_type': content_type}
        
        # Tema/Nicho
        tema = input("🎯 Tema/Nicho (ej: programación, marketing, diseño): ").strip()
        if not tema:
            tema = "tecnología"
        params['tema'] = tema
        
        # Contenido específico según tipo
        if content_type == "tip":
            params['titulo'] = input("💡 Título del tip: ").strip() or "Consejo Profesional"
            params['descripcion'] = input("📝 Describe el tip que quieres compartir: ").strip() or "Consejo útil para profesionales"
            
        elif content_type == "quote":
            params['frase'] = input("✨ Frase inspiracional: ").strip() or "El éxito llega a quienes se esfuerzan"
            params['autor'] = input("👤 Autor (opcional): ").strip() or ""
            
        elif content_type == "estadistica":
            params['numero'] = input("📊 Número/Porcentaje: ").strip() or "85%"
            params['descripcion'] = input("📝 ¿Qué representa ese número?: ").strip() or "de profesionales consideran esto importante"
            
        elif content_type == "lista":
            params['titulo'] = input("📋 Título de la lista: ").strip() or "5 Consejos Esenciales"
            params['descripcion'] = input("📝 Describe qué tipo de lista: ").strip() or "Lista de consejos profesionales"
            
        elif content_type == "hecho":
            params['titulo'] = input("🔥 Título del hecho: ").strip() or "¿Sabías que...?"
            params['descripcion'] = input("📝 El hecho curioso: ").strip() or "Dato interesante sobre el tema"
            
        elif content_type == "tutorial":
            params['titulo'] = input("📚 Título del tutorial: ").strip() or "Cómo hacer..."
            params['pasos'] = input("📝 Número de pasos (3-5): ").strip() or "4"
            
        elif content_type == "concepto":
            params['concepto'] = input("🧠 Concepto a explicar (ej: Red Neuronal, SOLID, Microservicios): ").strip() or "Algoritmo"
            params['descripcion'] = input("📝 Breve descripción del concepto: ").strip() or "Explicación técnica simplificada"
            
            # Nivel de complejidad
            print("\n📚 NIVEL DE EXPLICACIÓN:")
            niveles = ["Básico (principiantes)", "Intermedio (con algo de experiencia)", "Avanzado (profesionales)"]
            for i, nivel in enumerate(niveles, 1):
                print(f"   {i}. {nivel}")
            
            try:
                nivel_idx = int(input("Nivel de explicación (número): ")) - 1
                params['nivel'] = ["basico", "intermedio", "avanzado"][nivel_idx] if 0 <= nivel_idx < 3 else "intermedio"
            except:
                params['nivel'] = "intermedio"
            
            # Incluir ejemplo práctico
            incluir_ejemplo = input("¿Incluir ejemplo práctico? (s/n): ").strip().lower()
            params['incluir_ejemplo'] = incluir_ejemplo in ['s', 'si', 'sí', 'y', 'yes']
        
        # Estilo visual
        print("\n🎨 ESTILOS VISUALES:")
        estilos = [
            "Minimalista", "Moderno", "Profesional", "Colorido", 
            "Gradientes", "Oscuro", "Neón", "Elegante"
        ]
        for i, estilo in enumerate(estilos, 1):
            print(f"   {i}. {estilo}")
        
        try:
            estilo_idx = int(input("Estilo visual (número): ")) - 1
            params['estilo'] = estilos[estilo_idx] if 0 <= estilo_idx < len(estilos) else "Moderno"
        except:
            params['estilo'] = "Moderno"
        
        # Colores
        print("\n🌈 PALETAS DE COLORES:")
        paletas = [
            "Azul profesional", "Verde tech", "Púrpura moderno", "Naranja energético",
            "Rojo impactante", "Gradiente sunset", "Monocromático", "Colores marca"
        ]
        for i, paleta in enumerate(paletas, 1):
            print(f"   {i}. {paleta}")
        
        try:
            color_idx = int(input("Paleta de colores (número): ")) - 1
            params['colores'] = paletas[color_idx] if 0 <= color_idx < len(paletas) else "Azul profesional"
        except:
            params['colores'] = "Azul profesional"
        
        # Formato de red social
        params['formato'] = self.get_social_format()
        
        # Nombre del archivo
        nombre = input("\n💾 Nombre del archivo (sin extensión): ").strip()
        if not nombre:
            if content_type == "concepto":
                nombre = f"concepto_{params['concepto'].replace(' ', '_')}"
            else:
                nombre = f"{content_type}_{tema.replace(' ', '_')}"
        params['nombre_archivo'] = nombre
        
        return params

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
        """Prompt específico para contenido social - VERSIÓN MEJORADA"""
        
        # Obtener dimensiones
        dimensions = self.social_dimensions[params['formato']]
        
        # Solo usar 1 plantilla para reducir tamaño del prompt
        template_content = ""
        if templates:
            template_content = f"\n--- TEMPLATE DE REFERENCIA ---\n"
            template_content += templates[0]['content'][:600]  # Reducido aún más
        
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
        """Especificaciones según tipo de contenido - SIMPLIFICADAS"""
        content_type = params['content_type']
        
        if content_type == "tip":
            return f"TIP: {params['titulo']}\nDescripción: {params['descripcion']}"
            
        elif content_type == "quote":
            autor_text = f"- {params['autor']}" if params['autor'] else ""
            return f"QUOTE: {params['frase']}\nAutor: {autor_text}"
            
        elif content_type == "estadistica":
            return f"ESTADÍSTICA: {params['numero']}\nDescripción: {params['descripcion']}"
            
        elif content_type == "lista":
            return f"LISTA: {params['titulo']}\nTipo: {params['descripcion']}"
            
        elif content_type == "hecho":
            return f"HECHO: {params['titulo']}\nContenido: {params['descripcion']}"
            
        elif content_type == "tutorial":
            return f"TUTORIAL: {params['titulo']}\nPasos: {params['pasos']}"
            
        elif content_type == "concepto":
            ejemplo_text = ""
            if params.get('incluir_ejemplo'):
                ejemplo_text = "\nIncluir ejemplo práctico"
            return f"CONCEPTO: {params['concepto']}\nDescripción: {params['descripcion']}\nNivel: {params['nivel']}{ejemplo_text}"
        
        return ""

    async def generate_social_content(self, content_type):
        """Genera contenido social específico"""
        if not self.templates_folder:
            if not self.get_templates_folder():
                return

        print(f"\n{'='*60}")
        print(f"📱 GENERANDO CONTENIDO: {content_type.upper()}")
        print('='*60)
        
        # Obtener parámetros
        params = self.get_content_parameters(content_type)
        
        # Mostrar resumen
        print(f"\n📋 RESUMEN DEL POST:")
        print("─" * 30)
        dimensions = self.social_dimensions[params['formato']]
        print(f"   Formato: {dimensions['name']}")
        print(f"   Tema: {params['tema']}")
        if content_type == "concepto":
            print(f"   Concepto: {params['concepto']}")
            print(f"   Nivel: {params['nivel']}")
        print(f"   Estilo: {params['estilo']}")
        print(f"   Colores: {params['colores']}")
        
        confirmar = input(f"\n¿Generar post '{params['nombre_archivo']}'? (s/n): ").strip().lower()
        if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Generación cancelada")
            return
        
        await self._generate_content(params)

    async def generate_multiple_content(self):
        """Genera múltiples posts"""
        if not self.templates_folder:
            if not self.get_templates_folder():
                return
        
        print("\n" + "="*60)
        print("🚀 GENERACIÓN MÚLTIPLE DE POSTS")
        print("="*60)
        
        # Tipos de contenido disponibles
        content_types = ["tip", "quote", "estadistica", "lista", "hecho", "tutorial", "concepto"]
        
        try:
            cantidad = int(input("¿Cuántos posts quieres generar? (1-10): "))
            if cantidad < 1 or cantidad > 10:
                cantidad = 5
        except:
            cantidad = 5
        
        posts = []
        for i in range(cantidad):
            print(f"\n--- POST {i+1}/{cantidad} ---")
            print("Tipos: tip, quote, estadistica, lista, hecho, tutorial, concepto")
            tipo = input("Tipo de contenido: ").strip().lower()
            if tipo not in content_types:
                tipo = "tip"
            
            params = self.get_content_parameters(tipo)
            posts.append(params)
        
        # Generar todos
        for i, params in enumerate(posts):
            print(f"\n🔄 Generando post {i+1}/{len(posts)}")
            await self._generate_content(params)
            
            if i < len(posts) - 1:
                print("⏳ Pausa de 3 segundos...")
                await asyncio.sleep(3)

    async def _generate_content(self, params):
        """Lógica central de generación - VERSIÓN PERSISTENTE"""
        try:
            print("🔍 INICIANDO GENERACIÓN...")
            print(f"   Archivo: {params['nombre_archivo']}")
            print(f"   Tipo: {params['content_type']}")
            
            print("📁 Cargando plantillas...")
            templates = self.load_templates(self.templates_folder)
            print(f"   ✅ {len(templates)} plantillas cargadas")
            
            print("🛠️ Creando prompts...")
            system_prompt = self.create_system_prompt()
            user_prompt = self.create_content_prompt(templates, params)
            
            # DEBUG: Mostrar tamaños de prompts
            print(f"   📏 System prompt: {len(system_prompt)} caracteres")
            print(f"   📏 User prompt: {len(user_prompt)} caracteres")
            
            total_chars = len(system_prompt) + len(user_prompt)
            print(f"   📊 Total: {total_chars} caracteres")
            
            if total_chars > 2000:
                print(f"   ⚠️ Prompts largos ({total_chars} chars)")
                print("   ⏳ Esto puede tomar varios minutos...")
                
                # Preguntar al usuario si quiere esperar o usar fallback
                choice = input("\n¿Cómo proceder?\n   1. ⏳ Esperar a DeepSeek (puede tardar 3-5 minutos)\n   2. ⚡ Usar fallback rápido\n   Opción (1/2): ").strip()
                
                if choice == "2":
                    print("🚀 Usando fallback por elección del usuario...")
                    return await self._generate_fallback_content(params)
                else:
                    print("⏳ Esperando pacientemente a DeepSeek...")
            
            print("🤖 Llamando a DeepSeek...")
            print("   ⏳ Timeout configurado a 5 minutos (300 segundos)...")
            print("   ☕ Ve por un café, esto puede tardar...")
            
            # Intentos múltiples con timeouts progresivos
            max_attempts = 3
            timeouts = [180, 240, 300]  # 3, 4, 5 minutos
            
            for attempt in range(max_attempts):
                try:
                    timeout_seconds = timeouts[attempt]
                    print(f"\n🔄 Intento {attempt + 1}/{max_attempts} (timeout: {timeout_seconds//60} minutos)")
                    
                    response = await asyncio.wait_for(
                        asyncio.to_thread(
                            self.reasoner.chat,
                            message=user_prompt,
                            system_prompt=system_prompt,
                            temperature=0.3,  # Balanceado
                            max_tokens=4000,  # Aumentado para respuestas completas
                            maintain_history=False
                        ),
                        timeout=timeout_seconds
                    )
                    
                    print("✅ Respuesta recibida de DeepSeek!")
                    break
                    
                except asyncio.TimeoutError:
                    print(f"❌ TIMEOUT en intento {attempt + 1} ({timeout_seconds//60} min)")
                    if attempt < max_attempts - 1:
                        print("🔄 Reintentando con más tiempo...")
                        continue
                    else:
                        print("❌ TIMEOUT FINAL: DeepSeek no respondió en 5 minutos")
                        
                        # Última oportunidad: permitir al usuario decidir
                        final_choice = input("\n❓ ¿Qué hacer?\n   1. 🔄 Intentar una vez más (5 min adicionales)\n   2. 🛡️ Usar fallback\n   3. ❌ Cancelar\n   Opción (1/2/3): ").strip()
                        
                        if final_choice == "1":
                            print("🔄 Último intento con máxima paciencia...")
                            try:
                                response = await asyncio.wait_for(
                                    asyncio.to_thread(
                                        self.reasoner.chat,
                                        message=user_prompt,
                                        system_prompt=system_prompt,
                                        temperature=0.3,
                                        max_tokens=4000,
                                        maintain_history=False
                                    ),
                                    timeout=300  # 5 minutos más
                                )
                                print("✅ ¡Respuesta final recibida!")
                                break
                            except asyncio.TimeoutError:
                                print("❌ Timeout definitivo - Usando fallback")
                                return await self._generate_fallback_content(params)
                        elif final_choice == "2":
                            return await self._generate_fallback_content(params)
                        else:
                            print("❌ Generación cancelada por el usuario")
                            return False
            
            print(f"   📊 Success: {response.get('success', False)}")
            
            if response["success"]:
                html_content = response["response"]
                print(f"   📏 HTML recibido: {len(html_content)} caracteres")
                
                # DEBUG: Mostrar la respuesta completa si es corta o vacía
                if len(html_content) < 200:
                    print("🔍 RESPUESTA COMPLETA DE DEEPSEEK:")
                    print("─" * 50)
                    print(repr(html_content))
                    print("─" * 50)
                else:
                    print("🔍 Previsualizando HTML...")
                    print("   " + html_content[:200] + "...")
                
                # Verificar si hay contenido antes de limpiar
                if not html_content or html_content.strip() == "":
                    print("❌ ERROR: DeepSeek devolvió respuesta vacía")
                    print("🔄 Intentando generar con prompt más específico...")
                    
                    # Reintentar con prompt más específico
                    simple_prompt = f"""Genera SOLO código HTML para un post de {params['content_type']} sobre {params['tema']}.

Debe incluir:
- DOCTYPE html completo
- Head con Tailwind CSS CDN
- Body con el contenido
- Dimensiones: {self.social_dimensions[params['formato']]['width']}x{self.social_dimensions[params['formato']]['height']}px

Responde ÚNICAMENTE con HTML válido, sin explicaciones."""
                    
                    retry_response = await asyncio.wait_for(
                        asyncio.to_thread(
                            self.reasoner.chat,
                            message=simple_prompt,
                            system_prompt="Generas HTML válido. Solo código, sin explicaciones.",
                            temperature=0.1,
                            max_tokens=2000,
                            maintain_history=False
                        ),
                        timeout=120
                    )
                    
                    if retry_response.get("success") and retry_response.get("response"):
                        html_content = retry_response["response"]
                        print(f"✅ Reintento exitoso: {len(html_content)} caracteres")
                    else:
                        print("❌ Reintento falló - Usando fallback")
                        return await self._generate_fallback_content(params)
                
                # Limpiar HTML con mejor lógica
                print("🧹 Limpiando HTML...")
                original_length = len(html_content)
                original_content = html_content
                
                # Intentar múltiples métodos de extracción
                if '```html' in html_content:
                    html_content = html_content.split('```html')[1].split('```')[0].strip()
                elif '```' in html_content:
                    html_content = html_content.split('```')[1].split('```')[0].strip()
                elif '<!DOCTYPE' in html_content:
                    # Ya es HTML directo
                    html_content = html_content.strip()
                elif '<html' in html_content.lower():
                    # Extraer desde <html>
                    start = html_content.lower().find('<html')
                    if start != -1:
                        html_content = html_content[start:].strip()
                
                print(f"   📏 HTML limpio: {len(html_content)} caracteres (antes: {original_length})")
                
                # Validar HTML básico
                if not html_content.strip():
                    print("❌ ERROR: HTML vacío después de limpiar")
                    print("📋 Contenido original:")
                    print(repr(original_content[:500]))
                    
                    fallback_choice = input("\n🤔 ¿Usar fallback? (s/n): ").strip().lower()
                    if fallback_choice in ['s', 'si', 'sí', 'y', 'yes']:
                        return await self._generate_fallback_content(params)
                    return False
                    
                # Verificar que contenga estructura HTML mínima
                html_lower = html_content.lower()
                if 'html' not in html_lower and 'body' not in html_lower:
                    print("⚠️ WARNING: No se detecta estructura HTML válida")
                    print("🔄 Intentando crear HTML válido con el contenido...")
                    
                    # Envolver en estructura HTML básica
                    dimensions = self.social_dimensions[params['formato']]
                    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{params['nombre_archivo']}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body style="width: {dimensions['width']}px; height: {dimensions['height']}px; margin: 0; padding: 0;">
    <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-white p-8">
        <div class="text-center max-w-md">
            <div class="text-lg text-gray-800">{html_content}</div>
        </div>
    </div>
</body>
</html>"""
                
                # Guardar HTML
                print("💾 Guardando HTML...")
                html_filename = f"{params['nombre_archivo']}.html"
                with open(html_filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"✅ HTML guardado: {html_filename}")
                
                # Convertir a imagen con dimensiones correctas
                print("🖼️ Convirtiendo a imagen...")
                image_filename = f"{params['nombre_archivo']}.png"
                success = await self.html_to_social_image(html_content, image_filename, params['formato'])
                
                if success:
                    print(f"🎉 Post '{params.get('titulo', params.get('concepto', params['tema']))}' completado!")
                    print("⏱️ ¡Valió la pena esperar!")
                    return True
                else:
                    print("❌ Error en la conversión a imagen")
                    return False
                    
            else:
                print(f"❌ Error en DeepSeek: {response.get('error', 'Error desconocido')}")
                if 'response' in response:
                    print(f"   📄 Respuesta parcial: {response['response'][:500]}...")
                
                # Ofrecer fallback después del error
                fallback_choice = input("\n🤔 ¿Usar fallback después del error? (s/n): ").strip().lower()
                if fallback_choice in ['s', 'si', 'sí', 'y', 'yes']:
                    return await self._generate_fallback_content(params)
                return False
                
        except Exception as e:
            print(f"❌ ERROR INESPERADO: {e}")
            print("📋 Traceback completo:")
            traceback.print_exc()
            
            # Ofrecer fallback después del error
            fallback_choice = input("\n🤔 ¿Usar fallback después del error? (s/n): ").strip().lower()
            if fallback_choice in ['s', 'si', 'sí', 'y', 'yes']:
                return await self._generate_fallback_content(params)
            return False

    def create_minimal_prompt(self, params):
        """Prompt minimalista sin plantillas"""
        dimensions = self.social_dimensions[params['formato']]
        content_type = params['content_type']
        
        if content_type == "tip":
            content = f"TIP: {params.get('titulo', 'Consejo')} sobre {params['tema']}"
        elif content_type == "quote":
            content = f"QUOTE: {params.get('frase', 'Frase inspiracional')}"
        elif content_type == "estadistica":
            content = f"STAT: {params.get('numero', '85%')} sobre {params['tema']}"
        elif content_type == "lista":
            content = f"LISTA: {params.get('titulo', 'Tips')} sobre {params['tema']}"
        elif content_type == "hecho":
            content = f"DATO: {params.get('titulo', 'Hecho curioso')} sobre {params['tema']}"
        elif content_type == "tutorial":
            content = f"TUTORIAL: {params.get('titulo', 'Cómo hacer')} - {params.get('pasos', '3')} pasos"
        elif content_type == "concepto":
            content = f"CONCEPTO: {params.get('concepto', 'Término técnico')} - Explicación {params.get('nivel', 'intermedio')}"
        else:
            content = f"POST sobre {params['tema']}"
        
        return f"""Genera HTML completo para post de red social:

CONTENIDO: {content}
DIMENSIONES: {dimensions['width']}x{dimensions['height']}px
ESTILO: {params['estilo']}
COLORES: {params['colores']}

ESTRUCTURA OBLIGATORIA:
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body style="width: {dimensions['width']}px; height: {dimensions['height']}px;">
    <!-- CONTENIDO AQUÍ -->
</body>
</html>

Responde SOLO con HTML válido, sin explicaciones."""

    async def _generate_fallback_content(self, params):
        """Genera contenido HTML básico cuando DeepSeek falla"""
        try:
            print("🛡️ MODO FALLBACK: Generando HTML sin IA...")
            
            dimensions = self.social_dimensions[params['formato']]
            
            # Plantilla HTML básica pero funcional
            fallback_html = self._create_basic_html_template(params, dimensions)
            
            # Guardar HTML de respaldo
            html_filename = f"{params['nombre_archivo']}_fallback.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(fallback_html)
            print(f"✅ HTML de respaldo guardado: {html_filename}")
            
            # Convertir a imagen
            image_filename = f"{params['nombre_archivo']}_fallback.png"
            success = await self.html_to_social_image(fallback_html, image_filename, params['formato'])
            
            if success:
                print(f"🎉 Post de respaldo completado!")
                print("💡 Aunque es básico, es funcional y puedes editarlo manualmente.")
                return True
            else:
                print("❌ Error incluso en modo fallback")
                return False
                
        except Exception as e:
            print(f"❌ Error crítico en fallback: {e}")
            return False

    def _create_basic_html_template(self, params, dimensions):
        """Crea plantilla HTML básica sin IA"""
        content_type = params['content_type']
        
        # Contenido específico según tipo
        if content_type == "tip":
            main_content = f"""
            <div class="text-blue-600 text-sm font-semibold mb-2">💡 TIP PROFESIONAL</div>
            <h1 class="text-2xl font-bold mb-4 text-gray-800">{params['titulo']}</h1>
            <p class="text-gray-600 text-base leading-relaxed">{params['descripcion']}</p>
            """
        elif content_type == "quote":
            main_content = f"""
            <div class="text-6xl text-gray-300 mb-4">"</div>
            <p class="text-xl font-medium text-gray-800 italic mb-4">{params['frase']}</p>
            {f'<div class="text-gray-600">- {params["autor"]}</div>' if params.get('autor') else ''}
            """
        elif content_type == "estadistica":
            main_content = f"""
            <div class="text-5xl font-bold text-blue-600 mb-4">{params['numero']}</div>
            <p class="text-lg text-gray-700">{params['descripcion']}</p>
            <div class="text-sm text-gray-500 mt-4">📊 ESTADÍSTICA</div>
            """
        elif content_type == "concepto":
            nivel_emoji = {"basico": "🌱", "intermedio": "🚀", "avanzado": "⚡"}
            nivel_text = {"basico": "Nivel Básico", "intermedio": "Nivel Intermedio", "avanzado": "Nivel Avanzado"}
            emoji = nivel_emoji.get(params.get('nivel', 'intermedio'), '🚀')
            nivel = nivel_text.get(params.get('nivel', 'intermedio'), 'Nivel Intermedio')
            
            main_content = f"""
            <div class="text-purple-600 text-sm font-semibold mb-2">🧠 CONCEPTO TECH</div>
            <h1 class="text-3xl font-bold mb-4 text-gray-800">{params['concepto']}</h1>
            <p class="text-gray-600 text-base leading-relaxed mb-4">{params['descripcion']}</p>
            <div class="text-sm text-purple-500 font-medium">{emoji} {nivel}</div>
            """
        else:
            main_content = f"""
            <h1 class="text-2xl font-bold mb-4 text-gray-800">{params.get('titulo', params['tema'])}</h1>
            <p class="text-gray-600">{params.get('descripcion', 'Contenido sobre ' + params['tema'])}</p>
            """
        
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{params['nombre_archivo']}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body style="width: {dimensions['width']}px; height: {dimensions['height']}px; margin: 0; padding: 0;">
    <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-white p-8">
        <div class="text-center max-w-md">
            {main_content}
            <div class="mt-6 text-xs text-gray-400">{params['tema']}</div>
        </div>
    </div>
</body>
</html>"""

    async def html_to_social_image(self, html_content, output_path, social_format):
        """Convierte HTML a imagen con dimensiones de red social"""
        try:
            print("🌐 Iniciando conversión HTML → PNG...")
            dimensions = self.social_dimensions[social_format]
            print(f"   📐 Dimensiones: {dimensions['width']}x{dimensions['height']}px")
            
            async with async_playwright() as p:
                print("   🚀 Lanzando navegador...")
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(
                    viewport={
                        'width': dimensions['width'], 
                        'height': dimensions['height']
                    }
                )
                
                print("   📄 Cargando contenido HTML...")
                await page.set_content(html_content, wait_until='networkidle')
                
                print("   ⏳ Esperando renderizado...")
                await page.wait_for_timeout(3000)  # Aumentado a 3 segundos
                
                print("   📸 Tomando screenshot...")
                await page.screenshot(
                    path=output_path,
                    type='png',
                    full_page=False  # Solo el viewport
                )
                
                await browser.close()
                print(f"✅ Imagen guardada: {output_path}")
                return True
                
        except Exception as e:
            print(f"❌ Error en conversión a imagen: {e}")
            traceback.print_exc()
            return False

    def load_templates(self, templates_folder):
        """Carga plantillas HTML"""
        templates = []
        folder_path = Path(templates_folder)
        
        for html_file in folder_path.glob("*.html"):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    templates.append({
                        'filename': html_file.name,
                        'content': content
                    })
            except Exception as e:
                print(f"⚠️ Error leyendo {html_file}: {e}")
        
        return templates

    def get_templates_folder(self):
        """Configura carpeta de plantillas"""
        while True:
            print("\n📁 CONFIGURACIÓN DE PLANTILLAS")
            print("─" * 50)
            
            folder = input("Ruta de plantillas: ").strip()
            if not folder:
                folder = "./plantillas"
            
            folder_path = Path(folder)
            if folder_path.exists() and folder_path.is_dir():
                html_files = list(folder_path.glob("*.html"))
                if html_files:
                    self.templates_folder = folder
                    print(f"✅ {len(html_files)} plantillas encontradas")
                    return True
                else:
                    print("❌ No hay archivos HTML")
            else:
                print("❌ Carpeta no válida")
            
            if input("¿Reintentar? (s/n): ").lower() not in ['s', 'si', 'sí']:
                return False

    def show_social_formats(self):
        """Muestra formatos disponibles"""
        print("\n📱 FORMATOS DE REDES SOCIALES")
        print("=" * 50)
        for key, info in self.social_dimensions.items():
            print(f"📐 {info['name']}: {info['width']}x{info['height']}px")

    async def generate_random_idea(self):
        """Genera ideas aleatorias para publicaciones"""
        print("\n" + "="*60)
        print("🎲 GENERADOR DE IDEAS ALEATORIAS")
        print("="*60)
        
        # Bancos de datos para generar ideas
        content_types = [
            {"type": "tip", "name": "💡 Tip/Consejo", "emoji": "💡"},
            {"type": "quote", "name": "✨ Quote inspiracional", "emoji": "✨"},
            {"type": "estadistica", "name": "📊 Estadística/Datos", "emoji": "📊"},
            {"type": "lista", "name": "🎯 Lista de consejos", "emoji": "🎯"},
            {"type": "hecho", "name": "🔥 Hecho curioso", "emoji": "🔥"},
            {"type": "tutorial", "name": "📋 Tutorial paso a paso", "emoji": "📋"},
            {"type": "concepto", "name": "🧠 Concepto técnico", "emoji": "🧠"}
        ]
        
        themes = [
            "Programación", "Marketing Digital", "Diseño Gráfico", "Emprendimiento",
            "Productividad", "Inteligencia Artificial", "Redes Sociales", "E-commerce",
            "UX/UI Design", "Data Science", "Desarrollo Web", "Mobile Development",
            "Blockchain", "Ciberseguridad", "SEO", "Content Marketing", "Branding",
            "Freelancing", "Startups", "Tecnología", "Innovación", "Leadership",
            "Remote Work", "Growth Hacking", "Analytics", "Cloud Computing"
        ]
        
        # Conceptos técnicos populares
        conceptos_tecnicos = [
            "API REST", "Machine Learning", "Blockchain", "Microservicios", "Docker",
            "Kubernetes", "DevOps", "CI/CD", "SOLID", "Clean Code", "Design Patterns",
            "Arquitectura MVC", "Base de Datos NoSQL", "GraphQL", "React Hooks",
            "Async/Await", "Websockets", "OAuth", "JWT", "Scrum", "Agile",
            "Test Driven Development", "Pair Programming", "Code Review",
            "Git Flow", "Responsive Design", "PWA", "SEO", "GDPR",
            "Red Neuronal", "Deep Learning", "Big Data", "Cloud Computing",
            "Serverless", "Edge Computing", "IoT", "Cybersecurity", "VPN"
        ]
        
        tip_ideas = [
            "Mejores prácticas para", "Errores comunes en", "Herramientas esenciales para",
            "Tendencias 2025 en", "Secretos de profesionales en", "Optimización de",
            "Automatización en", "Estrategias avanzadas de", "Fundamentos de",
            "El futuro de", "Cómo destacar en", "Principios básicos de"
        ]
        
        quote_themes = [
            "Motivación profesional", "Superación personal", "Innovación tecnológica",
            "Liderazgo empresarial", "Creatividad y diseño", "Perseverancia",
            "Aprendizaje continuo", "Transformación digital", "Trabajo en equipo",
            "Visión de futuro", "Adaptación al cambio", "Excelencia profesional"
        ]
        
        stats_topics = [
            "usuarios de redes sociales", "tendencias de mercado", "comportamiento del consumidor",
            "adopción de tecnología", "productividad empresarial", "inversión en startups",
            "crecimiento del e-commerce", "uso de herramientas digitales", "preferencias generacionales",
            "impacto de la IA", "trabajo remoto", "transformación digital"
        ]
        
        tutorial_topics = [
            "Configurar", "Optimizar", "Crear desde cero", "Automatizar", "Analizar",
            "Implementar", "Diseñar", "Desarrollar", "Monitorear", "Escalar",
            "Integrar", "Personalizar", "Debuggear", "Deployar", "Testear"
        ]
        
        while True:
            print("\n🎯 OPCIONES DE GENERACIÓN:")
            print("─" * 40)
            print("   1. 🎲 Idea completamente aleatoria")
            print("   2. 🎨 Elegir tipo de contenido primero")
            print("   3. 📚 Elegir tema/nicho primero")
            print("   4. 🤖 Idea generada por IA")
            print("   5. 💡 Ideas predefinidas")
            print("   6. ↩️ Volver al menú principal")
            
            try:
                choice = input("\nSelecciona opción (1-6): ").strip()
                
                if choice == "1":
                    # Idea completamente aleatoria
                    content = random.choice(content_types)
                    theme = random.choice(themes)
                    
                    if content["type"] == "tip":
                        approach = random.choice(tip_ideas)
                        idea = f"{approach} {theme.lower()}"
                    elif content["type"] == "quote":
                        approach = random.choice(quote_themes)
                        idea = f"Frase inspiracional sobre {approach.lower()}"
                    elif content["type"] == "estadistica":
                        stat_topic = random.choice(stats_topics)
                        percentage = random.choice(["73%", "85%", "92%", "67%", "78%", "95%", "63%", "88%"])
                        idea = f"{percentage} de {stat_topic} en {theme.lower()}"
                    elif content["type"] == "lista":
                        number = random.choice([3, 4, 5, 7, 10])
                        approach = random.choice(tip_ideas)
                        idea = f"{number} {approach.lower()} {theme.lower()}"
                    elif content["type"] == "hecho":
                        idea = f"Dato curioso sobre {theme.lower()}"
                    elif content["type"] == "tutorial":
                        action = random.choice(tutorial_topics)
                        idea = f"Cómo {action.lower()} en {theme.lower()}"
                    elif content["type"] == "concepto":
                        concepto = random.choice(conceptos_tecnicos)
                        nivel = random.choice(["básico", "intermedio", "avanzado"])
                        idea = f"Explicar '{concepto}' nivel {nivel}"
                    
                    result = await self._display_idea(content, theme, idea)
                    if result == "nueva":
                        continue  # Generar nueva idea
                    elif result == "volver":
                        break  # Salir del bucle
                    
                elif choice == "2":
                    # Elegir tipo primero
                    print("\n🎨 TIPOS DE CONTENIDO:")
                    for i, ct in enumerate(content_types, 1):
                        print(f"   {i}. {ct['name']}")
                    
                    try:
                        type_choice = int(input("\nElige tipo (1-7): ")) - 1
                        if 0 <= type_choice < len(content_types):
                            content = content_types[type_choice]
                            theme = random.choice(themes)
                            idea = self._generate_specific_idea(content["type"], theme, tip_ideas, quote_themes, stats_topics, tutorial_topics, conceptos_tecnicos)
                            result = await self._display_idea(content, theme, idea)
                            if result == "nueva":
                                continue
                            elif result == "volver":
                                break
                    except:
                        print("❌ Opción no válida")
                    
                elif choice == "3":
                    # Elegir tema primero
                    print("\n📚 TEMAS/NICHOS POPULARES:")
                    random_themes = random.sample(themes, 10)  # Mostrar 10 aleatorios
                    for i, theme in enumerate(random_themes, 1):
                        print(f"   {i}. {theme}")
                    print("   11. 🎲 Tema aleatorio")
                    
                    try:
                        theme_choice = int(input("\nElige tema (1-11): "))
                        if 1 <= theme_choice <= 10:
                            selected_theme = random_themes[theme_choice - 1]
                        else:
                            selected_theme = random.choice(themes)
                        
                        content = random.choice(content_types)
                        idea = self._generate_specific_idea(content["type"], selected_theme, tip_ideas, quote_themes, stats_topics, tutorial_topics, conceptos_tecnicos)
                        result = await self._display_idea(content, selected_theme, idea)
                        if result == "nueva":
                            continue
                        elif result == "volver":
                            break
                    except:
                        print("❌ Opción no válida")
                
                elif choice == "4":
                    # Idea generada por IA
                    print("\n🤖 Generando idea con IA...")
                    await self._generate_ai_idea()
                
                elif choice == "5":
                    # Ideas predefinidas como respaldo
                    print("\n💡 Mostrando ideas predefinidas...")
                    self.generate_simple_ai_idea()
                
                elif choice == "6":
                    break
                else:
                    print("❌ Opción no válida")
                    
            except KeyboardInterrupt:
                break

    def _generate_specific_idea(self, content_type, theme, tip_ideas, quote_themes, stats_topics, tutorial_topics, conceptos_tecnicos):
        """Genera idea específica según tipo de contenido"""
        if content_type == "tip":
            approach = random.choice(tip_ideas)
            return f"{approach} {theme.lower()}"
        elif content_type == "quote":
            approach = random.choice(quote_themes)
            return f"Frase inspiracional sobre {approach.lower()} en {theme.lower()}"
        elif content_type == "estadistica":
            stat_topic = random.choice(stats_topics)
            percentage = random.choice(["73%", "85%", "92%", "67%", "78%", "95%", "63%", "88%"])
            return f"{percentage} de {stat_topic} en {theme.lower()}"
        elif content_type == "lista":
            number = random.choice([3, 4, 5, 7, 10])
            approach = random.choice(tip_ideas)
            return f"{number} {approach.lower()} {theme.lower()}"
        elif content_type == "hecho":
            return f"Dato curioso sobre {theme.lower()}"
        elif content_type == "tutorial":
            actions = ["Configurar", "Optimizar", "Crear", "Automatizar", "Implementar"]
            action = random.choice(actions)
            return f"Cómo {action.lower()} en {theme.lower()}"
        elif content_type == "concepto":
            concepto = random.choice(conceptos_tecnicos)
            nivel = random.choice(["básico", "intermedio", "avanzado"])
            return f"Explicar '{concepto}' nivel {nivel}"
        return f"Contenido sobre {theme.lower()}"

    async def _display_idea(self, content, theme, idea):
        """Muestra la idea generada"""
        print("\n" + "🎉 IDEA GENERADA 🎉".center(60, "="))
        print(f"\n{content['emoji']} TIPO: {content['name']}")
        print(f"🎯 TEMA: {theme}")
        print(f"💡 IDEA: {idea}")
        print("\n" + "="*60)
        
        action = input("\n¿Qué quieres hacer? (g=generar post / n=nueva idea / v=volver): ").strip().lower()
        
        if action in ['g', 'generar', 'gen']:
            print(f"\n🚀 ¡Perfecto! Configurando {content['name'].lower()}...")
            # Pre-llenar algunos datos basados en la idea
            params = self._auto_fill_idea(content["type"], theme, idea)
            if params:
                # Mostrar resumen antes de generar
                print(f"\n📋 RESUMEN DEL POST:")
                print("─" * 30)
                print(f"   Tipo: {content['name']}")
                print(f"   Tema: {params['tema']}")
                if content["type"] == "concepto":
                    print(f"   Concepto: {params.get('concepto', 'N/A')}")
                print(f"   Formato: {self.social_dimensions[params['formato']]['name']}")
                print(f"   Estilo: {params['estilo']}")
                print(f"   Colores: {params['colores']}")
                
                confirmar = input(f"\n¿Generar post '{params['nombre_archivo']}'? (s/n): ").strip().lower()
                if confirmar in ['s', 'si', 'sí', 'y', 'yes']:
                    # Ahora sí podemos usar await aquí
                    await self._generate_content(params)
                else:
                    print("❌ Generación cancelada")
        elif action in ['n', 'nueva', 'new']:
            print("\n🎲 Generando nueva idea...")
            return "nueva"  # Señal para generar nueva idea
        else:
            print("\n↩️ Volviendo...")
            return "volver"  # Señal para volver

    def _auto_fill_idea(self, content_type, theme, idea):
        """Auto-completa parámetros basados en la idea generada"""
        print(f"\n🎨 CONFIGURANDO: {content_type.upper()} - {theme}")
        print("=" * 50)
        print("💡 Datos pre-llenados basados en tu idea:")
        print(f"   🎯 Tema: {theme}")
        print(f"   💡 Concepto: {idea}")
        
        # Crear parámetros base
        params = {
            'content_type': content_type,
            'tema': theme
        }
        
        # Auto-llenar según tipo
        if content_type == "tip":
            params['titulo'] = idea
            params['descripcion'] = input(f"📝 Describe el tip sobre '{idea}': ").strip() or f"Consejo útil sobre {idea.lower()}"
        elif content_type == "quote":
            params['frase'] = input(f"✨ Frase inspiracional sobre '{idea}': ").strip() or "El éxito requiere dedicación y perseverancia"
            params['autor'] = input("👤 Autor (opcional): ").strip() or ""
        elif content_type == "estadistica":
            if "%" in idea:
                params['numero'] = idea.split("%")[0] + "%"
                params['descripcion'] = idea.split("% ")[1] if "% " in idea else idea
            else:
                params['numero'] = input("📊 Número/Porcentaje: ").strip() or "85%"
                params['descripcion'] = idea
        elif content_type == "lista":
            params['titulo'] = idea
            params['descripcion'] = idea
        elif content_type == "hecho":
            params['titulo'] = "¿Sabías que...?"
            params['descripcion'] = input(f"📝 El dato curioso sobre '{theme}': ").strip() or f"Información interesante sobre {theme.lower()}"
        elif content_type == "tutorial":
            params['titulo'] = idea
            params['pasos'] = input("📝 Número de pasos (3-5): ").strip() or "4"
        elif content_type == "concepto":
            # Extraer concepto de la idea si es posible
            if "'" in idea:
                concepto_extraido = idea.split("'")[1]
                params['concepto'] = concepto_extraido
            else:
                params['concepto'] = input("🧠 Concepto a explicar: ").strip() or "Algoritmo"
            
            params['descripcion'] = input(f"📝 Descripción del concepto '{params['concepto']}': ").strip() or f"Explicación técnica de {params['concepto']}"
            
            # Detectar nivel de la idea
            if "básico" in idea.lower():
                params['nivel'] = "basico"
            elif "avanzado" in idea.lower():
                params['nivel'] = "avanzado"
            else:
                params['nivel'] = "intermedio"
            
            # Incluir ejemplo práctico
            incluir_ejemplo = input("¿Incluir ejemplo práctico? (s/n): ").strip().lower()
            params['incluir_ejemplo'] = incluir_ejemplo in ['s', 'si', 'sí', 'y', 'yes']
        
        # Continuar con el resto de la configuración normal
        return self._complete_configuration(params)

    def _complete_configuration(self, params):
        """Completa la configuración de parámetros"""
        # Estilo visual
        print("\n🎨 ESTILOS VISUALES:")
        estilos = [
            "Minimalista", "Moderno", "Profesional", "Colorido", 
            "Gradientes", "Oscuro", "Neón", "Elegante"
        ]
        for i, estilo in enumerate(estilos, 1):
            print(f"   {i}. {estilo}")
        
        try:
            estilo_idx = int(input("Estilo visual (número): ")) - 1
            params['estilo'] = estilos[estilo_idx] if 0 <= estilo_idx < len(estilos) else "Moderno"
        except:
            params['estilo'] = "Moderno"
        
        # Colores
        print("\n🌈 PALETAS DE COLORES:")
        paletas = [
            "Azul profesional", "Verde tech", "Púrpura moderno", "Naranja energético",
            "Rojo impactante", "Gradiente sunset", "Monocromático", "Colores marca"
        ]
        for i, paleta in enumerate(paletas, 1):
            print(f"   {i}. {paleta}")
        
        try:
            color_idx = int(input("Paleta de colores (número): ")) - 1
            params['colores'] = paletas[color_idx] if 0 <= color_idx < len(paletas) else "Azul profesional"
        except:
            params['colores'] = "Azul profesional"
        
        # Formato de red social
        params['formato'] = self.get_social_format()
        
        # Nombre del archivo
        nombre = input("\n💾 Nombre del archivo (sin extensión): ").strip()
        if not nombre:
            if params['content_type'] == "concepto":
                nombre = f"concepto_{params['concepto'].replace(' ', '_')}"
            else:
                nombre = f"{params['content_type']}_{params['tema'].replace(' ', '_')}"
        params['nombre_archivo'] = nombre
        
        # Retornar parámetros para generar después
        return params

    async def _generate_ai_idea(self):
        from prompts.Prompt_Gen_Idea import prompt_gen_idea
        """Genera idea usando IA"""
        try:
            print("🤖 Consultando con la IA para generar ideas creativas...")
            print("   ⏳ Esto puede tomar unos segundos...")
            
            prompt = prompt_gen_idea.prompt
            
            system_prompt = prompt_gen_idea.system_promt
            
            print("   🔍 Enviando solicitud a DeepSeek...")
            
            # La función reasoner.chat() es SINCRÓNICA, usar solo to_thread
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.reasoner.chat,
                    message=prompt,
                    system_prompt=system_prompt,
                    temperature=0.8,
                    max_tokens=1000,
                    maintain_history=False
                ),
                timeout=60  # Aumentado a 60 segundos
            )
            
            print("   ✅ Respuesta recibida de DeepSeek!")
            
            if response and response.get("success"):
                print("\n🎯 IDEAS GENERADAS POR IA:")
                print("=" * 50)
                print(response["response"])
                print("=" * 50)
                
                use_idea = input("\n¿Te gusta alguna idea? (s/n): ").strip().lower()
                if use_idea in ['s', 'si', 'sí', 'y', 'yes']:
                    print("\n💡 ¡Perfecto! Usa los datos de la idea para configurar tu post manualmente.")
                    print("📝 Ve al menú principal y selecciona el tipo de post correspondiente.")
            else:
                error_msg = response.get('error', 'Respuesta vacía o sin éxito') if response else 'No se recibió respuesta'
                print(f"❌ Error en la respuesta de DeepSeek: {error_msg}")
                print("💡 Intenta con las ideas aleatorias tradicionales (opciones 1-3) o predefinidas (opción 5).")
                
        except asyncio.TimeoutError:
            print("❌ Timeout: DeepSeek tardó más de 60 segundos en responder")
            print("💡 Esto puede indicar problemas de conectividad o límites de API.")
            print("🔄 Intenta nuevamente o usa las ideas aleatorias tradicionales.")
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            print(f"❌ Error inesperado: {error_type}")
            print(f"📝 Detalle: {error_msg[:150]}...")
            
            # Errores comunes y sus soluciones
            if "API" in error_msg or "key" in error_msg.lower():
                print("🔑 Posible problema: API key de DeepSeek no configurada o inválida")
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                print("🌐 Posible problema: Sin conexión a internet o problemas de red")
            elif "rate" in error_msg.lower() or "limit" in error_msg.lower():
                print("⏰ Posible problema: Límite de rate de API excedido")
            elif "timeout" in error_msg.lower():
                print("⏱️ Posible problema: DeepSeek está sobrecargado")
            else:
                print("🔧 Error técnico en la integración con DeepSeek")
            
            print("\n💡 SOLUCIONES:")
            print("   • Verifica tu configuración de DeepSeek API")
            print("   • Revisa tu conexión a internet")
            print("   • Usa las ideas aleatorias (opciones 1-3)")
            print("   • Usa las ideas predefinidas (opción 5)")

    def test_deepseek_connection(self):
        """Prueba la conexión con DeepSeek"""
        try:
            print("🔍 Probando conexión con DeepSeek...")
            
            # Prueba simple
            test_response = self.reasoner.chat(
                message="Hola",
                system_prompt="Responde solo: 'Conexión OK'",
                max_tokens=10,
                maintain_history=False
            )
            
            if test_response and test_response.get("success"):
                print("✅ Conexión con DeepSeek: OK")
                print(f"📝 Respuesta de prueba: {test_response.get('response', 'N/A')}")
                return True
            else:
                print("❌ Conexión con DeepSeek: FALLO")
                print(f"📝 Error: {test_response.get('error', 'Respuesta vacía')}")
                return False
                
        except Exception as e:
            print("❌ Error probando DeepSeek:")
            print(f"   {type(e).__name__}: {str(e)[:100]}...")
            return False

    def generate_simple_ai_idea(self):
        """Versión simplificada sin IA - como respaldo"""
        print("\n🎯 IDEAS PREDEFINIDAS CREATIVAS:")
        print("=" * 50)
        
        ideas_predefined = [
            {
                "tipo": "💡 Tip",
                "tema": "Inteligencia Artificial", 
                "titulo": "5 errores que cometen los developers al usar IA",
                "razon": "Muy actual y útil para profesionales"
            },
            {
                "tipo": "📊 Estadística",
                "tema": "Remote Work",
                "titulo": "73% de las empresas mantendrán trabajo híbrido en 2025",
                "razon": "Tendencia post-pandemia relevante"
            },
            {
                "tipo": "🔥 Hecho Curioso",
                "tema": "Programación",
                "titulo": "Python fue nombrado por Monty Python, no por la serpiente",
                "razon": "Dato curioso que pocos conocen"
            },
            {
                "tipo": "🎯 Lista",
                "tema": "Productividad",
                "titulo": "7 herramientas de IA que todo profesional debe conocer",
                "razon": "Combina tendencias actuales con utilidad práctica"
            },
            {
                "tipo": "✨ Quote",
                "tema": "Emprendimiento",
                "titulo": "El fracaso es solo feedback disfrazado",
                "razon": "Motivacional y relacionable para emprendedores"
            },
            {
                "tipo": "🧠 Concepto",
                "tema": "Desarrollo de Software",
                "titulo": "¿Qué es SOLID? Los 5 principios explicados fácil",
                "razon": "Concepto fundamental que todo programador debe conocer"
            },
            {
                "tipo": "🧠 Concepto",
                "tema": "Inteligencia Artificial",
                "titulo": "Red Neuronal vs Cerebro Humano: ¿En qué se parecen?",
                "razon": "Analogía perfecta para explicar IA de forma simple"
            }
        ]
        
        for i, idea in enumerate(ideas_predefined, 1):
            print(f"\n{i}. {idea['tipo']}: {idea['titulo']}")
            print(f"   🎯 Tema: {idea['tema']}")
            print(f"   ⚡ Por qué funciona: {idea['razon']}")
        
        print("\n" + "="*50)
        try:
            choice = int(input("¿Cuál idea te gusta? (1-7): ")) - 1
            if 0 <= choice < len(ideas_predefined):
                selected = ideas_predefined[choice]
                print(f"\n✅ Idea seleccionada: {selected['titulo']}")
                print("📝 Ve al menú principal y configura tu post con esta idea.")
            else:
                print("❌ Opción no válida")
        except:
            print("❌ Entrada no válida")

    async def quick_mode_content(self, content_type):
        """Modo rápido sin plantillas - Genera contenido básico inmediatamente"""
        if not self.templates_folder:
            if not self.get_templates_folder():
                return

        print(f"\n⚡ MODO RÁPIDO: {content_type.upper()}")
        print('='*50)
        print("📝 Generación rápida con prompts minimalistas")
        
        # Obtener parámetros básicos
        params = self.get_content_parameters(content_type)
        
        # Mostrar resumen
        print(f"\n📋 RESUMEN DEL POST:")
        print("─" * 30)
        dimensions = self.social_dimensions[params['formato']]
        print(f"   Formato: {dimensions['name']}")
        print(f"   Tema: {params['tema']}")
        if content_type == "concepto":
            print(f"   Concepto: {params.get('concepto', 'N/A')}")
        print(f"   Modo: Rápido (prompts minimalistas)")
        
        confirmar = input(f"\n¿Generar post rápido '{params['nombre_archivo']}'? (s/n): ").strip().lower()
        if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Generación cancelada")
            return
        
        # Generar con prompts ultra simples
        await self._generate_quick_content(params)

    async def _generate_quick_content(self, params):
        """Genera contenido con prompts ultra minimalistas"""
        try:
            print("⚡ GENERACIÓN RÁPIDA...")
            
            # System prompt minimalista
            system_prompt = "Experto en HTML + Tailwind CSS. Crea posts de redes sociales. Solo código HTML."
            
            # User prompt ultra simple
            user_prompt = self.create_minimal_prompt(params)
            
            print(f"   📏 System prompt: {len(system_prompt)} caracteres")
            print(f"   📏 User prompt: {len(user_prompt)} caracteres")
            print(f"   📊 Total: {len(system_prompt) + len(user_prompt)} caracteres")
            
            print("🚀 Llamando a DeepSeek con prompts ultra-simples...")
            print("   ⏳ Timeout: 60 segundos")
            
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.reasoner.chat,
                        message=user_prompt,
                        system_prompt=system_prompt,
                        temperature=0.1,
                        max_tokens=2000,
                        maintain_history=False
                    ),
                    timeout=60
                )
                
                if response.get("success") and response.get("response"):
                    html_content = response["response"]
                    
                    # Limpiar HTML
                    if '```html' in html_content:
                        html_content = html_content.split('```html')[1].split('```')[0].strip()
                    elif '```' in html_content:
                        html_content = html_content.split('```')[1].split('```')[0].strip()
                    
                    if html_content.strip():
                        # Guardar HTML
                        html_filename = f"{params['nombre_archivo']}_quick.html"
                        with open(html_filename, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        print(f"✅ HTML rápido guardado: {html_filename}")
                        
                        # Convertir a imagen
                        image_filename = f"{params['nombre_archivo']}_quick.png"
                        success = await self.html_to_social_image(html_content, image_filename, params['formato'])
                        
                        if success:
                            print(f"🎉 Post rápido completado!")
                            return True
                
                # Si falla la generación rápida, usar fallback
                print("⚠️ Generación rápida falló - Usando fallback")
                return await self._generate_fallback_content(params)
                
            except asyncio.TimeoutError:
                print("❌ Timeout en modo rápido - Usando fallback")
                return await self._generate_fallback_content(params)
                
        except Exception as e:
            print(f"❌ Error en modo rápido: {e}")
            return await self._generate_fallback_content(params)

    async def diagnostic_test(self):
        """Diagnóstico de DeepSeek para identificar problemas"""
        print("\n🔧 DIAGNÓSTICO DE DEEPSEEK")
        print("=" * 50)
        
        # Test básico
        print("1. 🔍 Probando conexión básica...")
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.reasoner.chat,
                    message="Responde exactamente: 'CONEXIÓN OK'",
                    system_prompt="Responde exactamente lo que se te pide.",
                    max_tokens=50,
                    maintain_history=False
                ),
                timeout=30
            )
            
            if response and response.get("success"):
                print(f"   ✅ Conexión: OK")
                print(f"   📝 Respuesta: '{response.get('response', 'VACÍA')}'")
            else:
                print(f"   ❌ Fallo en conexión: {response.get('error', 'Error desconocido')}")
                return
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
            return
        
        # Test HTML simple
        print("\n2. 🔍 Probando generación HTML simple...")
        try:
            html_prompt = """Genera exactamente este HTML:
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>PRUEBA</h1></body>
</html>"""
            
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.reasoner.chat,
                    message=html_prompt,
                    system_prompt="Genera exactamente el HTML solicitado. Sin explicaciones.",
                    max_tokens=200,
                    maintain_history=False
                ),
                timeout=30
            )
            
            if response and response.get("success"):
                html_response = response.get('response', '')
                print(f"   📏 Longitud: {len(html_response)} caracteres")
                print(f"   📝 Contiene <!DOCTYPE: {'✅' if '<!DOCTYPE' in html_response else '❌'}")
                print(f"   📝 Contiene <html>: {'✅' if '<html>' in html_response else '❌'}")
                print(f"   📝 Contiene <body>: {'✅' if '<body>' in html_response else '❌'}")
                
                if len(html_response) > 10:
                    print("   📋 Muestra de respuesta:")
                    print("   " + repr(html_response[:100]))
                else:
                    print("   📋 Respuesta completa:")
                    print("   " + repr(html_response))
            else:
                print(f"   ❌ Fallo: {response.get('error', 'Error desconocido')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test con Tailwind
        print("\n3. 🔍 Probando HTML con Tailwind...")
        try:
            tailwind_prompt = """Genera HTML con Tailwind:
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-blue-500">
    <div class="text-white text-center p-4">TAILWIND TEST</div>
</body>
</html>"""
            
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.reasoner.chat,
                    message=f"Genera exactamente: {tailwind_prompt}",
                    system_prompt="Genera HTML válido con Tailwind. Sin explicaciones.",
                    max_tokens=300,
                    maintain_history=False
                ),
                timeout=30
            )
            
            if response and response.get("success"):
                html_response = response.get('response', '')
                print(f"   📏 Longitud: {len(html_response)} caracteres")
                print(f"   📝 Contiene Tailwind CDN: {'✅' if 'tailwindcss.com' in html_response else '❌'}")
                print(f"   📝 Contiene clases Tailwind: {'✅' if 'class=' in html_response else '❌'}")
            else:
                print(f"   ❌ Fallo: {response.get('error', 'Error desconocido')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Recomendaciones
        print("\n💡 RECOMENDACIONES:")
        print("─" * 30)
        print("• Si todos los tests pasan pero el contenido está vacío:")
        print("  - Usa prompts más específicos")
        print("  - Reduce la complejidad de las plantillas")
        print("  - Usa el modo rápido (opción 10)")
        print("• Si fallan los tests básicos:")
        print("  - Verifica la configuración de DeepSeek API")
        print("  - Revisa los límites de rate de la API")
        print("  - Verifica la conectividad de red")

    async def run(self):
        """Interfaz principal"""
        self.print_banner()
        
        if not self.get_templates_folder():
            print("❌ Sin plantillas no se puede continuar")
            return
        
        while True:
            self.print_menu()
            try:
                opcion = input("\nSelecciona opción (1-14): ").strip()
                
                if opcion == "1":
                    await self.generate_social_content("tip")
                elif opcion == "2":
                    await self.generate_social_content("quote")
                elif opcion == "3":
                    await self.generate_social_content("estadistica")
                elif opcion == "4":
                    await self.generate_social_content("lista")
                elif opcion == "5":
                    await self.generate_social_content("hecho")
                elif opcion == "6":
                    await self.generate_social_content("tutorial")
                elif opcion == "7":
                    await self.generate_social_content("concepto")
                elif opcion == "8":
                    await self.generate_multiple_content()
                elif opcion == "9":
                    await self.generate_random_idea()
                elif opcion == "10":
                    # Modo rápido con prompts minimalistas
                    print("\n⚡ MODO RÁPIDO - Prompts simples, más rápido")
                    print("Tipos: tip, quote, estadistica, lista, hecho, tutorial, concepto")
                    tipo = input("Tipo de contenido: ").strip().lower()
                    if tipo in ["tip", "quote", "estadistica", "lista", "hecho", "tutorial", "concepto"]:
                        await self.quick_mode_content(tipo)
                    else:
                        print("❌ Tipo no válido")
                elif opcion == "11":
                    self.get_templates_folder()
                elif opcion == "12":
                    self.show_social_formats()
                elif opcion == "13":
                    await self.diagnostic_test()
                elif opcion == "14":
                    print("\n👋 ¡Tus posts están listos para compartir!")
                    break
                else:
                    print("❌ Opción no válida")
                
                if opcion in ["1","2","3","4","5","6","7","8","9","10","13"]:
                    input("\nPresiona Enter para continuar...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break

# EJECUTAR
async def main():
    app = SocialContentGenerator()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())