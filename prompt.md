# 🎨 Sistema de Prompts para Diseños HTML Premium

## 📋 **Template de Prompt Base**

```
Crea un contenido HTML premium sobre [TEMA] con las siguientes especificaciones:

### 🎯 FORMATO Y ESTRUCTURA:
- Dimensiones: 800x800px (formato cuadrado para Instagram)
- Layout: [Grid/Cards/Dashboard/Vertical/Minimalist]
- Tema visual: [Futurista/Elegante/Moderno/Dark/Light]
- Font: [Inter/Space Grotesk/Poppins/Roboto]

### 🎨 ESTILO VISUAL:
- Paleta de colores: [Azul tech/Verde natura/Púrpura premium/Gradientes]
- Background: [Gradiente/Radial/Linear/Solid]
- Elementos: [Glassmorphism/Neumorphism/Dark theme/Cards]
- Efectos: [Hover animations/Floating elements/Glow effects]

### ✨ ANIMACIONES REQUERIDAS:
- [Pulse/Rotate/Shine/Float/BorderGlow/Particles]
- Duración: [3s-8s] con ease-in-out
- Delays escalonados para múltiples elementos

### 📱 CONTENIDO ESPECÍFICO:
- Título principal: [TEMA]
- Definición central: [Explicación en 1-2 líneas]
- Características: [4 puntos clave en grid 2x2]
- Ejemplos prácticos: [5-6 ejemplos reales]
- Call to action o marca

### 🔧 REQUISITOS TÉCNICOS:
- CSS Grid/Flexbox responsive
- Hover states en todos los elementos interactivos
- Optimizado para móvil (media queries)
- Sin dependencias externas (solo Font Awesome)
- Elementos semánticamente correctos
```

## 🧠 **Proceso Mental que Sigo:**

### 1️⃣ **ANÁLISIS DEL TEMA:**
```
¿Qué es? → [LLM/RAG/ChatGPT/etc.]
¿Cómo se siente? → [Tecnológico/Educativo/Futurista]
¿Qué colores evoca? → [Azul=Tech, Verde=Datos, Púrpura=IA]
¿Qué íconos representan mejor? → [Brain/Search/Network/Database]
```

### 2️⃣ **DECISIONES DE DISEÑO:**
```
Layout Structure:
- Header (Logo + Título)
- Main Content (Definición destacada)
- Features Grid (2x2 o 1x4)
- Examples/Process (Horizontal flow)
- Footer (Branding)

Visual Hierarchy:
- Primary: Título y definición central
- Secondary: Características principales  
- Tertiary: Ejemplos y detalles
- Accent: Marca y decoraciones
```

### 3️⃣ **PALETA DE COLORES SISTEMÁTICA:**
```css
/* Esquema de colores por tema */
LLM/AI: 
- Primary: #3b82f6 (Azul inteligencia)
- Secondary: #8b5cf6 (Púrpura tech)
- Accent: #10b981 (Verde éxito)

RAG/Búsqueda:
- Primary: #10b981 (Verde datos)
- Secondary: #06b6d4 (Cyan búsqueda)  
- Accent: #f59e0b (Naranja resultado)

Futurista/Premium:
- Base: #0f0f0f (Negro profundo)
- Primary: #667eea (Azul eléctrico)
- Secondary: #764ba2 (Púrpura elegante)
- Accent: #f093fb (Rosa futurista)
```

### 4️⃣ **LIBRERÍA DE COMPONENTES:**
```css
/* Mis componentes reutilizables */

.glass-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.neon-glow {
    box-shadow: 0 0 40px rgba(primary-color, 0.5);
    animation: pulse 3s ease-in-out infinite;
}

.gradient-text {
    background: linear-gradient(135deg, #fff, #primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hover-lift {
    transition: transform 0.3s ease;
}
.hover-lift:hover {
    transform: translateY(-4px);
}
```

## 🚀 **Prompt Específico para RAG Dark:**

```
Crea un HTML premium sobre RAG con:

TEMA: Futurista dark tech dashboard
LAYOUT: Dashboard con cards grid 2x2
COLORES: Negro base + gradientes azul/púrpura eléctrico
FONT: Space Grotesk (tech/moderna)
EFECTOS: Borde animado + partículas flotantes + shine effects
CONTENIDO: 
- Logo circular con doble animación
- Definición en card destacado con shine
- 4 características en grid con hover effects
- Proceso RAG en 4 pasos horizontales
ANIMACIONES: BorderGlow (6s) + Pulse (3s) + Particles floating
RESPONSIVE: 95vmin en móvil manteniendo proporción
```

## 🎯 **Elementos Clave que Siempre Incluyo:**

### ✨ **Micro-interacciones:**
```css
/* Hover states suaves */
transition: all 0.3s ease;

/* Animaciones sutiles */
animation: gentle-animation 3s ease-in-out infinite;

/* Estados activos claros */
transform: translateY(-2px);
box-shadow: 0 8px 25px rgba(color, 0.2);
```

### 🎨 **Jerarquía Visual:**
```
1. ATTRACT: Logo animado + título gradiente
2. INFORM: Definición central destacada  
3. DETAIL: Características en cards organizadas
4. EXAMPLES: Lista horizontal de casos reales
5. BRAND: Footer discreto pero presente
```

### 📱 **Responsive Strategy:**
```css
/* Mobile-first approach */
@media (max-width: 640px) {
    /* Mantener proporciones cuadradas */
    width: 95vmin;
    height: 95vmin;
    
    /* Ajustar typography scale */
    font-size: calc(desktop-size * 0.8);
    
    /* Simplificar layouts */
    grid-template-columns: 1fr; /* Stack en móvil */
}
```

## 💡 **Tips para Generar Designs Premium:**
