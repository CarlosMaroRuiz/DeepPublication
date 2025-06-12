# Esta clase prompt es usado para generar ideas

class Prompt_Gen_Idea:
    def __init__(self):
        self.system_promt = "Eres un experto en marketing de contenidos y redes sociales. Genera ideas virales y engageantes."
        self.prompt = """Genera 3 ideas creativas y específicas para posts de redes sociales profesionales. 

Incluye para cada idea:
- Tipo de contenido (tip, quote, estadística, lista, hecho curioso, tutorial, concepto técnico)
- Tema/nicho específico
- Título o concepto exacto
- Por qué sería viral o interesante

Para conceptos técnicos, incluye ejemplos como: API REST, Machine Learning, SOLID, Microservicios, etc.

Enfócate en temas actuales y relevantes como IA, programación, marketing digital, productividad, etc.

Responde en formato simple y directo."""

prompt_gen_idea = Prompt_Gen_Idea()
     