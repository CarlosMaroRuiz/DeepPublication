# DeepSeekReseaoner - Documentación

## Descripción

`DeepSeekReseaoner` es una clase Python que proporciona una interfaz simplificada para interactuar con el modelo `deepseek-reasoner` de DeepSeek. Esta clase maneja la comunicación con la API, el historial de conversaciones, streaming de respuestas y manejo robusto de errores.

---

## 📚 Conceptos Fundamentales

### 🌡️ **Temperatura - Controlando la Creatividad**

La **temperatura** es un parámetro que controla qué tan "creativo" o "aleatorio" será el modelo en sus respuestas.

#### ¿Qué hace la temperatura?
- **Rango:** 0.0 a 2.0
- **Baja (0.0-0.5):** Respuestas más predecibles, consistentes y "seguras"
- **Media (0.8-1.3):** Balance entre creatividad y coherencia
- **Alta (1.5-2.0):** Respuestas más creativas, variadas e impredecibles

#### Ejemplos Prácticos:

```python
# Temperatura BAJA (0.0) - Para matemáticas
result = reasoner.chat("¿Cuánto es 2+2?", temperature=0.0)
# Siempre responderá: "4" (predecible y correcto)

# Temperatura ALTA (1.5) - Para creatividad  
result = reasoner.chat("Escribe un poema sobre gatos", temperature=1.5)
# Cada vez generará un poema completamente diferente
```

### 🎯 **Tokens - Las Unidades de Texto**

Un **token** es la unidad básica que el modelo entiende. No siempre equivale a una palabra.

#### ¿Qué cuenta como token?
- **Palabras comunes:** "casa" = 1 token
- **Palabras largas:** "extraordinario" = 2-3 tokens  
- **Puntuación:** "," "." "?" = 1 token cada uno
- **Números:** "123" = 1 token, "12345" = 2-3 tokens
- **Espacios:** También cuentan como tokens

#### Regla práctica:
```
📏 1 token ≈ 4 caracteres en español
📏 100 tokens ≈ 75-80 palabras
📏 1000 tokens ≈ 750 palabras (una página de texto)
```

#### Ejemplo de conteo:
```python
# Texto: "Hola, ¿cómo estás?"
# Tokens: ["Hola", ",", " ¿", "cómo", " est", "ás", "?"] = ~7 tokens

result = reasoner.chat("Pregunta corta", max_tokens=50)
# Limitará la respuesta a ~40 palabras
```

### 📡 **Streaming - Respuestas en Tiempo Real**

El **streaming** permite ver la respuesta del modelo mientras se genera, palabra por palabra.

#### Diferencias Visuales:

**Sin Streaming (stream=False):**
```
Usuario: "Explica qué es Python"
[Esperando...] ⏳
[Esperando...] ⏳  
[Esperando...] ⏳
Respuesta completa: "Python es un lenguaje de programación..."
```

**Con Streaming (stream=True):**
```
Usuario: "Explica qué es Python"  
Respuesta: "Python es un lenguaje de programación..."
          ↑ Aparece palabra por palabra
```

#### Cuándo usar cada uno:

| Situación | Recomendación | Razón |
|-----------|---------------|-------|
| Respuestas cortas (< 50 palabras) | `stream=False` | No hay ventaja notable |
| Explicaciones largas | `stream=True` | Mejor experiencia de usuario |
| Código/JSON/Datos estructurados | `stream=False` | Easier parsing |
| Conversaciones interactivas | `stream=True` | Sensación de conversación real |
| Procesamiento automático | `stream=False` | Más fácil de procesar |

---

## 📋 Guía de Casos de Uso

### 1. 🧮 **Coding / Math** (Temperature: 0.0)

**Cuándo usar:** Cuando necesitas respuestas exactas, precisas y consistentes.

**Características:**
- ✅ Respuestas determinísticas
- ✅ Cálculos exactos
- ✅ Código funcional
- ❌ Poca variación en respuestas

```python
# Ejemplo: Resolver problemas matemáticos
result = reasoner.chat(
    message="Resuelve la ecuación: 3x + 7 = 22",
    temperature=0.0,
    max_tokens=200
)

# Ejemplo: Generar código
result = reasoner.chat(
    message="Escribe una función Python para ordenar una lista",
    temperature=0.0,
    stream=False  # Para código es mejor sin streaming
)
```

**Por qué temperatura 0.0:**
- Los problemas matemáticos tienen UNA respuesta correcta
- El código debe ser sintácticamente correcto
- Necesitas consistencia entre ejecuciones

### 2. 📊 **Data Cleaning / Data Analysis** (Temperature: 1.0)

