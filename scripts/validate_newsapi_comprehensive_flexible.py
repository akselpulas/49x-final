"""
Comprehensive validation of NewsAPI articles with flexible criteria.
Validates articles that have BOTH CE and AI keywords.
Uses LLM to check if keywords are used in relevant contexts.
Includes sub-disciplines and assigns confidence scores.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from openai import OpenAI

# Add project root to path
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Input/Output files
INPUT_CSV = PROJECT_ROOT / "data" / "NewsAPI articles son.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "newsapi_validation_comprehensive.csv"

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=OPENAI_API_KEY)

# Rate limiting
LLM_DELAY = 0.3

# Civil Engineering Areas with sub-disciplines
CE_AREAS = {
    "Structural": [
        "analysis", "design", "health monitoring", "materials", "buildings", "bridges", 
        "structures", "concrete", "steel", "structural engineering", "structural analysis",
        "structural design", "structural health", "structural materials", "reinforcement"
    ],
    "Geotechnical": [
        "soil", "foundations", "tunnels", "excavation", "ground engineering", "underground",
        "geotechnical engineering", "soil mechanics", "foundation design", "tunnel construction",
        "slope stability", "retaining walls", "earthworks"
    ],
    "Transportation": [
        "traffic", "roads", "autonomous vehicles", "logistics", "transportation systems",
        "railways", "airports", "ports", "mobility", "highways", "public transit",
        "transportation infrastructure", "traffic management", "fleet management",
        "transportation planning", "road safety", "vehicle automation"
    ],
    "Construction Management": [
        "scheduling", "safety", "cost estimation", "site monitoring", "project management",
        "construction projects", "building", "infrastructure development", "construction sites",
        "construction industry", "construction planning", "construction safety",
        "construction costs", "construction scheduling", "data centers", "facilities",
        "construction equipment", "construction materials", "construction technology"
    ],
    "Environmental Engineering": [
        "sustainability", "waste management", "green building", "renewable energy",
        "water", "energy infrastructure", "climate", "environmental impact",
        "environmental protection", "clean energy", "solar power", "wind power",
        "energy efficiency", "carbon emissions", "environmental sustainability",
        "water management", "wastewater", "environmental monitoring"
    ]
}

# AI Technologies with sub-disciplines
AI_TECHNOLOGIES = {
    "Computer Vision": [
        "image recognition", "drone inspection", "safety monitoring", "visual inspection",
        "cameras", "sensors", "image processing", "computer vision", "visual analysis",
        "image analysis", "video analysis", "object detection", "pattern recognition"
    ],
    "Predictive Analytics": [
        "risk assessment", "maintenance prediction", "forecasting", "machine learning",
        "data analytics", "prediction", "predictive modeling", "predictive maintenance",
        "risk analysis", "data analysis", "analytics", "predictive models",
        "forecasting models", "statistical analysis"
    ],
    "Generative Design": [
        "optimization", "parametric modeling", "algorithmic design", "design optimization",
        "automated design", "generative design", "design automation", "optimization algorithms",
        "parametric design", "computational design", "design generation"
    ],
    "Robotics/Automation": [
        "brick-laying robots", "autonomous machinery", "robots", "automation",
        "autonomous systems", "robotic systems", "automated construction", "robotics",
        "autonomous vehicles", "automated processes", "robotic automation",
        "autonomous equipment", "automated machinery", "robotic technology"
    ]
}


def validate_with_llm(title: str, description: str, ce_keywords: str, ai_keywords: str) -> Dict:
    """
    Use LLM to validate if article is relevant to CE and AI intersection.
    Returns validation result with confidence scores.
    """
    full_text = f"Title: {title}\n\nDescription: {description}"
    
    # Build comprehensive prompt
    ce_areas_list = "\n".join([f"- {area}: {', '.join(keywords[:5])}" for area, keywords in CE_AREAS.items()])
    ai_techs_list = "\n".join([f"- {tech}: {', '.join(keywords[:5])}" for tech, keywords in AI_TECHNOLOGIES.items()])
    
    prompt = f"""Analyze the following article. It has been flagged with CE keywords: "{ce_keywords}" and AI keywords: "{ai_keywords}".

Article:
{full_text}

Civil Engineering Areas (be flexible and inclusive):
{ce_areas_list}

AI Technologies (be flexible and inclusive):
{ai_techs_list}

IMPORTANT CRITERIA:
1. The article MUST relate to BOTH Civil Engineering AND AI technologies.
2. Be flexible - if keywords appear in relevant contexts (even indirectly), consider it valid.
3. Examples of valid intersections:
   - AI used in construction projects (construction management + AI)
   - AI for infrastructure monitoring (any CE area + computer vision/predictive analytics)
   - Autonomous vehicles in transportation (transportation + robotics/automation)
   - AI for structural analysis (structural + predictive analytics/generative design)
   - AI for environmental monitoring (environmental engineering + computer vision/predictive analytics)
   - Data centers (construction management + AI infrastructure)
   - Energy infrastructure with AI (environmental engineering + AI)
   - Smart cities/infrastructure (any CE area + AI technologies)

4. If the article mentions infrastructure, construction, building, transportation, energy, or any physical project AND mentions AI, machine learning, automation, or related technologies, it's likely valid.

Respond with a JSON object containing:
- "is_valid": boolean (true if article relates to both CE and AI)
- "ce_areas": array of applicable CE area names (can be multiple)
- "ai_technologies": array of applicable AI technology names (can be multiple)
- "ce_confidence": 0.0-1.0 (confidence that article relates to CE)
- "ai_confidence": 0.0-1.0 (confidence that article relates to AI)
- "overall_confidence": 0.0-1.0 (overall confidence in validation)
- "reason": brief explanation

