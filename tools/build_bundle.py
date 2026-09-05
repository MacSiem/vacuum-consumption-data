"""Deterministic data-only package. Hash verifies integrity, not publisher authenticity."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from tools.validate import ROOT, canonical, load_records, validate_dataset

def build(records, version='0.2.0', source_revision='uncommitted', schema_version=2):
    validate_dataset(records)
    if schema_version not in (1,2):raise ValueError('Incompatible bundle schema/version')
    if schema_version==1 and any(r['kind']=='estimate' for r in records):raise ValueError('V1 bundle cannot carry estimates')
    records=[r for r in records if r['kind']!='profile' or r['review']['status']=='approved']
    payload={'schema_version':schema_version,'dataset_version':version,'source_revision':source_revision,'records':sorted(records,key=lambda r:r['id'])}
    digest=hashlib.sha256(canonical(payload)).hexdigest()
    return {'manifest':{'schema_version':schema_version,'dataset_version':version,'payload_sha256':digest,'record_count':len(records)},'payload':payload}

def verify(bundle):
    if set(bundle)!={'manifest','payload'}:raise ValueError('Unknown bundle fields')
    manifest=bundle['manifest'];payload=bundle['payload']
    if set(manifest)!={'schema_version','dataset_version','payload_sha256','record_count'} or set(payload)!={'schema_version','dataset_version','source_revision','records'}:raise ValueError('Unknown manifest/payload fields')
    if manifest['schema_version'] not in (1,2) or payload['schema_version']!=manifest['schema_version'] or manifest['dataset_version']!=payload['dataset_version']:raise ValueError('Incompatible bundle schema/version')
    if manifest['payload_sha256']!=hashlib.sha256(canonical(payload)).hexdigest() or manifest['record_count']!=len(payload['records']):raise ValueError('Bundle integrity mismatch')
    validate_dataset(payload['records'])
    if any(r['kind']=='profile' and r['review']['status']!='approved' for r in payload['records']):raise ValueError('Non-approved profile in runtime bundle')
    return payload

def migrate_v1_bundle(bundle):
    """Deterministically repackage a verified V1 payload as V2; it adds no data."""
    payload=verify(bundle)
    if payload['schema_version']!=1:raise ValueError('Only V1 bundle can be migrated')
    return build(payload['records'],version=payload['dataset_version'],source_revision=payload['source_revision'],schema_version=2)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='dist/consumption-data.json');args=parser.parse_args()
    revision=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
    if subprocess.run(['git','diff','--quiet','HEAD'],cwd=ROOT).returncode:revision+='-dirty'
    bundle=build(load_records(),source_revision=revision);verify(bundle)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(canonical(bundle)+b'\n')
    print(json.dumps(bundle['manifest']))