**Cuándo usar:** Para análisis de datos, limpieza y tareas que requieren metodología pero con cierta flexibilidad.

**Características:**
- ✅ Enfoque metodológico
- ✅ Algo de creatividad en soluciones
- ✅ Diferentes perspectivas de análisis
- ⚖️ Balance entre precisión y creatividad

```python
# Ejemplo: Análisis de datos
result = reasoner.chat(
    message="""
    Tengo estos datos de ventas [1200, 1400, 1100, 1600, 1300].
    ¿Qué insights puedes obtener y qué visualización recomendarías?
    """,
    temperature=1.0,
    stream=True  # Para ver el proceso de análisis
)

# Ejemplo: Limpieza de datos
result = reasoner.chat(
    message="¿Cómo limpio datos con valores nulos en pandas?",
    temperature=1.0,
    system_prompt="Eres un experto en ciencia de datos"
)
```

**Por qué temperatura 1.0:**
- Permite diferentes enfoques metodológicos
- Da flexibilidad para soluciones creativas
- Mantiene rigor científico

### 3. 💬 **General Conversation** (Temperature: 1.3)

**Cuándo usar:** Conversaciones casuales, explicaciones generales, consultas cotidianas.

**Características:**
- ✅ Respuestas naturales y variadas
- ✅ Tono conversacional
- ✅ Explicaciones adaptables
- ✅ Personalidad más evidente

```python
# Ejemplo: Conversación casual
result = reasoner.chat(
    message="¿Qué opinas sobre trabajar desde casa?",
    temperature=1.3,
    stream=True,  # Para conversación natural
    maintain_history=True  # Para mantener contexto
)

# Ejemplo: Explicaciones generales
result = reasoner.chat(
    message="Explícame qué es la inteligencia artificial como si tuviera 12 años",
    temperature=1.3,
    system_prompt="Eres un profesor paciente y didáctico"
)
```

**Por qué temperatura 1.3:**
- Las conversaciones humanas son naturalmente variadas
- Permite respuestas más "humanas" y menos robóticas
- Da espacio para personalidad y matices

### 4. 🌍 **Translation** (Temperature: 1.3)

**Cuándo usar:** Traducción de textos, localización, adaptación cultural.

**Características:**
- ✅ Traducciones naturales
- ✅ Adaptación cultural
- ✅ Diferentes estilos según contexto
- ✅ Manejo de expresiones idiomáticas

```python
# Ejemplo: Traducción básica
result = reasoner.chat(
    message="Traduce al inglés: 'Me da mucha lata hacer la tarea'",
    temperature=1.3,
    system_prompt="Traduce considerando el contexto cultural mexicano"
)

# Ejemplo: Traducción con contexto
result = reasoner.chat(
    message="""
    Traduce este email comercial al inglés, manteniendo un tono profesional:
    "Estimado cliente, esperamos que esté bien..."
    """,
    temperature=1.3,
    max_tokens=500
)
```

**Por qué temperatura 1.3:**
- Las traducciones pueden tener múltiples variantes correctas
- Permite adaptación cultural y de registro
- Da flexibilidad para expresiones idiomáticas

### 5. 🎨 **Creative Writing / Poetry** (Temperature: 1.5)

**Cuándo usar:** Escritura creativa, poemas, historias, contenido artístico.

**Características:**
- ✅ Máxima creatividad
- ✅ Respuestas únicas e impredecibles
- ✅ Estilo literario variado
- ⚠️ Puede ser inconsistente

```python
# Ejemplo: Escribir poesía
result = reasoner.chat(
    message="Escribe un poema sobre la soledad en la ciudad",
    temperature=1.5,
    stream=True,  # Para ver la creatividad surgir
    max_tokens=300
)

# Ejemplo: Crear una historia
result = reasoner.chat(
    message="""
    Escribe el inicio de una historia de ciencia ficción donde 
    los humanos descubren que las plantas pueden comunicarse
    """,
    temperature=1.5,
    system_prompt="Eres un escritor de ciencia ficción imaginativo"
)
```

**Por qué temperatura 1.5:**
- La creatividad requiere aleatoriedad e impredecibilidad
- Cada ejecución debe generar contenido único
- Permite explorar ideas no convencionales

---

## 🎯 Matriz de Decisión Rápida

