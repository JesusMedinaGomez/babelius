from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

def generate_default_book_image(title, width=400, height=600, bg_color="#1F2937", text_color="#FFD700"):
    """
    Genera una imagen de portada por defecto para un libro.
    
    Args:
        title (str): Título del libro
        width (int): Ancho de la imagen
        height (int): Alto de la imagen
        bg_color (str): Color de fondo en hexadecimal
        text_color (str): Color del texto en hexadecimal
    
    Returns:
        ContentFile: Archivo de imagen listo para guardar
    """
    try:
        # Crear imagen con fondo
        image = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(image)

        # Intentar cargar fuentes (con fallbacks)
        font_size = 30
        try:
            # Intentar con fuentes comunes
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", font_size)
            except IOError:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                except IOError:
                    # Fallback a fuente básica
                    font = ImageFont.load_default()

        # Dividir título en líneas que quepan en el ancho
        lines = []
        words = title.split()
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            # Medir el texto
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width > width - 40:  # 40px de margen
                if current_line:  # Si ya hay texto en la línea actual
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)

        # Calcular altura total del texto
        line_height = 40  # Altura aproximada por línea
        total_text_height = len(lines) * line_height
        start_y = (height - total_text_height) // 2

        # Dibujar cada línea centrada
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = start_y + (i * line_height)
            
            draw.text((x, y), line, font=font, fill=text_color)

        # Convertir a ContentFile
        buffer = BytesIO()
        image.save(buffer, format="PNG", quality=95)
        buffer.seek(0)
        
        return ContentFile(buffer.getvalue(), name=f"default_cover.png")
        
    except Exception as e:
        print(f"Error en generate_default_book_image: {e}")
        return None

LANGUAGES_ES = [
    ('af', 'Afrikáans'),
    ('sq', 'Albanés'),
    ('am', 'Amárico'),
    ('ar', 'Árabe'),
    ('hy', 'Armenio'),
    ('az', 'Azerí'),
    ('eu', 'Vasco'),
    ('be', 'Bielorruso'),
    ('bn', 'Bengalí'),
    ('bs', 'Bosnio'),
    ('bg', 'Búlgaro'),
    ('ca', 'Catalán'),
    ('ceb', 'Cebuano'),
    ('zh-hans', 'Chino simplificado'),
    ('zh-hant', 'Chino tradicional'),
    ('hr', 'Croata'),
    ('cs', 'Checo'),
    ('da', 'Danés'),
    ('nl', 'Neerlandés'),
    ('en', 'Inglés'),
    ('eo', 'Esperanto'),
    ('et', 'Estonio'),
    ('fi', 'Finés'),
    ('fr', 'Francés'),
    ('gl', 'Gallego'),
    ('ka', 'Georgiano'),
    ('de', 'Alemán'),
    ('el', 'Griego'),
    ('gu', 'Guyaratí'),
    ('ht', 'Criollo haitiano'),
    ('ha', 'Hausa'),
    ('haw', 'Hawaiano'),
    ('he', 'Hebreo'),
    ('hi', 'Hindi'),
    ('hu', 'Húngaro'),
    ('is', 'Islandés'),
    ('id', 'Indonesio'),
    ('ga', 'Irlandés'),
    ('it', 'Italiano'),
    ('ja', 'Japonés'),
    ('jv', 'Javanés'),
    ('kn', 'Canarés'),
    ('kk', 'Kazajo'),
    ('km', 'Jemer'),
    ('ko', 'Coreano'),
    ('ku', 'Kurdo'),
    ('ky', 'Kirguís'),
    ('lo', 'Lao'),
    ('la', 'Latín'),
    ('lv', 'Letón'),
    ('lt', 'Lituano'),
    ('lb', 'Luxemburgués'),
    ('mk', 'Macedonio'),
    ('mg', 'Malgache'),
    ('ms', 'Malayo'),
    ('ml', 'Malayalam'),
    ('mt', 'Maltés'),
    ('mi', 'Maorí'),
    ('mr', 'Maratí'),
    ('mn', 'Mongol'),
    ('ne', 'Nepalí'),
    ('no', 'Noruego'),
    ('ny', 'Chichewa'),
    ('fa', 'Persa'),
    ('pl', 'Polaco'),
    ('pt', 'Portugués'),
    ('pa', 'Punyabí'),
    ('ro', 'Rumano'),
    ('ru', 'Ruso'),
    ('sm', 'Samoano'),
    ('gd', 'Gaélico escocés'),
    ('sr', 'Serbio'),
    ('st', 'Sesotho'),
    ('sn', 'Shona'),
    ('sd', 'Sindhi'),
    ('si', 'Cingalés'),
    ('sk', 'Eslovaco'),
    ('sl', 'Esloveno'),
    ('so', 'Somalí'),
    ('es', 'Español'),
    ('su', 'Sundanés'),
    ('sw', 'Suajili'),
    ('sv', 'Sueco'),
    ('tl', 'Tagalo'),
    ('tg', 'Tayiko'),
    ('ta', 'Tamil'),
    ('te', 'Telugu'),
    ('th', 'Tailandés'),
    ('tr', 'Turco'),
    ('uk', 'Ucraniano'),
    ('ur', 'Urdu'),
    ('uz', 'Uzbeko'),
    ('vi', 'Vietnamita'),
    ('cy', 'Galés'),
    ('xh', 'Xhosa'),
    ('yi', 'Yidis'),
    ('yo', 'Yoruba'),
    ('zu', 'Zulú'),
]
