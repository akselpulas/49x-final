"""
Validate NewsAPI articles - both CE and AI keywords must be present.
Uses expanded sub-discipline keywords for better coverage.
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
OUTPUT_VALIDATION = PROJECT_ROOT / "data" / "newsapi_ce_ai_validation.csv"
OUTPUT_VALID = PROJECT_ROOT / "data" / "newsapi_valid_ce_ai.csv"

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=OPENAI_API_KEY)

# Rate limiting
LLM_DELAY = 0.5
MIN_CONFIDENCE = 0.65

# Expanded CE Sub-discipline Keywords
CE_KEYWORDS = {
    "Structural": [
        "structural", "structure", "analysis", "design", "health monitoring", "materials",
        "steel", "concrete", "reinforcement", "beam", "column", "foundation", "load",
        "stress", "strain", "deflection", "seismic", "earthquake", "bridge", "building",
        "skyscraper", "tower", "frame", "truss", "arch", "cable", "suspension", "retrofit"
    ],
    "Geotechnical": [
        "geotechnical", "soil", "foundation", "tunnel", "excavation", "slope",
        "retaining wall", "pile", "ground", "subsoil", "bedrock", "settlement",
        "liquefaction", "landslide", "embankment", "cut", "fill", "geology", "geological",
        "underground", "borehole", "drilling", "shoring", "anchoring"
    ],
    "Transportation": [
        "transportation", "traffic", "road", "highway", "autonomous vehicle", "logistics",
        "railway", "rail", "airport", "port", "harbor", "pavement", "asphalt", "intersection",
        "roundabout", "bridge", "tunnel", "transit", "mobility", "public transport", "metro",
        "subway", "urban planning", "traffic flow", "congestion", "parking", "pedestrian",
        "bicycle", "cycling", "infrastructure", "transport"
    ],
    "Construction Management": [
        "construction management", "scheduling", "safety", "cost estimation", "site monitoring",
        "project management", "bim", "building information", "procurement", "contract",
        "quality control", "inspection", "workforce", "labor", "equipment", "machinery",
        "site", "construction site", "construction", "building", "development", "project"
    ],
    "Environmental Engineering": [
        "environmental engineering", "sustainability", "waste management", "green building",
        "renewable energy", "solar", "wind", "water treatment", "wastewater", "sewage",
        "pollution", "air quality", "carbon", "emission", "climate", "resilience", "adaptation",
        "leed", "certification", "energy efficiency", "environmental", "infrastructure"
    ]
}

# Expanded AI Technology Keywords
AI_KEYWORDS = {
    "Computer Vision": [
        "computer vision", "image recognition", "drone inspection", "safety monitoring",
        "visual inspection", "image processing", "object detection", "pattern recognition",
        "camera", "surveillance", "monitoring", "inspection", "defect detection", "crack detection",
        "visual", "imaging", "photogrammetry", "lidar", "scanning"
    ],
    "Predictive Analytics": [
        "predictive analytics", "risk assessment", "maintenance prediction", "forecast",
        "prediction", "machine learning", "ml", "data analytics", "predictive model",
        "risk analysis", "failure prediction", "condition assessment", "prognostics",
        "forecasting", "analytics", "data analysis", "statistical", "modeling"
    ],
    "Generative Design": [
        "generative design", "optimization", "parametric modeling", "algorithmic design",
        "design optimization", "topology optimization", "genetic algorithm", "evolutionary",
        "automated design", "computational design", "parametric", "optimization", "algorithm"
    ],
    "Robotics/Automation": [
        "robotics", "automation", "brick-laying robot", "autonomous machinery", "robot",
        "automated", "autonomous", "drones", "uav", "robotic", "automation", "automated construction",
        "3d printing", "additive manufacturing", "robotic", "automated", "autonomous system"
    ]
}

# All CE keywords (flattened)
ALL_CE_KEYWORDS = []
for keywords in CE_KEYWORDS.values():
    ALL_CE_KEYWORDS.extend(keywords)

# All AI keywords (flattened)
ALL_AI_KEYWORDS = []
for keywords in AI_KEYWORDS.values():
    ALL_AI_KEYWORDS.extend(keywords)


def find_keywords_in_text(text: str, keywords: List[str]) -> Set[str]:
    """Find which keywords appear in the text."""
    if pd.isna(text):
        return set()
    text_lower = str(text).lower()
    found = set()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found.add(keyword)
    return found


def validate_with_llm(title: str, description: str, text: str, ce_keywords_found: List[str], ai_keywords_found: List[str]) -> Dict:
    """
    Use LLM to validate if article is valid (has both CE and AI relevance).
    """
    ce_keywords_str = ', '.join(ce_keywords_found) if ce_keywords_found else 'None'
    ai_keywords_str = ', '.join(ai_keywords_found) if ai_keywords_found else 'None'
    
    full_text = f"Title: {title}\n\nDescription: {description}\n\nText: {text[:1500]}"
    
    prompt = f"""Analyze the following article. It contains CE keywords: {ce_keywords_str} and AI keywords: {ai_keywords_str}.

Article:
{full_text}

Determine if this article is VALID - meaning it discusses BOTH:
1. Civil Engineering topics (structural, geotechnical, transportation, construction, environmental)
2. AI technologies (computer vision, predictive analytics, generative design, robotics/automation)

The article must be relevant to BOTH CE and AI. If it only discusses one or neither, it's invalid.

Respond with a JSON object containing:
- "is_valid": true/false (true only if BOTH CE and AI are relevant)
- "ce_area": the most relevant CE sub-discipline (Structural, Geotechnical, Transportation, Construction Management, Environmental Engineering)
- "ai_technology": the most relevant AI technology (Computer Vision, Predictive Analytics, Generative Design, Robotics/Automation)
- "confidence": 0.0-1.0
- "reason": brief explanation

