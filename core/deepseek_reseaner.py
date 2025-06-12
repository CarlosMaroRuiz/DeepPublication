# Clase que nos servirá para usar deepSeekReseaoner
from config import config
from openai import OpenAI
from tabulate import tabulate
import json
from typing import Optional, Dict, Any, List

class DeepSeekReseaoner:
    def __init__(self):
        # Client para el contexto de nuestra clase
        self.client = OpenAI(api_key=config.api_key, base_url="https://api.deepseek.com")
        self.model = 'deepseek-reasoner'
        self.conversation_history = []  # Para mantener historial de conversación
    
    @staticmethod
    def get_information_temperature():
        """Muestra información sobre temperaturas recomendadas para diferentes casos de uso"""
        data = [
            ["Coding / Math", 0.0],
            ["Data Cleaning / Data Analysis", 1.0], 
            ["General Conversation", 1.3],
            ["Translation", 1.3],
            ["Creative Writing / Poetry", 1.5]
        ]
        headers = ["UseCase", "Temperature"]
        print(tabulate(data, headers=headers, tablefmt="grid"))
    
    def chat(self, 
             message: str, 
             temperature: float = 1.0,
             max_tokens: Optional[int] = None,
             system_prompt: Optional[str] = None,
             stream: bool = False,
             maintain_history: bool = True) -> Dict[str, Any]:
        """
        Envía un mensaje al modelo deepseek-reasoner y maneja errores
        
        Args:
            message: El mensaje del usuario
            temperature: Controla la aleatoriedad (0.0-2.0)
            max_tokens: Máximo número de tokens de salida
            system_prompt: Prompt del sistema (opcional)
            stream: Si usar streaming o no
            maintain_history: Si mantener historial de conversación
            
        Returns:
            Dict con la respuesta y metadatos
        """
        try:
            # Construir mensajes
            messages = []
            
            # Agregar system prompt si se proporciona
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Agregar historial si se mantiene
            if maintain_history and self.conversation_history:
                messages.extend(self.conversation_history)
            
            # Agregar mensaje actual
            messages.append({"role": "user", "content": message})
            
            # Configurar parámetros
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            # Agregar max_tokens si se especifica
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            # Realizar la llamada a la API
            response = self.client.chat.completions.create(**params)
            
            if stream:
                return self._handle_stream_response(response, message, maintain_history)
            else:
                return self._handle_standard_response(response, message, maintain_history)
                
        except Exception as e:
            return self._handle_error(e, message)
    
    def _handle_standard_response(self, response, user_message: str, maintain_history: bool) -> Dict[str, Any]:
        """Maneja respuesta estándar (no streaming)"""
        try:
            # Extraer información de la respuesta
            assistant_message = response.choices[0].message.content
            usage = response.usage
            
            # Actualizar historial si es necesario
            if maintain_history:
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return {
                "success": True,
                "response": assistant_message,
                "usage": {
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "model": self.model,
                "reasoning_content": getattr(response.choices[0].message, 'reasoning_content', None)
            }
            
        except Exception as e:
            return self._handle_error(e, user_message)
    
    def _handle_stream_response(self, response, user_message: str, maintain_history: bool) -> Dict[str, Any]:
        """Maneja respuesta streaming"""
        try:
            full_response = ""
            reasoning_content = ""
            
            print("Respuesta (streaming):")
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    print(content, end="", flush=True)
                
                # Capturar reasoning content si está disponible
                if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                    reasoning_content += chunk.choices[0].delta.reasoning_content
            
            print("\n")  # Nueva línea al final
            
            # Actualizar historial si es necesario
            if maintain_history:
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": full_response})
            
            return {
                "success": True,
                "response": full_response,
                "reasoning_content": reasoning_content if reasoning_content else None,
                "model": self.model,
                "streamed": True
            }
            
        except Exception as e:
            return self._handle_error(e, user_message)
    
    def _handle_error(self, error, user_message: str) -> Dict[str, Any]:
        """Maneja diferentes tipos de errores de la API"""
        error_info = {
            "success": False,
            "error": str(error),
            "user_message": user_message
        }
        
        # Clasificar errores específicos
        if hasattr(error, 'status_code'):
            status_code = error.status_code
            error_info["status_code"] = status_code
            
            if status_code == 400:
                error_info["error_type"] = "Invalid Format"
                error_info["solution"] = "Verifica el formato de tu solicitud"
            elif status_code == 401:
                error_info["error_type"] = "Authentication Fails"
                error_info["solution"] = "Verifica tu API key"
            elif status_code == 402:
                error_info["error_type"] = "Insufficient Balance"
                error_info["solution"] = "Recarga tu cuenta"
            elif status_code == 422:
                error_info["error_type"] = "Invalid Parameters"
                error_info["solution"] = "Revisa los parámetros de tu solicitud"
            elif status_code == 429:
                error_info["error_type"] = "Rate Limit Reached"
                error_info["solution"] = "Reduce la frecuencia de tus solicitudes"
            elif status_code == 500:
                error_info["error_type"] = "Server Error"
                error_info["solution"] = "Reintenta después de un momento"
            elif status_code == 503:
                error_info["error_type"] = "Server Overloaded"
                error_info["solution"] = "El servidor está sobrecargado, reintenta más tarde"
        
        return error_info
    
    def clear_history(self):
        """Limpia el historial de conversación"""
        self.conversation_history = []
        print("Historial de conversación limpiado.")
    
    def get_history(self) -> List[Dict[str, str]]:
        """Obtiene el historial de conversación actual"""
        return self.conversation_history.copy()
    
    def save_conversation(self, filename: str):
        """Guarda la conversación en un archivo JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
            print(f"Conversación guardada en {filename}")
        except Exception as e:
            print(f"Error al guardar conversación: {e}")
    
    def load_conversation(self, filename: str):
        """Carga una conversación desde un archivo JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)
            print(f"Conversación cargada desde {filename}")
        except Exception as e:
            print(f"Error al cargar conversación: {e}")
