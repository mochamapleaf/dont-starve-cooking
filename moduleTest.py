import yaml


if __name__ == "__main__":
    print(yaml.load("""
    - A
    - B
    - C
    """, Loader=yaml.FullLoader))