Be FLEXIBLE and INCLUSIVE - if the article mentions construction/infrastructure AND any AI/ML/automation, consider it valid.

Respond ONLY with valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in Civil Engineering and AI. Validate articles that discuss BOTH CE and AI. Be flexible and inclusive. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=250
        )
        
        result_text = response.choices[0].message.content.strip()
        
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
            result_text = result_text.strip()
        
        result = json.loads(result_text)
        
        return {
            'is_valid': result.get('is_valid', False),
            'ce_area': result.get('ce_area', ''),
            'ai_technology': result.get('ai_technology', ''),
            'confidence': float(result.get('confidence', 0.0)),
            'reason': result.get('reason', 'No reason provided')
        }
        
    except Exception as e:
        print(f"    ⚠️  Error: {e}")
        return {
            'is_valid': False,
            'ce_area': '',
            'ai_technology': '',
            'confidence': 0.0,
            'reason': f'Error: {str(e)}'
        }


def main():
    print("=" * 70)
    print("NEWSAPI CE & AI INTERSECTION VALIDATION")
    print("=" * 70)
    print(f"Input CSV: {INPUT_CSV}")
    print(f"Output Validation: {OUTPUT_VALIDATION}")
    print(f"Output Valid: {OUTPUT_VALID}\n")
    
    if not INPUT_CSV.exists():
        print(f"❌ Error: Input file not found: {INPUT_CSV}")
        return
    
    print("Reading CSV file...")
    df = pd.read_csv(INPUT_CSV)
    print(f"Found {len(df)} articles\n")
    
    # Prepare results
    validation_results = []
    valid_articles = []
    valid_count = 0
    invalid_count = 0
    
    # Process each article
    for idx, row in df.iterrows():
        title = str(row.get('title', ''))
        description = str(row.get('description', ''))
        text = str(row.get('text', '')) or str(row.get('content', '')) or ''
        url = str(row.get('url', ''))
        published_at = row.get('publishedAt', '') or row.get('published_at', '')
        source = str(row.get('source', '')) or str(row.get('source_name', ''))
        
        # Combine all text for keyword search
        full_text = f"{title} {description} {text}".lower()
        
        # Find CE keywords
        ce_keywords_found = []
        for area, keywords in CE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in full_text:
                    ce_keywords_found.append(keyword)
                    break  # One keyword per area is enough
        
        # Find AI keywords
        ai_keywords_found = []
        for tech, keywords in AI_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in full_text:
                    ai_keywords_found.append(keyword)
                    break  # One keyword per tech is enough
        
        print(f"[{idx+1}/{len(df)}] {title[:60]}...")
        print(f"    CE keywords: {len(ce_keywords_found)}, AI keywords: {len(ai_keywords_found)}")
        
        # Must have BOTH CE and AI keywords
        if not ce_keywords_found or not ai_keywords_found:
            print(f"    ✗ Missing keywords (CE: {len(ce_keywords_found)}, AI: {len(ai_keywords_found)})")
            validation_results.append({
                'title': title,
                'url': url,
                'ce_keywords_found': ', '.join(ce_keywords_found),
                'ai_keywords_found': ', '.join(ai_keywords_found),
                'is_valid': False,
                'confidence': 0.0,
                'reason': f'Missing keywords: CE={len(ce_keywords_found)}, AI={len(ai_keywords_found)}'
            })
            invalid_count += 1
            continue
        
        # Validate with LLM
        validation = validate_with_llm(title, description, text, ce_keywords_found, ai_keywords_found)
        
        is_valid = validation['is_valid'] and validation['confidence'] >= MIN_CONFIDENCE
        
        if is_valid:
            print(f"    ✓ VALID - CE: {validation['ce_area']}, AI: {validation['ai_technology']} (conf: {validation['confidence']:.2f})")
            valid_count += 1
            
            valid_articles.append({
                'title': title,
                'description': description,
                'text': text,
                'url': url,
                'published_at': published_at,
                'source': source,
                'ce_keywords_found': ', '.join(ce_keywords_found),
                'ai_keywords_found': ', '.join(ai_keywords_found),
                'ce_area': validation['ce_area'],
                'ai_technology': validation['ai_technology'],
                'validation_confidence': validation['confidence'],
                'validation_reason': validation['reason']
            })
        else:
            print(f"    ✗ Not valid (conf: {validation['confidence']:.2f}) - {validation['reason'][:50]}")
            invalid_count += 1
        
        validation_results.append({
            'title': title,
            'url': url,
            'ce_keywords_found': ', '.join(ce_keywords_found),
            'ai_keywords_found': ', '.join(ai_keywords_found),
            'is_valid': is_valid,
            'ce_area': validation['ce_area'],
            'ai_technology': validation['ai_technology'],
            'confidence': validation['confidence'],
            'reason': validation['reason']
        })
        
        time.sleep(LLM_DELAY)
    
    # Save results
    validation_df = pd.DataFrame(validation_results)
    validation_df.to_csv(OUTPUT_VALIDATION, index=False, encoding='utf-8-sig')
    
    if valid_articles:
        valid_df = pd.DataFrame(valid_articles)
        valid_df.to_csv(OUTPUT_VALID, index=False, encoding='utf-8-sig')
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print(f"Total articles: {len(df)}")
    print(f"Valid articles (CE + AI): {valid_count} ({valid_count/len(df)*100:.1f}%)")
    print(f"Invalid articles: {invalid_count} ({invalid_count/len(df)*100:.1f}%)")
    print(f"\nValidation results saved to: {OUTPUT_VALIDATION}")
    print(f"Valid articles saved to: {OUTPUT_VALID}")
    print("=" * 70)


if __name__ == "__main__":
    main()

