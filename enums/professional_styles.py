

PROFESSIONAL_COLOR_PALETTES = {
    # Paletas corporativas premium
    "Azul profesional": {
        "primary": "#1E40AF",
        "secondary": "#3B82F6", 
        "accent": "#60A5FA",
        "background": "#F8FAFC",
        "surface": "#FFFFFF",
        "text_primary": "#1E293B",
        "text_secondary": "#64748B",
        "gradient": "linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)",
        "description": "Confianza corporativa, estabilidad financiera",
        "best_for": ["finance", "corporate", "tech", "consulting"]
    },
    
    "Verde tech": {
        "primary": "#059669",
        "secondary": "#10B981",
        "accent": "#34D399",
        "background": "#F0FDF4",
        "surface": "#FFFFFF",
        "text_primary": "#064E3B",
        "text_secondary": "#047857", 
        "gradient": "linear-gradient(135deg, #059669 0%, #10B981 100%)",
        "description": "Innovación sostenible, crecimiento tecnológico",
        "best_for": ["startups", "sustainability", "health", "environment"]
    },
    
    "Púrpura moderno": {
        "primary": "#7C3AED",
        "secondary": "#A855F7",
        "accent": "#C084FC",
        "background": "#FAF5FF",
        "surface": "#FFFFFF",
        "text_primary": "#581C87",
        "text_secondary": "#7C3AED",
        "gradient": "linear-gradient(135deg, #7C3AED 0%, #A855F7 100%)",
        "description": "Creatividad premium, innovación digital",
        "best_for": ["design", "creative", "marketing", "entertainment"]
    },
    
    "Naranja energético": {
        "primary": "#EA580C",
        "secondary": "#FB923C",
        "accent": "#FDBA74",
        "background": "#FFF7ED",
        "surface": "#FFFFFF",
        "text_primary": "#9A3412",
        "text_secondary": "#EA580C",
        "gradient": "linear-gradient(135deg, #EA580C 0%, #FB923C 100%)",
        "description": "Energía positiva, dinamismo empresarial",
        "best_for": ["fitness", "motivation", "sales", "energy"]
    },
    
    "Gradiente sunset": {
        "primary": "#EC4899",
        "secondary": "#F59E0B",
        "accent": "#EF4444",
        "background": "linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)",
        "surface": "#FFFFFF",
        "text_primary": "#92400E",
        "text_secondary": "#BE185D",
        "gradient": "linear-gradient(135deg, #EC4899 0%, #F59E0B 50%, #EF4444 100%)",
        "description": "Calidez premium, experiencia única",
        "best_for": ["lifestyle", "hospitality", "personal_brand", "luxury"]
    },
    
    "Monocromático": {
        "primary": "#111827",
        "secondary": "#374151",
        "accent": "#6B7280",
        "background": "#F9FAFB",
        "surface": "#FFFFFF",
        "text_primary": "#111827",
        "text_secondary": "#4B5563",
        "gradient": "linear-gradient(135deg, #111827 0%, #374151 100%)",
        "description": "Elegancia atemporal, sofisticación",
        "best_for": ["architecture", "law", "premium_services", "editorial"]
    }
}

