from setuptools import setup
import os
import subprocess

def download_spacy_models():
    print("Installing SpaCy language models...")

    models = [
        "de_core_news_sm",
        "en_core_web_sm",
        "fr_core_news_sm"
    ]

    for model in models:
        subprocess.check_call([os.sys.executable, "-m", "spacy", "download", model])
        print(f"Model {model} installed successfully.")

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="SmartPDFManager",
    version="1.0",
    description="A smart tool for organizing PDFs based on language models.",
    install_requires=requirements,
    setup_requires=["spacy"],
    packages=["smart_pdf_manager"],
    include_package_data=True,
    zip_safe=False,
    cmdclass={'install': download_spacy_models},
)
