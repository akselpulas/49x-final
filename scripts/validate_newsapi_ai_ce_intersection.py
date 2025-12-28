"""
Validate NewsAPI articles: Must have BOTH AI and CE keywords.
Uses comprehensive sub-discipline keywords for better coverage.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Set
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
OUTPUT_VALIDATION_CSV = PROJECT_ROOT / "data" / "newsapi_ai_ce_validation.csv"
OUTPUT_VALID_CSV = PROJECT_ROOT / "data" / "newsapi_valid_ai_ce.csv"

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=OPENAI_API_KEY)

# Rate limiting
LLM_DELAY = 0.5
MIN_CONFIDENCE = 0.65

# Comprehensive CE Sub-disciplines with keywords
CE_SUBDISCIPLINES = {
    "Structural": [
        "structural", "structure", "analysis", "design", "health monitoring", 
        "materials", "steel", "concrete", "reinforcement", "beam", "column", 
        "foundation", "load", "stress", "strain", "deflection", "seismic", 
        "earthquake", "bridge", "building", "skyscraper", "tower", "frame",
        "structural engineering", "structural analysis", "structural design"
    ],
    "Geotechnical": [
        "geotechnical", "soil", "foundation", "tunnel", "excavation", 
        "slope", "retaining wall", "pile", "ground", "subsoil", "bedrock", 
        "settlement", "liquefaction", "landslide", "embankment", "cut", 
        "fill", "geology", "geological", "underground", "geotechnical engineering"
    ],
    "Transportation": [
        "transportation", "traffic", "road", "highway", "autonomous vehicle", 
        "logistics", "railway", "rail", "airport", "port", "harbor", 
        "pavement", "asphalt", "intersection", "roundabout", "bridge", 
        "tunnel", "transit", "mobility", "public transport", "metro", 
        "subway", "urban planning", "traffic flow", "congestion", "transportation engineering"
    ],
    "Construction Management": [
        "construction management", "scheduling", "safety", "cost estimation", 
        "site monitoring", "project management", "bim", "building information", 
        "procurement", "contract", "quality control", "inspection", 
        "workforce", "labor", "equipment", "machinery", "site", "construction site",
        "construction", "building", "infrastructure development"
    ],
    "Environmental Engineering": [
        "environmental engineering", "sustainability", "waste management", 
        "green building", "renewable energy", "solar", "wind", "water treatment", 
        "wastewater", "sewage", "pollution", "air quality", "carbon", "emission", 
        "climate", "resilience", "adaptation", "leed", "certification", "infrastructure"
    ]
}

# Comprehensive AI Technologies with keywords
AI_TECHNOLOGIES = {
    "Computer Vision": [
        "computer vision", "image recognition", "drone inspection", 
        "safety monitoring", "visual inspection", "image processing", 
        "object detection", "pattern recognition", "camera", "surveillance", 
        "monitoring", "inspection", "defect detection", "crack detection",
        "visual", "imaging", "camera system"
    ],
    "Predictive Analytics": [
        "predictive analytics", "risk assessment", "maintenance prediction", 
        "forecast", "prediction", "machine learning", "ml", "data analytics", 
        "predictive model", "risk analysis", "failure prediction", 
        "condition assessment", "prognostics", "neural networks", "deep learning",
        "artificial intelligence", "ai", "analytics", "forecasting"
    ],
    "Generative Design": [
        "generative design", "optimization", "parametric modeling", 
        "algorithmic design", "design optimization", "topology optimization", 
        "genetic algorithm", "evolutionary", "automated design", 
        "computational design", "parametric", "optimization algorithm"
    ],
    "Robotics/Automation": [
        "robotics", "automation", "brick-laying robot", "autonomous machinery", 
        "robot", "automated", "autonomous", "drones", "uav", "robotic", 
        "automation", "automated construction", "3d printing", "additive manufacturing",
        "autonomous vehicle", "autonomous system", "robotic system"
    ]
}


def check_keywords_in_text(text: str, keywords: List[str]) -> Set[str]:
    """Check which keywords appear in text."""
    if pd.isna(text):
        text = ""
    text_lower = str(text).lower()
    found = set()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found.add(keyword)
    return found


def validate_with_llm_comprehensive(title: str, description: str, ai_keywords: List[str], ce_keywords: List[str]) -> Dict:
    """
    Use LLM to validate if article has BOTH AI and CE keywords in relevant context.
    More comprehensive - includes sub-disciplines.
    """
    if not ai_keywords and not ce_keywords:
        return {
            'is_valid': False,
            'confidence': 0.0,
            'reason': 'No AI or CE keywords found',
            'ce_areas': [],
            'ai_technologies': []
        }
    
    # Combine text
    full_text = f"Title: {title}\n\nDescription: {description}"
    ai_keywords_str = ', '.join(ai_keywords) if ai_keywords else 'None'
    ce_keywords_str = ', '.join(ce_keywords) if ce_keywords else 'None'
    
    prompt = f"""Analyze the following article. It MUST have BOTH AI technologies AND Civil Engineering relevance to be valid.