PROFESSIONAL_DESIGN_STYLES = {
    "Minimalista": {
        "font_primary": "Inter",
        "font_secondary": "system-ui",
        "spacing": "generous",
        "borders": "none",
        "shadows": "subtle",
        "animation": "minimal",
        "layout": "centered_clean",
        "description": "Inspirado en Apple - minimalismo extremo",
        "characteristics": ["clean", "spacious", "typography_focused"]
    },
    
    "Moderno": {
        "font_primary": "Inter",
        "font_secondary": "SF Pro Display",
        "spacing": "balanced",
        "borders": "rounded_subtle",
        "shadows": "layered_depth",
        "animation": "purposeful",
        "layout": "asymmetric_balance",
        "description": "Como Stripe - profesional pero amigable",
        "characteristics": ["professional", "trustworthy", "modern"]
    },
    
    "Profesional": {
        "font_primary": "system-ui",
        "font_secondary": "Arial",
        "spacing": "corporate_standard",
        "borders": "professional_subtle",
        "shadows": "conservative",
        "animation": "subtle_professional",
        "layout": "traditional_grid",
        "description": "Corporativo confiable - para executives",
        "characteristics": ["corporate", "reliable", "traditional"]
    },
    
    "Colorido": {
        "font_primary": "Poppins",
        "font_secondary": "Inter",
        "spacing": "dynamic", 
        "borders": "rounded_large",
        "shadows": "dramatic",
        "animation": "creative_motion",
        "layout": "experimental",
        "description": "Creatividad visual - para impactar",
        "characteristics": ["bold", "experimental", "artistic"]
    },
    
    "Gradientes": {
        "font_primary": "Inter",
        "font_secondary": "system-ui",
        "spacing": "flowing",
        "borders": "organic_rounded",
        "shadows": "gradient_glow",
        "animation": "smooth_flowing",
        "layout": "fluid_organic",
        "description": "Transiciones suaves - para experiencias premium",
        "characteristics": ["smooth", "premium", "flowing"]
    },
    
    "Oscuro": {
        "font_primary": "Inter",
        "font_secondary": "Roboto",
        "spacing": "dramatic",
        "borders": "sharp_contrast",
        "shadows": "deep_dramatic",
        "animation": "bold_transitions",
        "layout": "high_contrast",
        "description": "Modo oscuro premium - para tech",
        "characteristics": ["dramatic", "tech", "premium"]
    },
    
    "Neón": {
        "font_primary": "Inter",
        "font_secondary": "system-ui",
        "spacing": "futuristic_minimal",
        "borders": "sharp_geometric",
        "shadows": "neon_glow",
        "animation": "tech_motion", 
        "layout": "asymmetric_tech",
        "description": "Futurista tech - para innovación",
        "characteristics": ["futuristic", "tech", "innovative"]
    },
    
    "Elegante": {
        "font_primary": "Playfair Display",
        "font_secondary": "Inter",
        "spacing": "luxury_spacious",
        "borders": "refined_subtle",
        "shadows": "elegant_soft",
        "animation": "graceful",
        "layout": "sophisticated_grid",
        "description": "Lujo sofisticado - para marcas premium",
        "characteristics": ["luxury", "sophisticated", "refined"]
    }
}

def get_style_recommendations(content_type, industry, platform):
    """
    Recomienda estilos basándose en el contexto
    """
    recommendations = {
        "color_palette": None,
        "design_style": None,
        "typography": None,
        "layout": None,
        "confidence": 0.0
    }
    
    # Lógica de recomendación basada en industria
    industry_palette_map = {
        "tech": ["Verde tech", "Púrpura moderno", "Monocromático"],
        "finance": ["Azul profesional", "Monocromático", "Verde tech"],
        "creative": ["Púrpura moderno", "Gradiente sunset", "Colorido"],
        "healthcare": ["Verde tech", "Azul profesional", "Minimalista"],
        "marketing": ["Púrpura moderno", "Gradiente sunset", "Naranja energético"],
        "business": ["Azul profesional", "Monocromático", "Profesional"]
    }
    
    # Mapeo de tipo de contenido a estilo
    content_style_map = {
        "quote": ["Elegante", "Minimalista"],
        "tip": ["Moderno", "Profesional"], 
        "estadistica": ["Profesional", "Moderno"],
        "concepto": ["Minimalista", "Moderno"],
        "lista": ["Profesional", "Colorido"]
    }
    
    # Hacer recomendaciones
    if industry.lower() in industry_palette_map:
        recommendations["color_palette"] = industry_palette_map[industry.lower()][0]
        recommendations["confidence"] += 0.3
    
    if content_type in content_style_map:
        recommendations["design_style"] = content_style_map[content_type][0]
        recommendations["confidence"] += 0.2
        
    # Ajustes por plataforma
    if platform == "linkedin_post":
        recommendations["design_style"] = "Profesional"
        recommendations["color_palette"] = "Azul profesional"
        recommendations["confidence"] += 0.3
    elif platform == "instagram_square":
        recommendations["design_style"] = "Colorido"
        recommendations["confidence"] += 0.2
    elif platform == "instagram_story":
        recommendations["design_style"] = "Moderno"
        recommendations["confidence"] += 0.2
    
    return recommendations