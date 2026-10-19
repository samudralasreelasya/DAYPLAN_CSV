import os
import sys

# Make "from services import ..." work no matter where pytest is launched from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))