Respond ONLY with valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in Civil Engineering and AI. Be flexible and inclusive when validating articles. If an article mentions infrastructure, construction, building, transportation, energy, or physical projects AND mentions AI, machine learning, automation, or related technologies, it's likely valid. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=400
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Try to parse JSON
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()
        
        result = json.loads(result_text)
        
        return {
            'is_valid': bool(result.get('is_valid', False)),
            'ce_areas': result.get('ce_areas', []),
            'ai_technologies': result.get('ai_technologies', []),
            'ce_confidence': float(result.get('ce_confidence', 0.5)),
            'ai_confidence': float(result.get('ai_confidence', 0.5)),
            'overall_confidence': float(result.get('overall_confidence', 0.5)),
            'reason': result.get('reason', 'No reason provided')
        }
        
    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON parse error: {e}")
        return {
            'is_valid': False,
            'ce_areas': [],
            'ai_technologies': [],
            'ce_confidence': 0.0,
            'ai_confidence': 0.0,
            'overall_confidence': 0.0,
            'reason': f'JSON parse error: {str(e)}'
        }
    except Exception as e:
        print(f"    ⚠️  API error: {e}")
        return {
            'is_valid': False,
            'ce_areas': [],
            'ai_technologies': [],
            'ce_confidence': 0.0,
            'ai_confidence': 0.0,
            'overall_confidence': 0.0,
            'reason': f'API error: {str(e)}'
        }


def main():
    print("=" * 70)
    print("COMPREHENSIVE NEWSAPI VALIDATION (CE + AI INTERSECTION)")
    print("=" * 70)
    
    if not INPUT_CSV.exists():
        print(f"❌ Error: Input CSV not found: {INPUT_CSV}")
        return
    
    print(f"Reading articles from {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    print(f"Total articles: {len(df)}\n")
    
    # Filter articles that have BOTH CE and AI keywords
    df['has_ce'] = df['ce_keywords_found'].notna() & (df['ce_keywords_found'].astype(str).str.strip() != '')
    df['has_ai'] = df['ai_keywords_found'].notna() & (df['ai_keywords_found'].astype(str).str.strip() != '')
    df['has_both'] = df['has_ce'] & df['has_ai']
    
    print(f"Articles with CE keywords: {df['has_ce'].sum()}")
    print(f"Articles with AI keywords: {df['has_ai'].sum()}")
    print(f"Articles with BOTH CE and AI keywords: {df['has_both'].sum()}\n")
    
    # Process articles with both keywords
    articles_to_validate = df[df['has_both']].copy()
    print(f"Validating {len(articles_to_validate)} articles with LLM...\n")
    
    results = []
    valid_count = 0
    
    for idx, row in articles_to_validate.iterrows():
        title = str(row.get('title', ''))
        description = str(row.get('description', ''))
        ce_keywords = str(row.get('ce_keywords_found', ''))
        ai_keywords = str(row.get('ai_keywords_found', ''))
        
        print(f"[{len(results)+1}/{len(articles_to_validate)}] Validating: {title[:60]}...")
        
        validation = validate_with_llm(title, description, ce_keywords, ai_keywords)
        
        result_row = {
            'title': title,
            'description': description,
            'url': row.get('url', ''),
            'source': row.get('source', ''),
            'publication_date': row.get('publication_date', ''),
            'ce_keywords_found': ce_keywords,
            'ai_keywords_found': ai_keywords,
            'is_valid': validation['is_valid'],
            'ce_areas': ', '.join(validation['ce_areas']) if validation['ce_areas'] else '',
            'ai_technologies': ', '.join(validation['ai_technologies']) if validation['ai_technologies'] else '',
            'ce_confidence': validation['ce_confidence'],
            'ai_confidence': validation['ai_confidence'],
            'overall_confidence': validation['overall_confidence'],
            'reason': validation['reason']
        }
        
        results.append(result_row)
        
        if validation['is_valid']:
            valid_count += 1
            print(f"    ✓ VALID (CE: {validation['ce_confidence']:.2f}, AI: {validation['ai_confidence']:.2f}, Overall: {validation['overall_confidence']:.2f})")
            print(f"       CE Areas: {', '.join(validation['ce_areas']) if validation['ce_areas'] else 'None'}")
            print(f"       AI Techs: {', '.join(validation['ai_technologies']) if validation['ai_technologies'] else 'None'}")
        else:
            print(f"    ✗ NOT VALID (Overall: {validation['overall_confidence']:.2f}) - {validation['reason'][:60]}...")
        
        time.sleep(LLM_DELAY)
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Save results
    results_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    print(f"Total articles with both CE and AI keywords: {len(articles_to_validate)}")
    print(f"Valid articles (CE + AI intersection): {valid_count} ({valid_count/len(articles_to_validate)*100:.1f}%)")
    print(f"Invalid articles: {len(articles_to_validate) - valid_count}")
    print(f"\nAverage CE confidence: {results_df['ce_confidence'].mean():.2f}")
    print(f"Average AI confidence: {results_df['ai_confidence'].mean():.2f}")
    print(f"Average overall confidence: {results_df['overall_confidence'].mean():.2f}")
    print(f"\nResults saved to: {OUTPUT_CSV}")
    print("=" * 70)


if __name__ == "__main__":
    main()

