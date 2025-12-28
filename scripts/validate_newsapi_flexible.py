"""
Validate NewsAPI articles with flexible criteria - both AI and CE keywords required.
Includes sub-disciplines for maximum valid articles.
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
OUTPUT_CSV = PROJECT_ROOT / "data" / "newsapi_validation_flexible.csv"

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=OPENAI_API_KEY)

# Rate limiting
LLM_DELAY = 0.3

# Civil Engineering Areas with expanded sub-disciplines
CE_AREAS = {
    "Structural": [
        "analysis", "design", "health monitoring", "materials", "buildings", "bridges", 
        "structures", "concrete", "steel", "structural engineering", "structural analysis",
        "structural design", "building design", "bridge design", "structural materials"
    ],
    "Geotechnical": [
        "soil", "foundations", "tunnels", "excavation", "ground engineering", "underground",
        "geotechnical engineering", "foundation design", "tunnel construction", "soil mechanics"
    ],
    "Transportation": [
        "traffic", "roads", "autonomous vehicles", "logistics", "transportation systems",
        "railways", "airports", "ports", "mobility", "transportation infrastructure",
        "road construction", "traffic management", "public transit", "transportation planning"
    ],
    "Construction Management": [
        "scheduling", "safety", "cost estimation", "site monitoring", "project management",
        "construction projects", "building", "infrastructure development", "data centers",
        "construction industry", "construction sites", "construction planning", "infrastructure projects",
        "facility construction", "construction technology", "construction sector"
    ],
    "Environmental Engineering": [
        "sustainability", "waste management", "green building", "renewable energy",
        "water", "energy infrastructure", "climate", "environmental impact",
        "sustainable construction", "green infrastructure", "energy efficiency", "water management",
        "environmental sustainability", "clean energy", "energy systems"
    ]
}

# AI Technologies with expanded sub-disciplines
AI_TECHNOLOGIES = {
    "Computer Vision": [
        "image recognition", "drone inspection", "safety monitoring", "visual inspection",
        "cameras", "sensors", "image processing", "computer vision", "visual analysis",
        "image analysis", "visual monitoring", "optical recognition"
    ],
    "Predictive Analytics": [
        "risk assessment", "maintenance prediction", "forecasting", "machine learning",
        "data analytics", "prediction", "modeling", "predictive analytics", "data analysis",
        "predictive modeling", "analytics", "data science", "predictive maintenance"
    ],
    "Generative Design": [
        "optimization", "parametric modeling", "algorithmic design", "design optimization",
        "automated design", "ai design", "generative design", "design automation",
        "optimization algorithms", "parametric design"
    ],
    "Robotics/Automation": [
        "robots", "automation", "autonomous machinery", "drones", "automated construction",
        "autonomous systems", "robotic", "robotics", "automated systems", "autonomous vehicles",
        "robotic systems", "automation technology", "autonomous equipment"
    ]
}


def validate_with_llm(title: str, description: str, ai_keywords: str, ce_keywords: str) -> Dict:
    """
    Use LLM to validate if article is relevant to both CE and AI with flexible criteria.
    """
    full_text = f"Title: {title}\n\nDescription: {description}\n\nAI Keywords Found: {ai_keywords}\n\nCE Keywords Found: {ce_keywords}"
    
    prompt = f"""Analyze the following article. Determine if it is relevant to BOTH Civil Engineering AND AI technologies.

Article:
{full_text}

Civil Engineering Areas (be flexible and inclusive):
- Structural: Analysis, design, health monitoring, materials, buildings, bridges, structures, concrete, steel, structural engineering
- Geotechnical: Soil, foundations, tunnels, excavation, ground engineering, underground construction
- Transportation: Traffic, roads, autonomous vehicles, logistics, transportation systems, railways, airports, ports, mobility, transportation infrastructure
- Construction Management: Scheduling, safety, cost estimation, site monitoring, project management, construction projects, building, infrastructure development, data centers, construction industry, infrastructure projects
- Environmental Engineering: Sustainability, waste management, green building, renewable energy, water, energy infrastructure, climate, environmental impact, sustainable construction

AI Technologies (be flexible and inclusive):
- Computer Vision: Image recognition, drone inspection, safety monitoring, visual inspection, cameras, sensors, image processing
- Predictive Analytics: Risk assessment, maintenance prediction, forecasting, machine learning, data analytics, prediction, modeling, predictive analytics
- Generative Design: Optimization, parametric modeling, algorithmic design, design optimization, automated design, AI design
- Robotics/Automation: Robots, automation, autonomous machinery, drones, automated construction, autonomous systems, robotic systems

IMPORTANT CRITERIA:
1. The article MUST relate to BOTH Civil Engineering AND AI technologies
2. Be FLEXIBLE - if the topic is even remotely related to CE (construction, infrastructure, building, energy, transportation, etc.) AND mentions AI/ML/automation/robotics/data analytics, consider it valid
3. Data center construction, energy infrastructure, transportation systems, building projects, infrastructure development - all are valid CE contexts
4. AI mentions can be indirect - if article discusses AI infrastructure, AI data centers, AI in construction, automation in building, etc., consider it valid
5. If keywords suggest both CE and AI relevance, be generous in validation