Article:
{full_text}

AI Keywords found: {ai_keywords_str}
CE Keywords found: {ce_keywords_str}

Civil Engineering Sub-disciplines:
- Structural: Analysis, design, health monitoring, materials, buildings, bridges, structures
- Geotechnical: Soil, foundations, tunnels, excavation, ground engineering
- Transportation: Traffic, roads, autonomous vehicles, logistics, transportation systems
- Construction Management: Scheduling, safety, cost estimation, site monitoring, project management, construction projects
- Environmental Engineering: Sustainability, waste management, green building, renewable energy, water, energy infrastructure

AI Technologies:
- Computer Vision: Image recognition, drone inspection, safety monitoring, visual inspection, cameras, sensors
- Predictive Analytics: Risk assessment, maintenance prediction, forecasting, machine learning, data analytics, prediction, neural networks
- Generative Design: Optimization, parametric modeling, algorithmic design, design optimization, automated design
- Robotics/Automation: Robots, automation, autonomous machinery, drones, automated construction, autonomous systems

Respond with JSON:
- "is_valid": true/false (true ONLY if BOTH AI and CE are relevant)
- "confidence": 0.0-1.0
- "reason": explanation
- "ce_areas": array of relevant CE areas (can be multiple)
- "ai_technologies": array of relevant AI technologies (can be multiple)

Be INCLUSIVE - if article mentions AI in context of construction, infrastructure, buildings, transportation, energy, etc., it's likely valid.
If AI keywords are used in CE context (e.g., AI for construction, ML for infrastructure), it's valid.

Respond ONLY with valid JSON."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in Civil Engineering and AI. Articles must have BOTH AI and CE relevance. Be inclusive and flexible. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()
        
        result = json.loads(result_text)
        
        return {
            'is_valid': result.get('is_valid', False),
            'confidence': float(result.get('confidence', 0.0)),
            'reason': result.get('reason', 'No reason provided'),
            'ce_areas': result.get('ce_areas', []),
            'ai_technologies': result.get('ai_technologies', [])
        }
        
    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON parse error: {e}")
        return {
            'is_valid': False,
            'confidence': 0.0,
            'reason': f'JSON parse error: {str(e)}',
            'ce_areas': [],
            'ai_technologies': []
        }
    except Exception as e:
        print(f"    ⚠️  API error: {e}")
        return {
            'is_valid': False,
            'confidence': 0.0,
            'reason': f'API error: {str(e)}',
            'ce_areas': [],
            'ai_technologies': []
        }


