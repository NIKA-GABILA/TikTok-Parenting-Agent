"""
Design Generator - Creates beautiful TikTok images using Pillow
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os
import config
import textwrap

class DesignGenerator:
    def __init__(self):
        self.width = config.IMAGE_WIDTH
        self.height = config.IMAGE_HEIGHT
        self.load_fonts()
    
    def load_fonts(self):
        """Load Georgian fonts"""
        self.fonts = {}
        font_sizes = {
            'title': 80,
            'main': 60,
            'caption': 45,
            'small': 35,
            'branding': 28
        }
        
        # Try to load system fonts
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        ]
        
        for size_name, size in font_sizes.items():
            loaded = False
            for font_path in font_paths:
                try:
                    if 'Bold' in font_path and size_name in ['title', 'main']:
                        self.fonts[size_name] = ImageFont.truetype(font_path, size)
                        loaded = True
                        break
                    elif 'Bold' not in font_path:
                        self.fonts[size_name] = ImageFont.truetype(font_path, size)
                        loaded = True
                        break
                except:
                    continue
            
            if not loaded:
                # Fallback to default font
                self.fonts[size_name] = ImageFont.load_default()
    
    def generate_image(self, content, style=None):
        """Generate image based on content and style"""
        if style is None:
            style = random.choices(
                list(config.VISUAL_STYLE_DISTRIBUTION.keys()),
                weights=list(config.VISUAL_STYLE_DISTRIBUTION.values())
            )[0]
        
        # Create base image
        if style == 'minimalist':
            return self._create_minimalist(content)
        elif style == 'warm_cozy':
            return self._create_warm_cozy(content)
        elif style == 'infographic':
            return self._create_infographic(content)
        elif style == 'gradient':
            return self._create_gradient(content)
        elif style == 'story_card':
            return self._create_story_card(content)
        else:
            return self._create_minimalist(content)
    
    def _create_minimalist(self, content):
        """Create minimalist clean design"""
        img = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(img)
        
        colors = config.COLOR_PALETTES['minimalist']
        accent_color = colors[2]  # Blue accent
        text_color = colors[1]    # Dark text
        
        # Add subtle top decoration
        draw.rectangle([(0, 0), (self.width, 40)], fill=accent_color)
        
        # Title
        title = content.get('title', '')
        if title:
            y_pos = 200
            wrapped_title = self._wrap_text(title, self.fonts['title'], self.width - 200)
            for line in wrapped_title:
                bbox = draw.textbbox((0, 0), line, font=self.fonts['title'])
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                draw.text((x, y_pos), line, fill=text_color, font=self.fonts['title'])
                y_pos += 100
        
        # Main text
        main_text = content.get('main_text', '')
        y_pos += 100
        wrapped_main = self._wrap_text(main_text, self.fonts['main'], self.width - 200)
        for line in wrapped_main:
            bbox = draw.textbbox((0, 0), line, font=self.fonts['main'])
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y_pos), line, fill=text_color, font=self.fonts['main'])
            y_pos += 80
        
        # Branding at bottom
        self._add_branding(draw, img)
        
        return img
    
    def _create_warm_cozy(self, content):
        """Create warm and cozy design with pastels"""
        colors = config.COLOR_PALETTES['warm_cozy']
        
        # Gradient background
        img = self._create_vertical_gradient(colors[0], colors[1])
        draw = ImageDraw.Draw(img)
        
        text_color = colors[3]  # Warm orange/red
        
        # Decorative rounded rectangle
        margin = 100
        rect_coords = [margin, 300, self.width - margin, self.height - 400]
        self._draw_rounded_rectangle(draw, rect_coords, colors[2], radius=50)
        
        # Title
        title = content.get('title', '')
        if title:
            y_pos = 400
            wrapped_title = self._wrap_text(title, self.fonts['title'], self.width - 300)
            for line in wrapped_title:
                bbox = draw.textbbox((0, 0), line, font=self.fonts['title'])
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                draw.text((x, y_pos), line, fill=text_color, font=self.fonts['title'])
                y_pos += 100
        
        # Main text
        main_text = content.get('main_text', '')
        y_pos += 80
        wrapped_main = self._wrap_text(main_text, self.fonts['main'], self.width - 300)
        for line in wrapped_main:
            bbox = draw.textbbox((0, 0), line, font=self.fonts['main'])
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y_pos), line, fill=text_color, font=self.fonts['main'])
            y_pos += 75
        
        # Branding
        self._add_branding(draw, img)
        
        return img
    
    def _create_infographic(self, content):
        """Create infographic style"""
        colors = config.COLOR_PALETTES['infographic']
        img = Image.new('RGB', (self.width, self.height), color=colors[0])
        draw = ImageDraw.Draw(img)
        
        # Header bar
        draw.rectangle([(0, 0), (self.width, 200)], fill=colors[1])
        
        # Title in header
        title = content.get('title', '')
        if title:
            wrapped_title = self._wrap_text(title, self.fonts['title'], self.width - 100)
            y_pos = 60
            for line in wrapped_title:
                bbox = draw.textbbox((0, 0), line, font=self.fonts['title'])
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                draw.text((x, y_pos), line, fill='white', font=self.fonts['title'])
                y_pos += 90
        
        # Main content in boxes
        y_pos = 350
        main_text = content.get('main_text', '')
        
        # Split by newlines or sentences for bullet points
        lines = main_text.split('\n') if '\n' in main_text else [main_text]
        
        for idx, line in enumerate(lines[:5]):  # Max 5 points
            if not line.strip():
                continue
            
            # Circle bullet
            circle_x = 150
            draw.ellipse([(circle_x - 25, y_pos - 25), (circle_x + 25, y_pos + 25)], 
                        fill=colors[2])
            
            # Text
            wrapped_line = self._wrap_text(line, self.fonts['main'], self.width - 300)
            line_y = y_pos - 20
            for wrapped in wrapped_line:
                draw.text((220, line_y), wrapped, fill=colors[1], font=self.fonts['main'])
                line_y += 70
            
            y_pos += len(wrapped_line) * 70 + 50
        
        # Branding
        self._add_branding(draw, img)
        
        return img
    
    def _create_gradient(self, content):
        """Create modern gradient design"""
        colors = config.COLOR_PALETTES['gradient']
        
        # Diagonal gradient
        img = self._create_diagonal_gradient(colors[0], colors[1])
        
        # Add semi-transparent overlay
        overlay = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 100))
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        
        draw = ImageDraw.Draw(img)
        
        # Title
        title = content.get('title', '')
        if title:
            y_pos = 300
            wrapped_title = self._wrap_text(title, self.fonts['title'], self.width - 200)
            for line in wrapped_title:
                # Text shadow
                bbox = draw.textbbox((0, 0), line, font=self.fonts['title'])
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                draw.text((x+3, y_pos+3), line, fill=(0, 0, 0, 100), font=self.fonts['title'])
                draw.text((x, y_pos), line, fill='white', font=self.fonts['title'])
                y_pos += 100
        
        # Main text
        main_text = content.get('main_text', '')
        y_pos += 100
        wrapped_main = self._wrap_text(main_text, self.fonts['main'], self.width - 200)
        for line in wrapped_main:
            bbox = draw.textbbox((0, 0), line, font=self.fonts['main'])
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x+2, y_pos+2), line, fill=(0, 0, 0, 100), font=self.fonts['main'])
            draw.text((x, y_pos), line, fill='white', font=self.fonts['main'])
            y_pos += 75
        
        img = img.convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # Branding
        self._add_branding(draw, img)
        
        return img
    
    def _create_story_card(self, content):
        """Create story card style"""
        colors = config.COLOR_PALETTES['story_card']
        img = Image.new('RGB', (self.width, self.height), color=colors[0])
        draw = ImageDraw.Draw(img)
        
        # Large rounded card in center
        card_margin = 80
        card_coords = [card_margin, 250, self.width - card_margin, self.height - 350]
        self._draw_rounded_rectangle(draw, card_coords, 'white', radius=60)
        
        # Add shadow effect
        shadow_coords = [card_margin + 10, 260, self.width - card_margin + 10, self.height - 340]
        self._draw_rounded_rectangle(draw, shadow_coords, colors[2], radius=60)
        
        # Re-draw card on top
        self._draw_rounded_rectangle(draw, card_coords, 'white', radius=60)
        
        # Title
        title = content.get('title', '')
        if title:
            y_pos = 350
            wrapped_title = self._wrap_text(title, self.fonts['title'], self.width - 300)
            for line in wrapped_title:
                bbox = draw.textbbox((0, 0), line, font=self.fonts['title'])
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                draw.text((x, y_pos), line, fill=colors[3], font=self.fonts['title'])
                y_pos += 95
        
        # Main text
        main_text = content.get('main_text', '')
        y_pos += 60
        wrapped_main = self._wrap_text(main_text, self.fonts['main'], self.width - 280)
        for line in wrapped_main:
            bbox = draw.textbbox((0, 0), line, font=self.fonts['main'])
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y_pos), line, fill='#333333', font=self.fonts['main'])
            y_pos += 70
        
        # Branding
        self._add_branding(draw, img)
        
        return img
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        lines = []
        words = text.split()
        
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _add_branding(self, draw, img):
        """Add branding watermark"""
        branding_text = config.BRANDING
        
        # At bottom
        y_pos = self.height - 120
        
        # Semi-transparent background
        bbox = draw.textbbox((0, y_pos - 20), branding_text, font=self.fonts['branding'])
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        
        # Draw semi-transparent rectangle
        padding = 20
        draw.rectangle([
            (x - padding, y_pos - 30),
            (x + text_width + padding, y_pos + 50)
        ], fill=(255, 255, 255, 200))
        
        # Draw text
        draw.text((x, y_pos), branding_text, fill='#2C3E50', font=self.fonts['branding'])
    
    def _draw_rounded_rectangle(self, draw, coords, fill, radius=20):
        """Draw rectangle with rounded corners"""
        x1, y1, x2, y2 = coords
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
        draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
        draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
        draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)
    
    def _create_vertical_gradient(self, color1, color2):
        """Create vertical gradient"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Parse hex colors
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        for y in range(self.height):
            ratio = y / self.height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return img
    
    def _create_diagonal_gradient(self, color1, color2):
        """Create diagonal gradient"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        max_distance = (self.width ** 2 + self.height ** 2) ** 0.5
        
        for y in range(self.height):
            for x in range(self.width):
                distance = (x ** 2 + y ** 2) ** 0.5
                ratio = distance / max_distance
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
                draw.point((x, y), fill=(r, g, b))
        
        return img
    
    def save_image(self, img, filename):
        """Save image to file"""
        os.makedirs(config.GENERATED_DIR, exist_ok=True)
        filepath = os.path.join(config.GENERATED_DIR, filename)
        img.save(filepath, config.IMAGE_FORMAT, quality=config.IMAGE_QUALITY)
        return filepath
