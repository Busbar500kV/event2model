import argparse
import yaml
from analyze import run_analysis
from report import write_report

def main(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    results = run_analysis(cfg)
    write_report(cfg, results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    main(args.config)