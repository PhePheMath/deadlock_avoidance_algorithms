import sys
from bankeiro_compiler import bankeiro

def main():
    for source in sys.argv[1:]:
        try:
            text = open(source).read()
            system = bankeiro()
            system.get_info(text)
            while True:
                if not system.run_banker_s_algorithm():
                    break
        except FileNotFoundError as FNFE:
            print('Source: ', FNFE)

if __name__ == "__main__":
    main()