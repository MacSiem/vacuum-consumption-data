"""Validate a downloaded intake packet without publishing or promoting it."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.contribution import validate_contribution


def check(path, root=ROOT):
    path = Path(path)
    if path.stat().st_size > 512 * 1024:
        raise ValueError('Intake packet exceeds 512 KiB')
    payload = json.loads(path.read_text(encoding='utf-8'))
    catalog = {}
    for model_path in (Path(root) / 'data' / 'models').glob('*.json'):
        model = json.loads(model_path.read_text(encoding='utf-8'))
        catalog[model['id']] = model
    return validate_contribution(payload, public_catalog=catalog)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    args = parser.parse_args()
    try:
        result = check(args.packet)
    except (ValueError, OSError, KeyError, TypeError):
        result = {'submission_eligible':False, 'runtime_eligible':False,
                  'review_needed':True, 'reason':'invalid_contribution'}
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result['submission_eligible'] else 1)
