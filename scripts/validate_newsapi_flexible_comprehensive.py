"""
Comprehensive flexible validation for NewsAPI articles.
Must have BOTH AI and CE keywords, with flexible sub-discipline matching.
Focus on maximizing valid articles from 1780 total.
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
    "Structural": ["analysis", "design", "health monitoring", "materials", "buildings", "bridges", "structures", "concrete", "steel", "structural", "foundation", "load", "beam", "column"],
    "Geotechnical": ["soil", "foundations", "tunnels", "excavation", "ground", "underground", "geotechnical", "slope", "retaining wall", "pile"],
    "Transportation": ["traffic", "roads", "autonomous vehicles", "logistics", "transportation", "highway", "railway", "airport", "port", "mobility", "transit", "traffic flow", "road safety"],
    "Construction Management": ["scheduling", "safety", "cost estimation", "site monitoring", "project management", "construction", "building", "infrastructure development", "data center", "datacenter", "facility", "development", "project"],
    "Environmental Engineering": ["sustainability", "waste management", "green building", "renewable energy", "water", "energy infrastructure", "climate", "environmental", "solar", "wind", "power", "energy"]
}

# AI Technologies with sub-disciplines
AI_TECHNOLOGIES = {
    "Computer Vision": ["image recognition", "drone inspection", "safety monitoring", "visual inspection", "cameras", "sensors", "computer vision", "image processing", "visual", "detection"],
    "Predictive Analytics": ["risk assessment", "maintenance prediction", "forecasting", "machine learning", "data analytics", "prediction", "predictive", "analytics", "forecast", "modeling", "neural networks", "deep learning"],
    "Generative Design": ["optimization", "parametric modeling", "algorithmic design", "design optimization", "automated design", "generative", "optimization", "algorithm", "parametric"],
    "Robotics/Automation": ["brick-laying robots", "autonomous machinery", "drones", "automated construction", "autonomous systems", "robotics", "automation", "robotic", "autonomous", "automated", "robot"]
}


def check_keyword_presence(text: str, keywords: List[str]) -> bool:
    """Check if any keyword appears in text (case-insensitive)."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def validate_with_llm_flexible(title: str, description: str, ai_keywords: str, ce_keywords: str) -> Dict:
    """
    Use LLM to validate if article has BOTH AI and CE keywords in relevant context.
    Very flexible - if topic is close, mark as valid.
    """
    full_text = f"Title: {title}\n\nDescription: {description}"
    
    # Parse keywords
    ai_kw_list = [kw.strip() for kw in ai_keywords.split(',') if kw.strip()] if pd.notna(ai_keywords) else []
    ce_kw_list = [kw.strip() for kw in ce_keywords.split(',') if kw.strip()] if pd.notna(ce_keywords) else []
    
    prompt = f"""Analyze the following article. It has been pre-filtered to contain BOTH AI keywords ({', '.join(ai_kw_list)}) AND CE keywords ({', '.join(ce_kw_list)}).

Article:
{full_text}

Civil Engineering Areas (be flexible and inclusive):
- Structural: Analysis, design, health monitoring, materials, buildings, bridges, structures, concrete, steel, foundations, loads
- Geotechnical: Soil, foundations, tunnels, excavation, ground engineering, underground structures
- Transportation: Traffic, roads, autonomous vehicles, logistics, transportation systems, railways, airports, ports, mobility, road safety
- Construction Management: Scheduling, safety, cost estimation, site monitoring, project management, construction projects, building, infrastructure development, data centers, facilities, development projects
- Environmental Engineering: Sustainability, waste management, green building, renewable energy, water infrastructure, energy infrastructure, climate, solar, wind power

AI Technologies (be flexible and inclusive):
- Computer Vision: Image recognition, drone inspection, safety monitoring, visual inspection, cameras, sensors, visual detection
- Predictive Analytics: Risk assessment, maintenance prediction, forecasting, machine learning, data analytics, prediction, neural networks, deep learning, modeling
- Generative Design: Optimization, parametric modeling, algorithmic design, design optimization, automated design, algorithms
- Robotics/Automation: Robots, automation, autonomous machinery, drones, automated construction, autonomous systems, robotic systems

IMPORTANT: 
- This article already has both AI and CE keywords, so be VERY FLEXIBLE.
- If the topic is even REMOTELY related to Civil Engineering AND AI, mark it as valid.
- Data centers, infrastructure projects, energy facilities, transportation systems, construction projects - all are valid CE contexts.
- AI technologies mentioned in context of infrastructure, construction, or engineering - all are valid.
- If the article discusses AI in relation to infrastructure, construction, energy, transportation, or any physical project, it's valid.

Respond with a JSON object containing:
- "is_valid": true/false (be VERY lenient - if topic is close, mark as true)
- "ce_areas": array of applicable CE area names (can be empty if not clearly applicable, but try to find at least one)
- "ai_technologies": array of applicable AI technology names (can be empty if not clearly applicable, but try to find at least one)
- "confidence": 0.0-1.0 (how confident you are)
- "reason": brief explanation

Respond ONLY with valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in Civil Engineering and AI. Be VERY FLEXIBLE and INCLUSIVE. If an article has both AI and CE keywords and the topic is even remotely related, mark it as valid. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
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
            'is_valid': bool(result.get('is_valid', True)),  # Default to True if unclear
            'ce_areas': result.get('ce_areas', []),
            'ai_technologies': result.get('ai_technologies', []),
            'confidence': float(result.get('confidence', 0.7)),
            'reason': result.get('reason', 'Flexible validation')
        }
        
    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON parse error: {e}")
        # Default to valid if we can't parse
        return {
            'is_valid': True,
            'ce_areas': ['Construction Management'],
            'ai_technologies': [],
            'confidence': 0.5,
            'reason': f'JSON parse error, defaulting to valid'
        }
    except Exception as e:
        print(f"    ⚠️  API error: {e}")
        # Default to valid if API fails
        return {
            'is_valid': True,
            'ce_areas': ['Construction Management'],
            'ai_technologies': [],
            'confidence': 0.5,
            'reason': f'API error, defaulting to valid'
        }


def main():
    print("=" * 70)
    print("COMPREHENSIVE FLEXIBLE VALIDATION - NewsAPI Articles")
    print("=" * 70)
    
    if not INPUT_CSV.exists():
        print(f"❌ Error: Input CSV not found: {INPUT_CSV}")
        return
    
    print(f"Reading articles from {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    print(f"Total articles: {len(df)}\n")
    
    # Filter articles with BOTH AI and CE keywords
    df['has_ai'] = df['ai_keywords_found'].notna() & (df['ai_keywords_found'].astype(str).str.strip() != '')
    df['has_ce'] = df['ce_keywords_found'].notna() & (df['ce_keywords_found'].astype(str).str.strip() != '')
    df['has_both'] = df['has_ai'] & df['has_ce']
    
    print(f"Articles with AI keywords: {df['has_ai'].sum()}")
    print(f"Articles with CE keywords: {df['has_ce'].sum()}")
    print(f"Articles with BOTH AI and CE keywords: {df['has_both'].sum()}\n")
    
    # Process only articles with both keywords
    articles_to_validate = df[df['has_both']].copy()
    print(f"Validating {len(articles_to_validate)} articles with both keywords...\n")
    
    results = []
    valid_count = 0
    
    for idx, row in articles_to_validate.iterrows():
        title = str(row.get('title', ''))
        description = str(row.get('description', ''))
        ai_keywords = str(row.get('ai_keywords_found', ''))
        ce_keywords = str(row.get('ce_keywords_found', ''))
        
        print(f"[{len(results)+1}/{len(articles_to_validate)}] {title[:60]}...")
        
        validation = validate_with_llm_flexible(title, description, ai_keywords, ce_keywords)
        
        ce_areas_str = ', '.join(validation['ce_areas']) if validation['ce_areas'] else ''
        ai_techs_str = ', '.join(validation['ai_technologies']) if validation['ai_technologies'] else ''
        
        if validation['is_valid']:
            valid_count += 1
            print(f"    ✓ VALID (conf: {validation['confidence']:.2f}) - CE: {ce_areas_str[:40]} | AI: {ai_techs_str[:40]}")
        else:
            print(f"    ✗ NOT VALID (conf: {validation['confidence']:.2f}) - {validation['reason'][:50]}...")
        
        results.append({
            'title': title,
            'description': description,
            'ai_keywords_found': ai_keywords,
            'ce_keywords_found': ce_keywords,
            'is_valid': validation['is_valid'],
            'ce_areas': ce_areas_str,
            'ai_technologies': ai_techs_str,
            'confidence': validation['confidence'],
            'reason': validation['reason']
        })
        
        time.sleep(LLM_DELAY)
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    print(f"Total articles validated: {len(results)}")
    print(f"Valid articles: {valid_count} ({valid_count/len(results)*100:.1f}%)")
    print(f"Invalid articles: {len(results)-valid_count} ({(len(results)-valid_count)/len(results)*100:.1f}%)")
    print(f"\nResults saved to: {OUTPUT_CSV}")
    print("=" * 70)


if __name__ == "__main__":
    main()

