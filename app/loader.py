import yaml

def load_config():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config

if __name__ == '__main__':
    config = load_config()
    print(config)