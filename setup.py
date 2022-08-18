from setuptools import setup, find_packages 

with open('README.md', 'r', encoding='UTF-8') as f:
    README_MD = f.read()

setup(
    name="autoliter",
    version="0.1.2",
    description=" Helps you manage your literature notes",
    long_description=README_MD,
    long_description_content_type='text/markdown',
    url="https://github.com/WilmerWang/autoLiterature",
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Markup",
    ],
    install_requires=["beautifulsoup4>=4.11.1", "feedparser>=6.0.10", 
                      "urllib3>=1.26.11","requests>=2.28.1", 
                      "tqdm>=4.64.0", "Unidecode>=1.3.4"],
    entry_points={
        "console_scripts": [
            "autoliter = autoliterature.autoliter:main",
        ]
    },
    packages=find_packages(),
    license="AGPLv3",
    author="Wilmer Wang",
    author_email="wangwei0206@foxmail.com",
    download_url="https://github.com/WilmerWang/autoLiterature/archive/refs/tags/v0.1.2.tar.gz",
    keywords=["bibtex", "arxiv", "doi", "science", "scientific-journals"],
)