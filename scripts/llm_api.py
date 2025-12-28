"""
LLM API integration module for CE49X Final Project.
Supports OpenAI GPT models and Anthropic Claude models.
"""

import os
import json
from typing import List, Dict, Optional, Literal
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai package not installed. Install with: pip install openai")

# Try to import Anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic package not installed. Install with: pip install anthropic")


class LLMClassifier:
    """
    LLM-based classifier for articles.
    Classifies articles into CE areas and AI technologies.
    """
    
    def __init__(
        self,
        provider: Literal['openai', 'anthropic'] = 'openai',
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize LLM classifier.
        
        Args:
            provider: 'openai' or 'anthropic'
            model: Model name (e.g., 'gpt-4', 'gpt-3.5-turbo', 'claude-3-opus-20240229')
            api_key: API key (if not provided, reads from environment)
        """
        self.provider = provider
        self.model = model or self._get_default_model(provider)
        self.api_key = api_key or self._get_api_key(provider)
        
        if provider == 'openai' and OPENAI_AVAILABLE:
            openai.api_key = self.api_key
            self.client = openai
        elif provider == 'anthropic' and ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Provider {provider} not available. Install required package.")
    
    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider."""
        defaults = {
            'openai': 'gpt-3.5-turbo',
            'anthropic': 'claude-3-sonnet-20240229'
        }
        return defaults.get(provider, 'gpt-3.5-turbo')
    
    def _get_api_key(self, provider: str) -> str:
        """Get API key from environment."""
        env_keys = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY'
        }
        key = os.getenv(env_keys.get(provider, 'OPENAI_API_KEY'))
        if not key:
            raise ValueError(f"API key not found. Set {env_keys.get(provider)} environment variable.")
        return key
    
    def _create_classification_prompt(self, title: str, content: str) -> str:
        """Create prompt for classification."""
        prompt = f"""You are an expert in Civil Engineering and Artificial Intelligence. 
Analyze the following article and classify it into:
1. Civil Engineering Areas (select all that apply):
   - Structural
   - Geotechnical
   - Transportation
   - Construction Management
   - Environmental Engineering

2. AI Technologies (select all that apply):
   - Computer Vision
   - Predictive Analytics
   - Generative Design
   - Robotics/Automation
   - Machine Learning

Article Title: {title}

Article Content (first 2000 characters):
{content[:2000]}

Respond ONLY with a valid JSON object in this exact format:
{{
    "ce_areas": ["Structural", "Transportation"],
    "ai_technologies": ["Computer Vision", "Machine Learning"],
    "confidence": 0.85,
    "reasoning": "Brief explanation of why these classifications were chosen"
}}

If the article is not relevant to both Civil Engineering AND AI, return empty arrays.
"""
        return prompt
    
    def classify_article(self, title: str, content: str) -> Dict:
        """
        Classify an article using LLM.
        
        Args:
            title: Article title
            content: Article content/text
            
        Returns:
            Dictionary with classification results
        """
        prompt = self._create_classification_prompt(title, content or "")
        
        try:
            if self.provider == 'openai':
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that classifies articles. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                response_text = response.choices[0].message.content
                
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                response_text = response.content[0].text
            
            # Parse JSON response
            # Sometimes LLM wraps JSON in markdown code blocks
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            return {
                'ce_areas': result.get('ce_areas', []),
                'ai_technologies': result.get('ai_technologies', []),
                'confidence': result.get('confidence', 0.5),
                'reasoning': result.get('reasoning', ''),
                'raw_response': response_text,
                'model': self.model,
                'provider': self.provider
            }
            
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Response was: {response_text[:200]}")
            return {
                'ce_areas': [],
                'ai_technologies': [],
                'confidence': 0.0,
                'reasoning': f'JSON parse error: {str(e)}',
                'raw_response': response_text,
                'model': self.model,
                'provider': self.provider
            }
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return {
                'ce_areas': [],
                'ai_technologies': [],
                'confidence': 0.0,
                'reasoning': f'API error: {str(e)}',
                'raw_response': '',
                'model': self.model,
                'provider': self.provider
            }
    
    def classify_batch(self, articles: List[Dict], batch_size: int = 10) -> List[Dict]:
        """
        Classify multiple articles in batches.
        
        Args:
            articles: List of article dicts with 'title' and 'content' keys
            batch_size: Number of articles to process per batch
            
        Returns:
            List of classification results
        """
        results = []
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(articles)-1)//batch_size + 1}...")
            
            for article in batch:
                result = self.classify_article(
                    article.get('title', ''),
                    article.get('content', '') or article.get('full_text', '')
                )
                result['article_id'] = article.get('id')
                results.append(result)
        
        return results


def get_classifier(provider: Optional[str] = None) -> LLMClassifier:
    """
    Factory function to get LLM classifier.
    Auto-detects available provider from environment.
    """
    if provider:
        return LLMClassifier(provider=provider)
    
    # Auto-detect
    if os.getenv('OPENAI_API_KEY'):
        return LLMClassifier(provider='openai')
    elif os.getenv('ANTHROPIC_API_KEY'):
        return LLMClassifier(provider='anthropic')
    else:
        raise ValueError("No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")


if __name__ == "__main__":
    # Test the classifier
    classifier = get_classifier()
    
    test_article = {
        'title': 'AI-Powered Structural Health Monitoring for Bridges',
        'content': 'This article discusses the use of computer vision and machine learning to monitor bridge health in real-time...'
    }
    
    result = classifier.classify_article(test_article['title'], test_article['content'])
    print(json.dumps(result, indent=2))