Respond with a JSON object containing:
- "is_valid": true/false (true if BOTH CE and AI are relevant)
- "ce_area": primary CE area if valid (or empty string)
- "ai_technology": primary AI technology if valid (or empty string)
- "confidence": 0.0-1.0
- "reason": brief explanation

Respond ONLY with valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in Civil Engineering and AI. Be flexible and inclusive when validating articles. If an article relates to both CE and AI (even indirectly), mark it as valid. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
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
            'ce_area': result.get('ce_area', ''),
            'ai_technology': result.get('ai_technology', ''),
            'confidence': float(result.get('confidence', 0.5)),
            'reason': result.get('reason', '')
        }
        
    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON parse error: {e}")
        return {
            'is_valid': False,
            'ce_area': '',
            'ai_technology': '',
            'confidence': 0.0,
            'reason': f'JSON parse error: {str(e)}'
        }
    except Exception as e:
        print(f"    ⚠️  API error: {e}")
        return {
            'is_valid': False,
            'ce_area': '',
            'ai_technology': '',
            'confidence': 0.0,
            'reason': f'API error: {str(e)}'
        }


def main():
    print("=" * 70)
    print("VALIDATING NEWSAPI ARTICLES (FLEXIBLE CRITERIA)")
    print("=" * 70)
    
    if not INPUT_CSV.exists():
        print(f"❌ Error: Input CSV not found: {INPUT_CSV}")
        return
    
    print(f"Reading articles from {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    print(f"Total articles: {len(df)}\n")
    
    # Filter articles that have both AI and CE keywords
    print("Filtering articles with both AI and CE keywords...")
    df['has_ai'] = df['ai_keywords_found'].astype(str).str.strip() != ''
    df['has_ce'] = df['ce_keywords_found'].astype(str).str.strip() != ''
    df['has_both'] = df['has_ai'] & df['has_ce']
    
    candidates = df[df['has_both']].copy()
    print(f"Articles with both AI and CE keywords: {len(candidates)}")
    print(f"Articles with only AI keywords: {len(df[df['has_ai'] & ~df['has_ce']])}")
    print(f"Articles with only CE keywords: {len(df[df['has_ce'] & ~df['has_ai']])}")
    print(f"Articles with neither: {len(df[~df['has_ai'] & ~df['has_ce']])}\n")
    
    # Validate with LLM
    print("Validating articles with LLM (flexible criteria)...")
    print("=" * 70)
    
    results = []
    valid_count = 0
    
    for idx, row in candidates.iterrows():
        title = str(row.get('title', ''))
        description = str(row.get('description', ''))
        ai_keywords = str(row.get('ai_keywords_found', ''))
        ce_keywords = str(row.get('ce_keywords_found', ''))
        
        print(f"[{len(results)+1}/{len(candidates)}] Validating: {title[:60]}...")
        
        validation = validate_with_llm(title, description, ai_keywords, ce_keywords)
        
        results.append({
            'article_id': idx,
            'title': title,
            'description': description,
            'url': row.get('url', ''),
            'source': row.get('source', ''),
            'publication_date': row.get('publication_date', ''),
            'ai_keywords_found': ai_keywords,
            'ce_keywords_found': ce_keywords,
            'is_valid': validation['is_valid'],
            'ce_area': validation['ce_area'],
            'ai_technology': validation['ai_technology'],
            'confidence': validation['confidence'],
            'reason': validation['reason']
        })
        
        if validation['is_valid']:
            valid_count += 1
            print(f"    ✓ VALID - CE: {validation['ce_area']}, AI: {validation['ai_technology']} (conf: {validation['confidence']:.2f})")
        else:
            print(f"    ✗ NOT VALID (conf: {validation['confidence']:.2f}) - {validation['reason'][:50]}...")
        
        time.sleep(LLM_DELAY)
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    print(f"Total articles with both keywords: {len(candidates)}")
    print(f"Valid articles (CE + AI): {valid_count} ({valid_count/len(candidates)*100:.1f}%)")
    print(f"Invalid articles: {len(candidates) - valid_count} ({(len(candidates)-valid_count)/len(candidates)*100:.1f}%)")
    
    # CE Area distribution
    if valid_count > 0:
        print("\nCE Area Distribution (valid articles):")
        ce_dist = results_df[results_df['is_valid']]['ce_area'].value_counts()
        for area, count in ce_dist.items():
            print(f"  {area:30s}: {count:3d} articles")
        
        # AI Technology distribution
        print("\nAI Technology Distribution (valid articles):")
        ai_dist = results_df[results_df['is_valid']]['ai_technology'].value_counts()
        for tech, count in ai_dist.items():
            print(f"  {tech:30s}: {count:3d} articles")
    
    print(f"\nResults saved to: {OUTPUT_CSV}")
    print("=" * 70)


if __name__ == "__main__":
    main()

