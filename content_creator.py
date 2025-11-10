"""
Content Creator - Generates parenting content using Claude API
"""
import anthropic
import random
import json
from datetime import datetime
import config

class ContentCreator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.load_learning_preferences()
    
    def load_learning_preferences(self):
        """Load user's learned preferences"""
        try:
            with open(config.LEARNING_FILE, 'r', encoding='utf-8') as f:
                self.preferences = json.load(f)
        except:
            self.preferences = {
                'liked_formats': {},
                'liked_tones': {},
                'liked_styles': {},
                'disliked_topics': [],
                'custom_edits': []
            }
    
    def save_preferences(self):
        """Save learned preferences"""
        import os
        os.makedirs(config.DATA_DIR, exist_ok=True)
        with open(config.LEARNING_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.preferences, f, ensure_ascii=False, indent=2)
    
    def get_weighted_choice(self, distribution_dict, preference_key):
        """Get weighted random choice based on distribution and learning"""
        # Adjust weights based on preferences
        weights = {}
        for key, base_weight in distribution_dict.items():
            preference_boost = self.preferences.get(preference_key, {}).get(key, 0)
            weights[key] = base_weight + (preference_boost * 0.1)
        
        # Normalize
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}
        
        return random.choices(list(weights.keys()), weights=list(weights.values()))[0]
    
    def generate_content_ideas(self, count=3, news_context=None):
        """Generate content ideas using Claude API"""
        
        # Determine format, tone, age for each variant
        variants = []
        for i in range(count):
            format_type = self.get_weighted_choice(config.FORMAT_DISTRIBUTION, 'liked_formats')
            tone = self.get_weighted_choice(config.TONE_DISTRIBUTION, 'liked_tones')
            age_group = 'preschool' if random.random() < config.AGE_DISTRIBUTION['preschool'] else 'school'
            
            variants.append({
                'format': format_type,
                'tone': tone,
                'age_group': age_group
            })
        
        # Build prompt for Claude
        prompt = self._build_generation_prompt(variants, news_context)
        
        # Call Claude API
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON response
            # Remove markdown code blocks if present
            response_text = response_text.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
            
            content_data = json.loads(response_text)
            
            return content_data.get('variants', [])
            
        except Exception as e:
            print(f"Error generating content: {e}")
            return []
    
    def _build_generation_prompt(self, variants, news_context):
        """Build the prompt for Claude API"""
        
        age_descriptions = {
            'preschool': 'სკოლამდელი ასაკი (3-7 წელი)',
            'school': 'სკოლის ასაკი (6-12 წელი)'
        }
        
        format_descriptions = {
            'myth_vs_reality': 'მითი VS რეალობა - გავრცელებული მითი და მეცნიერული ფაქტი',
            'self_assessment': 'თვით-შეფასება - კითხვები მშობლებისთვის თვითშემოწმებისთვის',
            'practical_scenario': 'პრაქტიკული სცენარი - რეალური სიტუაცია და გადაჭრის გზები',
            'quick_tip': 'სწრაფი რჩევა - ერთი მოკლე, მაგრამ ძლიერი იდეა',
            'mini_story': 'მინი ისტორია - რეალური კეისი ანონიმურად'
        }
        
        tone_descriptions = {
            'friendly': 'მეგობრული - თბილი, უშუალო, ახლობელი ტონი',
            'professional': 'პროფესიონალური - ავტორიტეტული, მეცნიერული',
            'practical': 'პრაქტიკული - კონკრეტული, actionable რჩევები',
            'storytelling': 'სათხრობი - ნარატივი, engaging ისტორია'
        }
        
        variants_desc = []
        for i, v in enumerate(variants, 1):
            variants_desc.append(f"""
ვარიანტი {i}:
- ფორმატი: {format_descriptions[v['format']]}
- ტონი: {tone_descriptions[v['tone']]}
- ასაკობრივი ჯგუფი: {age_descriptions[v['age_group']]}
""")
        
        news_section = ""
        if news_context:
            news_section = f"""
📰 ბოლოდროინდელი ნიუსები რომელზეც შეიძლება რეაგირება:
{news_context}

შეგიძლია ამ ნიუსებზე დაფუძნებული კონტენტის შექმნა, მაგრამ არ არის სავალდებულო.
"""
        
        custom_style_notes = "\n".join(self.preferences.get('custom_edits', [])[-10:]) if self.preferences.get('custom_edits') else ""
        
        style_section = ""
        if custom_style_notes:
            style_section = f"""
💡 ნიკას სტილის ნოტები (შენი წინა რედაქტირებებიდან სწავლა):
{custom_style_notes}
"""
        
        prompt = f"""შენ ხარ ნიკა გაბლიშვილი - გამოცდილი ფსიქოკონსულტანტი მშობლებისთვის, ჰარვარდის უნივერსიტეტის კურსდამთავრებული, 20 წლიანი პრაქტიკით.

შენი ამოცანაა შექმნა TikTok კონტენტი ქართულ მშობლებისთვის. კონტენტი უნდა იყოს:
- პრაქტიკული და გამოსადეგი
- მეცნიერულად დასაბუთებული
- ადვილად გასაგები
- მოკლე და კონკრეტური (TikTok ფორმატი)

{news_section}

გენერირება უნდა გააკეთო შემდეგი {len(variants)} ვარიანტისთვის:
{''.join(variants_desc)}

{style_section}

ᲙᲠᲘᲢᲘᲙᲣᲚᲐᲓ ᲛᲜᲘᲨᲕᲜᲔᲚᲝᲕᲐᲜᲘ: 
1. ყოველთვის პასუხობ მხოლოდ და მხოლოდ VALID JSON ფორმატში
2. არ იყენებ markdown code blocks (```json)
3. არ იყენებ არანაირ დამატებით ტექსტს JSON-ის გარეთ

JSON სტრუქტურა:
{{
  "variants": [
    {{
      "format": "myth_vs_reality",
      "title": "მოკლე სათაური",
      "main_text": "ძირითადი ტექსტი რომელიც გამოჩნდება სურათზე (მაქსიმუმ 200 სიმბოლო)",
      "caption": "Instagram/TikTok caption - უფრო დეტალური ახსნა (მაქსიმუმ 500 სიმბოლო)",
      "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
      "visual_notes": "როგორ უნდა გამოიყურებოდეს ვიზუალურად - ფერები, ელემენტები"
    }}
  ]
}}

გაიხსენე: 
- ტექსტი უნდა იყოს ᲥᲐᲠᲗᲣᲚᲐᲓ
- მოკლე და კონკრეტული (TikTok vertical ფორმატი)
- ემოციურად რეზონანსული მშობლებისთვის
- პრაქტიკული - რაღაც რასაც დღესვე გამოიყენებენ

არ დაგავიწყდეს - მხოლოდ JSON, არაფერი სხვა!"""
        
        return prompt
    
    def regenerate_with_feedback(self, original_content, feedback_text):
        """Regenerate content based on user feedback"""
        
        prompt = f"""შენ ხარ ნიკა გაბლიშვილი - ფსიქოკონსულტანტი მშობლებისთვის.

წინა კონტენტი იყო:
{json.dumps(original_content, ensure_ascii=False, indent=2)}

მომხმარებლის feedback:
"{feedback_text}"

გთხოვ, შექმნა გაუმჯობესებული ვერსია მომხმარებლის კომენტარების გათვალისწინებით.

ᲙᲠᲘᲢᲘᲙᲣᲚᲐᲓ ᲛᲜᲘᲨᲕᲜᲔᲚᲝᲕᲐᲜᲘ:
- პასუხობ მხოლოდ VALID JSON ფორმატში
- არ იყენებ markdown (```json)
- არ იყენებ დამატებით ტექსტს

JSON სტრუქტურა:
{{
  "format": "...",
  "title": "...",
  "main_text": "...",
  "caption": "...",
  "hashtags": ["..."],
  "visual_notes": "..."
}}"""
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            response_text = response_text.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            print(f"Error regenerating content: {e}")
            return original_content
    
    def record_feedback(self, content, rating):
        """Record user feedback to improve future generations"""
        format_type = content.get('format')
        
        if rating in ['❤️', '👍']:
            # Positive feedback
            self.preferences['liked_formats'][format_type] = \
                self.preferences['liked_formats'].get(format_type, 0) + 1
        elif rating == '👎':
            # Negative feedback
            self.preferences['liked_formats'][format_type] = \
                self.preferences['liked_formats'].get(format_type, 0) - 1
        
        self.save_preferences()
    
    def add_custom_edit(self, edit_note):
        """Add a custom edit note to learn user's style"""
        if 'custom_edits' not in self.preferences:
            self.preferences['custom_edits'] = []
        
        self.preferences['custom_edits'].append(edit_note)
        
        # Keep only last 20 edits
        if len(self.preferences['custom_edits']) > 20:
            self.preferences['custom_edits'] = self.preferences['custom_edits'][-20:]
        
        self.save_preferences()
