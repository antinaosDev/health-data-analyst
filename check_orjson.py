import orjson
import plotly
import sys

print("Python version:", sys.version)
print("orjson version:", getattr(orjson, '__version__', 'unknown'))
print("plotly version:", getattr(plotly, '__version__', 'unknown'))

try:
    print("OPT_NON_STR_KEYS available:", hasattr(orjson, 'OPT_NON_STR_KEYS'))
except Exception as e:
    print("Error checking attr:", e)
