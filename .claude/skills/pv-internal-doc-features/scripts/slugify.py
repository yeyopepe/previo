"""Calcula la parte de texto (slug) del nombre de fichero de una funcionalidad nueva --
el nombre de fichero final es '{numero}-{slug}.md'; el numero (ver next-feature-number.py)
es quien garantiza que no hay colision, este slug no necesita comprobar nada por si mismo.

Uso:
    python slugify.py "Nombre de la funcionalidad"
"""
import argparse

from _slug import slugify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("title")
    args = parser.parse_args()

    print(slugify(args.title) or "feature")


if __name__ == "__main__":
    main()