| Necesito... | Temperature | Streaming | Max Tokens | Ejemplo |
|-------------|-------------|-----------|------------|---------|
| **Código exacto** | 0.0 | ❌ No | 500-1000 | `reasoner.chat("función fibonacci", temperature=0.0)` |
| **Cálculo matemático** | 0.0 | ❌ No | 200-500 | `reasoner.chat("derivada de x²", temperature=0.0)` |
| **Análisis de datos** | 1.0 | ✅ Sí | 800-1500 | `reasoner.chat("analiza estos datos", temperature=1.0, stream=True)` |
| **Explicación técnica** | 1.0 | ✅ Sí | 1000-2000 | `reasoner.chat("explica blockchain", temperature=1.0, stream=True)` |
| **Charla casual** | 1.3 | ✅ Sí | 500-1000 | `reasoner.chat("¿qué tal tu día?", temperature=1.3, stream=True)` |
| **Traducir texto** | 1.3 | ❌ No | 300-800 | `reasoner.chat("traduce: hello", temperature=1.3)` |
| **Escribir historia** | 1.5 | ✅ Sí | 1500-3000 | `reasoner.chat("escribe cuento", temperature=1.5, stream=True)` |
| **Poema creativo** | 1.5 | ✅ Sí | 200-500 | `reasoner.chat("poema sobre amor", temperature=1.5, stream=True)` |

## Instalación

### Dependencias Requeridas

```bash
pip install openai tabulate
```

### Estructura de Archivos

```
proyecto/
├── config.py              # Configuración con API key
├── deepseek_reasoner.py    # Clase principal
└── main.py                 # Archivo de uso
```

### Configuración

Crea un archivo `config.py` con tu API key:

```python
# config.py
class Config:
    api_key = "tu_api_key_de_deepseek"

config = Config()
```

## Clase DeepSeekReseaoner

### Constructor

```python
DeepSeekReseaoner()
```

**Inicializa la clase con:**
- Cliente OpenAI configurado para DeepSeek API
- Modelo `deepseek-reasoner`
- Historial de conversación vacío

---

## Métodos Principales

### 1. `get_information_temperature()` (Método Estático)

Muestra una tabla con temperaturas recomendadas para diferentes casos de uso.

```python
DeepSeekReseaoner.get_information_temperature()
```

**Salida:**
```
┌─────────────────────────────────┬─────────────┐
│ UseCase                         │ Temperature │
├─────────────────────────────────┼─────────────┤
│ Coding / Math                   │         0.0 │
│ Data Cleaning / Data Analysis   │         1.0 │
│ General Conversation            │         1.3 │
│ Translation                     │         1.3 │
│ Creative Writing / Poetry       │         1.5 │
└─────────────────────────────────┴─────────────┘
```

### 2. `chat()` - Método Principal

Envía mensajes al modelo y maneja las respuestas.

```python
chat(
    message: str, 
    temperature: float = 1.0,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
    stream: bool = False,
    maintain_history: bool = True
) -> Dict[str, Any]
```

#### Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `message` | `str` | - | **Requerido.** El mensaje del usuario |
| `temperature` | `float` | `1.0` | Controla aleatoriedad (0.0-2.0) |
| `max_tokens` | `int` | `None` | Máximo tokens de salida |
| `system_prompt` | `str` | `None` | Prompt del sistema |
| `stream` | `bool` | `False` | Habilita streaming |
| `maintain_history` | `bool` | `True` | Mantiene historial |

#### Valor de Retorno

**En caso exitoso:**
```python
{
    "success": True,
    "response": "Respuesta del modelo",
    "usage": {
        "input_tokens": 100,
        "output_tokens": 150,
        "total_tokens": 250
    },
    "model": "deepseek-reasoner",
    "reasoning_content": "Contenido de razonamiento",  # Solo si disponible
    "streamed": True  # Solo en modo streaming
}
```

**En caso de error:**
```python
{
    "success": False,
    "error": "Descripción del error",
    "error_type": "Tipo de error",
    "solution": "Solución sugerida",
    "status_code": 400,  # Si disponible
    "user_message": "Mensaje original"
}
```

---

## Métodos de Historial

### 3. `clear_history()`

Limpia el historial de conversación.

```python
reasoner.clear_history()
# Output: "Historial de conversación limpiado."
```

### 4. `get_history()`

Obtiene una copia del historial actual.

```python
history = reasoner.get_history()
# Returns: List[Dict[str, str]]
```

### 5. `save_conversation(filename: str)`

Guarda el historial en un archivo JSON.

```python
reasoner.save_conversation("mi_conversacion.json")
# Output: "Conversación guardada en mi_conversacion.json"
```

### 6. `load_conversation(filename: str)`

Carga un historial desde archivo JSON.

```python
reasoner.load_conversation("mi_conversacion.json")
# Output: "Conversación cargada desde mi_conversacion.json"
```

