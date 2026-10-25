#!/usr/bin/env python3
"""
Onion Run Game Launcher
Run this script to start the game.
"""

if __name__ == "__main__":
    import sys
    import os
    
    # Work from the project folder so config.xml and assets are found from any launch directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Add src directory to path so we can import modules
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    # Import and run the main game
    from main import main
    main()