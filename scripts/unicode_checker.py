#!/usr/bin/env python3

import os
import sys
import unicodedata

EXTENDED_INVISIBLE = {

    "\u1680",  # ogham space mark
    "\uFEFF",  # zero-width no-break space / BOM

    # Unicode general spacing characters (expanded from U+2000–U+200A)
    "\u2000", "\u2001", "\u2002", "\u2003", "\u2004",
    "\u2005", "\u2006", "\u2007", "\u2008", "\u2009",
    "\u200A", 

    # Basic invisible and formatting marks
    "\u200B",  # ZERO WIDTH SPACE
    "\u200C",  # ZERO WIDTH NON-JOINER
    "\u200D",  # ZERO WIDTH JOINER
    "\u2060",  # WORD JOINER
    "\u00AD",  # SOFT HYPHEN (invisible until a line break)  
    "\u034F",  # COMBINING GRAPHEME JOINER  

    # Bidirectional and direction formatting marks (expanded)
    "\u200E",  # LEFT-TO-RIGHT MARK
    "\u200F",  # RIGHT-TO-LEFT MARK
    "\u202A",  # LEFT-TO-RIGHT EMBEDDING
    "\u202B",  # RIGHT-TO-LEFT EMBEDDING
    "\u202C",  # POP DIRECTIONAL FORMATTING
    "\u202D",  # LEFT-TO-RIGHT OVERRIDE
    "\u202E",  # RIGHT-TO-LEFT OVERRIDE
    "\u2066",  # LEFT-TO-RIGHT ISOLATE
    "\u2067",  # RIGHT-TO-LEFT ISOLATE
    "\u2068",  # FIRST STRONG ISOLATE
    "\u2069",  # POP DIRECTIONAL ISOLATE
    "\u206A",  # INHIBIT SYMMETRIC SWAPPING  
    "\u206B",  # ACTIVATE SYMMETRIC SWAPPING  
    "\u206C",  # INHIBIT ARABIC FORM SHAPING  
    "\u206D",  # ACTIVATE ARABIC FORM SHAPING  
    "\u206E",  # NATIONAL DIGIT SHAPES  
    "\u206F",  # NOMINAL DIGIT SHAPES  

    # Invisible math operators/separators (expanded)
    "\u2061",  # FUNCTION APPLICATION
    "\u2062",  # INVISIBLE TIMES
    "\u2063",  # INVISIBLE SEPARATOR
    "\u2064",  # INVISIBLE PLUS

    # Space characters of various widths (expanded)
    "\u00A0",  # NO-BREAK SPACE
    "\u202F",  # NARROW NO-BREAK SPACE
    "\u205F",  # MEDIUM MATHEMATICAL SPACE
    "\u3000",  # IDEOGRAPHIC SPACE

    # Other language/string fillers
    "\u180E",  # MONGOLIAN VOWEL SEPARATOR
    "\u2800",  # BRAILLE PATTERN BLANK
    "\u3164",  # HANGUL FILLER
    "\uFFA0",  # HALFWIDTH HANGUL FILLER

    # (Optional) Unicode special annotation or replacement characters
    "\uFFF9",  # INTERLINEAR ANNOTATION ANCHOR
    "\uFFFA",  # INTERLINEAR ANNOTATION SEPARATOR
    "\uFFFB",  # INTERLINEAR ANNOTATION TERMINATOR
}

# Existing categories already considered suspicious:
SUSPICIOUS_CATEGORIES = {
    "Cf",  # Format (e.g., zero-width, directional marks)
    "Cc",  # Controls
}

# BASIC_LATIN covers ASCII letters, digits, and standard punctuation.
BASIC_LATIN = set(chr(cp) for cp in range(0x0020, 0x007F + 1))

# LATIN_1_SUPPLEMENT covers additional Latin letters (e.g., accents)
LATIN_1_SUPPLEMENT = set(chr(cp) for cp in range(0x00A0, 0x00FF + 1))

# LATIN_EXTENDED_A covers letters like Ā, Œ, etc.
LATIN_EXTENDED_A = set(chr(cp) for cp in range(0x0100, 0x017F + 1))

# COMBINING_DIACRITICS allow letters formed with accents (e.g., é)
COMBINING_DIACRITICS = set(chr(cp) for cp in range(0x0300, 0x036F + 1))

# MERGE the allowed sets
ALLOWED_LATIN_FOR_DE_ENGLISH = (
    BASIC_LATIN
    | LATIN_1_SUPPLEMENT
    | LATIN_EXTENDED_A
    | COMBINING_DIACRITICS
    # (Optional) you can add additional Latin extended blocks if needed
)

def is_non_german_english(ch):
    return ch not in ALLOWED_LATIN_FOR_DE_ENGLISH

def is_allowed_char(ch):
    # ASCII printable range: space (0x20) through ~ (0x7E)  <-- allowed
    if 0x20 <= ord(ch) <= 0x7E:
        return True

    # extended Latin range often used in German/English text
    # e.g., accented vowels, cedillas, etc.
    if 0x00C0 <= ord(ch) <= 0x024F:  # Latin-1 Supplement + Latin Extended-A/B
        return True

    # additional punctuation and typographic symbols often used
    # e.g., en-dash, em-dash, smart quotes, ellipsis
    if ch in {
        "\u2013",  # en dash
        "\u2014",  # em dash
        "\u2018", "\u2019",  # smart single quotes
        "\u201C", "\u201D",  # smart double quotes
        "\u2026"  # ellipsis
    }:
        return True

    return False


def scan_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, start=1):
            for col, ch in enumerate(line, start=1):
                cat = unicodedata.category(ch)

                if ch in EXTENDED_INVISIBLE or cat in SUSPICIOUS_CATEGORIES:
                    name = unicodedata.name(ch, "<unknown>")
                    print(f"{file_path}:{lineno}:{col} U+{ord(ch):04X} {name} ({cat})")

                elif (is_non_german_english(ch) or not is_allowed_char(ch)) and not ch.isspace():
                    name = unicodedata.name(ch, "<non-Latin or unusual>")
                    print(f"{file_path}:{lineno}:{col} NON-ENG/GER U+{ord(ch):04X} {name} ({cat})")

def scan_directory(root_path):
    for root, dirs, files in os.walk(root_path):
        for filename in files:
            full_path = os.path.join(root, filename)
            scan_file(full_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path-to-folder-or-file>")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isdir(target):
        scan_directory(target)
    elif os.path.isfile(target):
        scan_file(target)
    else:
        print(f"Not file or directory: {target}")