def main():
    print("=" * 70)
    print("NEWSAPI AI & CE INTERSECTION VALIDATION")
    print("=" * 70)
    print(f"Input CSV: {INPUT_CSV}")
    print(f"Output Validation CSV: {OUTPUT_VALIDATION_CSV}")
    print(f"Output Valid CSV: {OUTPUT_VALID_CSV}\n")
    
    # Read CSV
    if not INPUT_CSV.exists():
        print(f"❌ Error: Input file not found: {INPUT_CSV}")
        return
    
    print("Reading CSV file...")
    df = pd.read_csv(INPUT_CSV)
    print(f"Found {len(df)} articles\n")
    
    # Filter articles with BOTH AI and CE keywords
    print("Filtering articles with both AI and CE keywords...")
    articles_with_both = []
    
    for idx, row in df.iterrows():
        ai_keywords_str = str(row.get('ai_keywords_found', ''))
        ce_keywords_str = str(row.get('ce_keywords_found', ''))
        
        # Parse keywords
        ai_keywords = [kw.strip() for kw in ai_keywords_str.split(',') if kw.strip()] if ai_keywords_str and ai_keywords_str != 'nan' else []
        ce_keywords = [kw.strip() for kw in ce_keywords_str.split(',') if kw.strip()] if ce_keywords_str and ce_keywords_str != 'nan' else []
        
        if ai_keywords and ce_keywords:
            articles_with_both.append({
                'index': idx,
                'row': row
            })
    
    print(f"Articles with both AI and CE keywords: {len(articles_with_both)} / {len(df)} ({len(articles_with_both)/len(df)*100:.1f}%)\n")
    
    # Validate with LLM
    print("Validating articles with LLM (must have BOTH AI and CE relevance)...")
    validation_results = []
    valid_articles = []
    valid_count = 0
    invalid_count = 0
    
    for idx, item in enumerate(articles_with_both):
        row = item['row']
        title = str(row.get('title', ''))
        description = str(row.get('description', ''))
        ai_keywords_str = str(row.get('ai_keywords_found', ''))
        ce_keywords_str = str(row.get('ce_keywords_found', ''))
        
        # Parse keywords
        ai_keywords = [kw.strip() for kw in ai_keywords_str.split(',') if kw.strip()] if ai_keywords_str and ai_keywords_str != 'nan' else []
        ce_keywords = [kw.strip() for kw in ce_keywords_str.split(',') if kw.strip()] if ce_keywords_str and ce_keywords_str != 'nan' else []
        
        print(f"[{idx+1}/{len(articles_with_both)}] {title[:60]}...")
        
        # Validate with LLM
        validation = validate_with_llm_comprehensive(title, description, ai_keywords, ce_keywords)
        
        is_valid = validation['is_valid'] and validation['confidence'] >= MIN_CONFIDENCE
        
        ce_areas_str = ', '.join(validation['ce_areas']) if validation['ce_areas'] else ''
        ai_techs_str = ', '.join(validation['ai_technologies']) if validation['ai_technologies'] else ''
        
        if is_valid:
            print(f"    ✓ VALID - CE: {ce_areas_str[:40]} | AI: {ai_techs_str[:40]} (conf: {validation['confidence']:.2f})")
            valid_count += 1
            
            # Add to valid articles
            valid_articles.append({
                'title': title,
                'publication_date': row.get('publication_date', ''),
                'source': row.get('source', ''),
                'url': row.get('url', ''),
                'description': description,
                'ai_keywords_found': ai_keywords_str,
                'ce_keywords_found': ce_keywords_str,
                'ce_areas': ce_areas_str,
                'ai_technologies': ai_techs_str,
                'validation_confidence': validation['confidence'],
                'validation_reason': validation['reason']
            })
        else:
            reason_short = validation['reason'][:50] if len(validation['reason']) > 50 else validation['reason']
            print(f"    ✗ Not valid (conf: {validation['confidence']:.2f}) - {reason_short}")
            invalid_count += 1
        
        validation_results.append({
            'title': title,
            'url': row.get('url', ''),
            'ai_keywords': ai_keywords_str,
            'ce_keywords': ce_keywords_str,
            'is_valid': is_valid,
            'confidence': validation['confidence'],
            'reason': validation['reason'],
            'ce_areas': ce_areas_str,
            'ai_technologies': ai_techs_str
        })
        
        # Rate limiting
        time.sleep(LLM_DELAY)
    
    # Save validation results
    validation_df = pd.DataFrame(validation_results)
    validation_df.to_csv(OUTPUT_VALIDATION_CSV, index=False, encoding='utf-8-sig')
    
    # Save valid articles
    if valid_articles:
        valid_df = pd.DataFrame(valid_articles)
        valid_df.to_csv(OUTPUT_VALID_CSV, index=False, encoding='utf-8-sig')
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print(f"Total articles in CSV: {len(df)}")
    print(f"Articles with both AI and CE keywords: {len(articles_with_both)}")
    print(f"Valid articles (AI + CE relevant): {valid_count} ({valid_count/len(articles_with_both)*100:.1f}% of articles with both)")
    print(f"Invalid articles: {invalid_count}")
    print(f"\nValidation results saved to: {OUTPUT_VALIDATION_CSV}")
    print(f"Valid articles saved to: {OUTPUT_VALID_CSV}")
    print("=" * 70)


if __name__ == "__main__":
    main()
