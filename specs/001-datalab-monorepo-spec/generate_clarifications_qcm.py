#!/usr/bin/env python3
"""
Génère une image de tableur QCM pour les clarifications de spécification.
Les cases peuvent être cochées directement dans l'image générée.

Usage:
    python generate_clarifications_qcm.py [--output nom_fichier.png]
"""

import argparse
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Installation de Pillow requise: pip install Pillow")
    exit(1)


# Configuration des couleurs
COLORS = {
    "background": "#FFFFFF",
    "header_bg": "#2C3E50",
    "header_text": "#FFFFFF",
    "row_even": "#F8F9FA",
    "row_odd": "#FFFFFF",
    "border": "#BDC3C7",
    "text": "#2C3E50",
    "checkbox_border": "#34495E",
    "checkbox_bg": "#FFFFFF",
    "recommended": "#27AE60",
    "question_bg": "#EBF5FB",
}

# Données des clarifications identifiées
CLARIFICATIONS = [
    {
        "id": "Q1",
        "category": "Data Retention",
        "question": "Durée de rétention des données collectées?",
        "recommended": "B",
        "options": [
            ("A", "7 jours (dev/test)"),
            ("B", "30 jours (standard)"),
            ("C", "90 jours (analyse longue)"),
            ("D", "Illimité (archivage)"),
        ],
    },
    {
        "id": "Q2",
        "category": "Buffer Size",
        "question": "Taille maximale du buffer en mémoire?",
        "recommended": "B",
        "options": [
            ("A", "1,000 ticks (~1MB)"),
            ("B", "10,000 ticks (~10MB)"),
            ("C", "100,000 ticks (~100MB)"),
            ("D", "Personnalisé"),
        ],
    },
    {
        "id": "Q3",
        "category": "Logging Strategy",
        "question": "Niveau de logging par défaut?",
        "recommended": "B",
        "options": [
            ("A", "ERROR seulement"),
            ("B", "INFO + métriques"),
            ("C", "DEBUG complet"),
            ("D", "Configurable runtime"),
        ],
    },
    {
        "id": "Q4",
        "category": "API Failure",
        "question": "Comportement lors d'échec WebSocket?",
        "recommended": "C",
        "options": [
            ("A", "Abandon immédiat"),
            ("B", "3 retries puis abandon"),
            ("C", "Retry infini + backoff"),
            ("D", "Fallback REST API"),
        ],
    },
    {
        "id": "Q5",
        "category": "Data Privacy",
        "question": "Données sensibles à protéger?",
        "recommended": "A",
        "options": [
            ("A", "Aucune (données publiques)"),
            ("B", "Clés API uniquement"),
            ("C", "Positions + stratégies"),
            ("D", "Tout chiffré au repos"),
        ],
    },
]


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Retourne une police avec la taille spécifiée."""
    font_names = [
        "arial.ttf",
        "Arial.ttf",
        "DejaVuSans.ttf",
        "FreeSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]

    if bold:
        font_names = [
            "arialbd.ttf",
            "Arial Bold.ttf",
            "DejaVuSans-Bold.ttf",
            "FreeSansBold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ] + font_names

    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, size)
        except (OSError, IOError):
            continue

    # Fallback to default
    return ImageFont.load_default()


def draw_checkbox(draw: ImageDraw.Draw, x: int, y: int, size: int = 16, checked: bool = False):
    """Dessine une case à cocher."""
    draw.rectangle(
        [x, y, x + size, y + size],
        fill=COLORS["checkbox_bg"],
        outline=COLORS["checkbox_border"],
        width=2,
    )
    if checked:
        # Dessine une coche
        draw.line([(x + 3, y + size // 2), (x + size // 3, y + size - 4)], fill=COLORS["recommended"], width=2)
        draw.line([(x + size // 3, y + size - 4), (x + size - 3, y + 4)], fill=COLORS["recommended"], width=2)


def generate_qcm_image(output_path: str = "clarifications_qcm.png"):
    """Génère l'image du tableur QCM."""

    # Dimensions
    col_widths = [60, 140, 300, 180, 180, 180, 180]  # ID, Category, Question, Opt A, B, C, D
    row_height = 50
    header_height = 45
    padding = 10
    checkbox_size = 18

    total_width = sum(col_widths) + padding * 2
    total_height = header_height + (len(CLARIFICATIONS) * row_height) + padding * 2 + 80  # +80 for title and footer

    # Création de l'image
    img = Image.new("RGB", (total_width, total_height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    # Polices
    font_title = get_font(20, bold=True)
    font_header = get_font(12, bold=True)
    font_cell = get_font(11)
    font_small = get_font(9)
    font_footer = get_font(10)

    # Titre
    title = "DataLab - Clarifications de Spécification (QCM)"
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_x = (total_width - (title_bbox[2] - title_bbox[0])) // 2
    draw.text((title_x, padding), title, fill=COLORS["text"], font=font_title)

    # Position de départ du tableau
    table_y = padding + 35

    # En-têtes
    headers = ["ID", "Catégorie", "Question", "Option A", "Option B", "Option C", "Option D"]
    x = padding
    for i, (header, width) in enumerate(zip(headers, col_widths)):
        draw.rectangle([x, table_y, x + width, table_y + header_height], fill=COLORS["header_bg"], outline=COLORS["border"])

        # Centrer le texte
        text_bbox = draw.textbbox((0, 0), header, font=font_header)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = x + (width - text_width) // 2
        text_y = table_y + (header_height - (text_bbox[3] - text_bbox[1])) // 2
        draw.text((text_x, text_y), header, fill=COLORS["header_text"], font=font_header)
        x += width

    # Lignes de données
    y = table_y + header_height
    for row_idx, clarif in enumerate(CLARIFICATIONS):
        bg_color = COLORS["row_even"] if row_idx % 2 == 0 else COLORS["row_odd"]
        x = padding

        # Cellules
        cells = [
            clarif["id"],
            clarif["category"],
            clarif["question"],
        ]

        # Dessiner les 3 premières colonnes (ID, Category, Question)
        for col_idx, (cell, width) in enumerate(zip(cells, col_widths[:3])):
            cell_bg = COLORS["question_bg"] if col_idx == 2 else bg_color
            draw.rectangle([x, y, x + width, y + row_height], fill=cell_bg, outline=COLORS["border"])

            # Texte
            text_bbox = draw.textbbox((0, 0), cell, font=font_cell)
            text_y = y + (row_height - (text_bbox[3] - text_bbox[1])) // 2

            if col_idx == 2:  # Question - aligné à gauche
                draw.text((x + 8, text_y), cell, fill=COLORS["text"], font=font_cell)
            else:  # Centré
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x + (width - text_width) // 2
                draw.text((text_x, text_y), cell, fill=COLORS["text"], font=font_cell)
            x += width

        # Dessiner les colonnes d'options (A, B, C, D)
        for opt_idx, (opt_letter, opt_text) in enumerate(clarif["options"]):
            width = col_widths[3 + opt_idx]
            is_recommended = opt_letter == clarif["recommended"]

            cell_bg = bg_color
            if is_recommended:
                cell_bg = "#E8F8F5"  # Vert clair pour recommandé

            draw.rectangle([x, y, x + width, y + row_height], fill=cell_bg, outline=COLORS["border"])

            # Checkbox
            checkbox_x = x + 8
            checkbox_y = y + (row_height - checkbox_size) // 2
            draw_checkbox(draw, checkbox_x, checkbox_y, checkbox_size, checked=False)

            # Texte de l'option
            text_x = checkbox_x + checkbox_size + 6

            # Indicateur recommandé
            if is_recommended:
                rec_text = "[REC]"
                draw.text((text_x, y + 5), rec_text, fill=COLORS["recommended"], font=font_small)
                text_y_opt = y + 18
            else:
                text_y_opt = y + (row_height - 24) // 2

            # Texte de l'option (peut être sur 2 lignes)
            max_text_width = width - checkbox_size - 20
            words = opt_text.split()
            lines = []
            current_line = ""

            for word in words:
                test_line = f"{current_line} {word}".strip()
                test_bbox = draw.textbbox((0, 0), test_line, font=font_small)
                if test_bbox[2] - test_bbox[0] <= max_text_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            for line_idx, line in enumerate(lines[:2]):  # Max 2 lignes
                draw.text((text_x, text_y_opt + line_idx * 14), line, fill=COLORS["text"], font=font_small)

            x += width

        y += row_height

    # Pied de page avec instructions
    footer_y = y + 15
    footer_text = "Instructions: Cochez les cases correspondant à vos choix. [REC] = Option recommandée"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    footer_x = (total_width - (footer_bbox[2] - footer_bbox[0])) // 2
    draw.text((footer_x, footer_y), footer_text, fill=COLORS["text"], font=font_footer)

    # Date
    from datetime import datetime
    date_text = f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    draw.text((padding, footer_y + 20), date_text, fill=COLORS["border"], font=font_small)

    # Sauvegarde
    img.save(output_path, "PNG", quality=95)
    print(f"Image QCM générée: {output_path}")
    print(f"Dimensions: {total_width}x{total_height} pixels")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Génère une image de tableur QCM pour les clarifications de spécification"
    )
    parser.add_argument(
        "--output", "-o",
        default="clarifications_qcm.png",
        help="Nom du fichier de sortie (défaut: clarifications_qcm.png)"
    )

    args = parser.parse_args()

    # Déterminer le chemin de sortie
    script_dir = Path(__file__).parent
    output_path = script_dir / args.output

    generate_qcm_image(str(output_path))

    print("\nClarifications incluses:")
    for c in CLARIFICATIONS:
        print(f"  {c['id']}: {c['question']}")
        print(f"      Recommandé: Option {c['recommended']}")


if __name__ == "__main__":
    main()
