"""Deterministic data-only package. Hash verifies integrity, not publisher authenticity."""
import argparse
import hashlib
import json
from pathlib import Path
from tools.validate import ROOT, canonical, load_records, validate_dataset

def build(records, version='0.1.0'):
    validate_dataset(records)
    records=[r for r in records if r['kind']!='profile' or r['review']['status']=='approved']
    payload={'schema_version':1,'dataset_version':version,'records':sorted(records,key=lambda r:r['id'])}
    digest=hashlib.sha256(canonical(payload)).hexdigest()
    return {'manifest':{'schema_version':1,'dataset_version':version,'payload_sha256':digest,'record_count':len(records)},'payload':payload}

def verify(bundle):
    if set(bundle)!={'manifest','payload'}:raise ValueError('Unknown bundle fields')
    manifest=bundle['manifest'];payload=bundle['payload']
    if set(manifest)!={'schema_version','dataset_version','payload_sha256','record_count'} or set(payload)!={'schema_version','dataset_version','records'}:raise ValueError('Unknown manifest/payload fields')
    if manifest['schema_version']!=1 or payload['schema_version']!=1 or manifest['dataset_version']!=payload['dataset_version']:raise ValueError('Incompatible bundle schema/version')
    if manifest['payload_sha256']!=hashlib.sha256(canonical(payload)).hexdigest() or manifest['record_count']!=len(payload['records']):raise ValueError('Bundle integrity mismatch')
    validate_dataset(payload['records'])
    if any(r['kind']=='profile' and r['review']['status']!='approved' for r in payload['records']):raise ValueError('Non-approved profile in runtime bundle')
    return payload

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='dist/consumption-data.json');args=parser.parse_args()
    bundle=build(load_records());verify(bundle)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(canonical(bundle)+b'\n')
    print(json.dumps(bundle['manifest']))