---

## Manejo de Errores

La clase maneja automáticamente los siguientes errores de la API DeepSeek:

| Código | Tipo de Error | Solución |
|--------|---------------|----------|
| 400 | Invalid Format | Verifica el formato de tu solicitud |
| 401 | Authentication Fails | Verifica tu API key |
| 402 | Insufficient Balance | Recarga tu cuenta |
| 422 | Invalid Parameters | Revisa los parámetros de tu solicitud |
| 429 | Rate Limit Reached | Reduce la frecuencia de solicitudes |
| 500 | Server Error | Reintenta después de un momento |
| 503 | Server Overloaded | El servidor está sobrecargado |

---

## Ejemplos de Uso

### Uso Básico

```python
from deepseek_reasoner import DeepSeekReseaoner

# Crear instancia
reasoner = DeepSeekReseaoner()

# Mostrar temperaturas recomendadas
DeepSeekReseaoner.get_information_temperature()

# Chat básico
result = reasoner.chat("¿Qué es Python?")
if result["success"]:
    print(result["response"])
else:
    print(f"Error: {result['error']}")
```

### Uso con Parámetros Específicos

```python
# Para matemáticas (temperatura baja)
result = reasoner.chat(
    message="Resuelve: 2x + 5 = 15",
    temperature=0.0,
    max_tokens=500
)

# Para creatividad (temperatura alta)
result = reasoner.chat(
    message="Escribe un poema sobre el mar",
    temperature=1.5,
    system_prompt="Eres un poeta romántico del siglo XIX"
)
```

### Streaming en Tiempo Real

```python
# Ver respuesta generándose palabra por palabra
result = reasoner.chat(
    message="Explica cómo funciona una red neuronal",
    stream=True,
    temperature=1.0
)

# El texto aparece en tiempo real
# Al final tienes la respuesta completa en result["response"]
```

### Conversación Continua

```python
# Primera pregunta
result1 = reasoner.chat("Hola, ¿puedes ayudarme con Python?")

# Segunda pregunta (mantiene contexto)
result2 = reasoner.chat("Específicamente con listas")

# Ver historial
history = reasoner.get_history()
print(f"Mensajes en historial: {len(history)}")

# Guardar conversación
reasoner.save_conversation("sesion_python.json")
```

### Manejo de Errores

```python
result = reasoner.chat("Pregunta muy compleja", max_tokens=100000)

if not result["success"]:
    print(f"Tipo de error: {result.get('error_type', 'Unknown')}")
    print(f"Mensaje: {result['error']}")
    if 'solution' in result:
        print(f"Solución: {result['solution']}")
```

### Caso de Uso Completo

```python
def chatbot_session():
    reasoner = DeepSeekReseaoner()
    
    print("🤖 Chatbot DeepSeek iniciado (escribe 'salir' para terminar)")
    
    while True:
        user_input = input("\n💬 Tú: ")
        
        if user_input.lower() in ['salir', 'exit', 'quit']:
            break
            
        # Determinar temperatura según el tipo de pregunta
        if any(word in user_input.lower() for word in ['matemática', 'código', 'programar']):
            temp = 0.0
        elif any(word in user_input.lower() for word in ['historia', 'poema', 'creativo']):
            temp = 1.5
        else:
            temp = 1.3
            
        result = reasoner.chat(
            message=user_input,
            temperature=temp,
            stream=True  # Respuesta en tiempo real
        )
        
        if not result["success"]:
            print(f"❌ Error: {result['error']}")
    
    # Guardar sesión al finalizar
    reasoner.save_conversation(f"sesion_{int(time.time())}.json")
    print("👋 Sesión guardada. ¡Hasta luego!")

if __name__ == "__main__":
    chatbot_session()
```

---

## Notas Importantes

### Costos y Tokens

- El modelo `deepseek-reasoner` incluye tokens de razonamiento (CoT) en el conteo
- Revisa los precios en la documentación oficial de DeepSeek
- Usa `max_tokens` para controlar costos

### Límites

- Contexto máximo: 64K tokens
- Output máximo por defecto: 32K tokens
- Sin límites estrictos de rate limit

### Mejores Prácticas

1. **Usa temperaturas apropiadas** según el caso de uso
2. **Habilita streaming** para respuestas largas
3. **Maneja errores** siempre verificando `result["success"]`
4. **Guarda conversaciones importantes** con `save_conversation()`
5. **Limpia historial** cuando cambies de tema con `clear_history()`

---

## Licencia

Esta clase es de uso libre. Asegúrate de cumplir con los términos de servicio de DeepSeek API.