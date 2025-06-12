import asyncio
import traceback
from pathlib import Path
from playwright.async_api import async_playwright
from enums.social_dimensions import SOCIAL_DIMENSIONS

class HTMLConverterService:
    def __init__(self):
        self.social_dimensions = SOCIAL_DIMENSIONS
    
    async def convert_to_image(self, html_content, output_path, social_format):
        """Convierte HTML a imagen con dimensiones de red social"""
        try:
            print(f"🌐 Iniciando conversión HTML → PNG...")
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
                await page.wait_for_timeout(3000)  # 3 segundos
                
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
    
    def validate_html(self, html_content):
        """Valida que el HTML contenga estructura básica"""
        html_lower = html_content.lower()
        
        checks = {
            'has_doctype': '<!doctype' in html_lower,
            'has_html': '<html' in html_lower,
            'has_head': '<head>' in html_lower,
            'has_body': '<body' in html_lower,
            'has_tailwind': 'tailwindcss.com' in html_content,
            'has_title': '<title>' in html_lower
        }
        
        return checks
    
    async def convert_multiple_formats(self, html_content, base_filename):
        """Convierte HTML a múltiples formatos de redes sociales"""
        results = {}
        
        for format_key, dimensions in self.social_dimensions.items():
            try:
                output_filename = f"{base_filename}_{format_key}.png"
                success = await self.convert_to_image(html_content, output_filename, format_key)
                
                results[format_key] = {
                    'success': success,
                    'filename': output_filename if success else None,
                    'dimensions': dimensions
                }
            except Exception as e:
                results[format_key] = {
                    'success': False,
                    'error': str(e),
                    'dimensions': dimensions
                }
        
        return results
    
    def get_image_info(self, image_path):
        """Obtiene información de la imagen generada"""
        try:
            from PIL import Image
            
            with Image.open(image_path) as img:
                return {
                    'size': img.size,
                    'mode': img.mode,
                    'format': img.format,
                    'file_size': Path(image_path).stat().st_size
                }
        except Exception as e:
            return {'error': str(e)}