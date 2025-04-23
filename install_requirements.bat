::******************************************************************************
:: File:        install_requirements.bat
:: Author:      Brennan Romero, Luke Delzer
:: Class:       Introduction to AI (CS3820), Spring 2025, Dr. Armin Moin
:: Assignment:  Semester Project
:: Due Date:    04-23-2025
:: Description: This script automates installing the requirements file
::              every time SB3 starts. This is required since SB3 is highly
::              dependent on having the updated requirements installed

:: Usage:       This program is automatically used by the SB3 environment
::              at startup and is not intended for use on its own.
::******************************************************************************
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu126