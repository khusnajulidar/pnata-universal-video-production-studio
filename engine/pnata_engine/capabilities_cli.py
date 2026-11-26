import json
from .capabilities import detect_capabilities

def main():
    print(json.dumps(detect_capabilities(), indent=2))

if __name__ == "__main__": main()
