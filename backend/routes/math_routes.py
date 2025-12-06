"""
Routes pour la génération d'exercices mathématiques
Architecture hybride : Python pour calculs, IA pour rédaction
"""
from fastapi import APIRouter, HTTPException
from typing import List
import logging

# Import depuis models
from models.math_models import (
    MathExerciseSpec, 
    MathExerciseType,
    GeneratedMathExercise
)

# Import depuis services
from services.math_generation_service import MathGenerationService
from services.math_text_service import MathTextService

# Import depuis geometry renderer
# from geometry_svg_renderer import render_svg_schema  # TODO: À implémenter si nécessaire

# Logger
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/math", tags=["mathematics"])


async def generate_math_exercises_new_architecture(
    niveau: str, 
    chapitre: str, 
    difficulte: str, 
    nb_exercices: int
) -> List[dict]:
    """
    Nouvelle architecture pour génération d'exercices mathématiques
    
    Pipeline en 3 étapes :
    1. Génération specs mathématiques (Python pur, pas d'IA)
    2. Génération textes IA (rédaction uniquement)
    3. Conversion vers format Exercise
    
    Args:
        niveau: Niveau scolaire (6e, 5e, 4e, 3e)
        chapitre: Chapitre du programme
        difficulte: Niveau de difficulté
        nb_exercices: Nombre d'exercices à générer
        
    Returns:
        Liste de dictionnaires Exercise compatibles avec le système existant
    """
    logger.info(
        f"🎯 NOUVELLE ARCHITECTURE MATH - Démarrage: {niveau} - {chapitre} - {nb_exercices}ex"
    )
    
    try:
        # ÉTAPE 1: Génération des specs mathématiques (Python pur)
        logger.info("📊 ÉTAPE 1/3: Génération specs mathématiques")
        math_service = MathGenerationService()
        specs = math_service.generate_math_exercise_specs(
            niveau=niveau,
            chapitre=chapitre,
            difficulte=difficulte,
            nb_exercices=nb_exercices
        )
        
        if not specs:
            logger.warning("⚠️ Aucune spec générée, fallback vers ancien système")
            return []
        
        logger.info(f"✅ {len(specs)} specs mathématiques générées")
        
        # ÉTAPE 2: Génération des textes IA (rédaction uniquement)
        logger.info("✍️ ÉTAPE 2/3: Génération textes IA")
        text_service = MathTextService()
        generated_exercises = await text_service.generate_text_for_specs(specs)
        
        logger.info(f"✅ {len(generated_exercises)} exercices avec texte générés")
        
        # ÉTAPE 3: Conversion vers le format Exercise
        logger.info("🔄 ÉTAPE 3/3: Conversion vers format Exercise")
        exercises = []
        
        for gen_ex in generated_exercises:
            exercise_dict = gen_ex.to_exercise_dict()
            
            # Enrichir avec geometric_schema SVG si nécessaire
            # TODO: Implémenter le rendu SVG si nécessaire
            # if gen_ex.spec.figure_geometrique:
            #     try:
            #         svg_data = render_svg_schema(gen_ex.spec.figure_geometrique)
            #         exercise_dict["geometric_schema_svg"] = svg_data
            #     except Exception as e:
            #         logger.warning(f"SVG rendering failed: {e}")
            
            exercises.append(exercise_dict)
        
        logger.info(f"✅ {len(exercises)} exercices prêts")
        logger.info("🎉 NOUVELLE ARCHITECTURE - Génération réussie")
        
        return exercises
        
    except Exception as e:
        logger.error(f"❌ Erreur nouvelle architecture: {e}", exc_info=True)
        return []


@router.get("/health")
async def math_health():
    """Health check pour les routes mathématiques"""
    return {
        "status": "ok",
        "service": "math_generation",
        "architecture": "hybrid_python_ai"
    }
