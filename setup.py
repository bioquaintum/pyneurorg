# setup.py

import setuptools
import os

# --- Define the version directly for the first release ---
# For subsequent releases, consider reading from src/pyneurorg/__init__.py
# to keep it as the single source of truth.
current_version = "0.1.19"

# --- Get the long description from the README file ---
# Assumes README.md is in the same directory as setup.py
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme_path, "r", encoding="utf-8") as fh:
    long_description = fh.read()

# --- Read dependencies from requirements.txt ---
# Ensures setup.py and requirements.txt are synchronized for runtime dependencies.
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
install_requires = []
if os.path.exists(requirements_path):
    with open(requirements_path, 'r', encoding='utf-8') as f:
        install_requires = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    print("Warning: requirements.txt not found. Using a default list of core dependencies for setup.")
    # Fallback if requirements.txt is missing (not ideal for a release)
    install_requires = [
        "brian2>=2.5",
        "numpy>=1.20",
        "matplotlib>=3.4",
        "scipy>=1.7",
        "networkx>=2.6",
    ]

# --- Optional dependencies (for development, testing, documentation) ---
extras_require = {
    "dev": [
        "pytest>=6.0",
        "flake8>=3.9",
        "black>=21.0b0",
        "ipykernel", # For running example notebooks
        "jupyterlab",
        # Add other dependencies from 'requirements-dev.txt' here if desired
        # or instruct users to install them separately.
    ],
    "docs": [
        "sphinx>=4.0",
        "sphinx-rtd-theme>=1.0",
        "nbsphinx>=0.8",
        "ipykernel", # nbsphinx needs this to execute notebooks
    ],
    "test": [
        "pytest>=6.0",
    ]
}
extras_require["all_extras"] = sum(extras_require.values(), [])

# Debug: check what packages are found
# This will look inside the 'src' directory for the 'pyneurorg' package.
print(f"DEBUG: Packages found by find_packages(where='src'): {setuptools.find_packages(where='src', exclude=['tests*', 'examples*', 'docs*'])}")


setuptools.setup(
    name="pyneurorg",  # Package name as it will appear on PyPI
    version=current_version,
    author="Luciano Silva/Bioquaintum Research & Development", # REPLACE
    author_email="luciano.silva@bioquaintum.io", # REPLACE
    description="Python Brain Organoid Simulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your_username/pyneurorg",  # URL of your GitHub repository (REPLACE)
    project_urls={ # Additional useful URLs
        "Bug Tracker": "https://github.com/bioquaintum/pyneurorg/issues", # REPLACE
        "Documentation": "https://pyneurorg.readthedocs.io/", # REPLACE (e.g., ReadTheDocs URL)
        "Source Code": "https://github.com/bioquaintum/pyneurorg", # REPLACE
    },
    # package_dir tells setuptools that the package code (for the import name 'pyneurorg')
    # is located in the 'src/' directory. The empty string key '' means
    # "the root package and all its subpackages".
    package_dir={'': 'src'},
    # packages finds all packages within the directory specified by package_dir's value for ''.
    # So, it will look inside 'src/' for a directory named 'pyneurorg' (and its sub-packages).
    packages=setuptools.find_packages(
        where='src', # Look for packages inside the 'src/' directory
        exclude=['tests*', 'examples*', 'docs*'] # Exclude non-package directories from src/ if any
                                                # (though usually tests/examples/docs are outside src/)
    ),
    classifiers=[
        "Development Status :: 3 - Alpha",  # Appropriate for v0.1.0
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",  # REPLACE with your actual license
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Natural Language :: English",
    ],
    python_requires='>=3.7',
    install_requires=install_requires,
    extras_require=extras_require,
    keywords="brain organoid neuronal simulation brian2 computational neuroscience",
)
