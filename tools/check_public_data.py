"""Reject recognizable private identifiers/secrets in the public JSON tree.

This is a conservative leak check, not a guarantee that free text is anonymous.
Manual review and contributor consent remain required.
"""
import ipaddress
import json
import re
from pathlib import Path
from tools.validate import ROOT

PATTERNS=(r'(?i)\b(?:bearer\s+)[A-Za-z0-9._-]{12,}',r'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b',r'\bgh[pousr]_[A-Za-z0-9]{20,}\b',r'\b[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}\b',r'-----BEGIN [A-Z ]*PRIVATE KEY-----')

def check_text(text):
    if any(re.search(p,text) for p in PATTERNS):raise ValueError('Possible secret or hardware identifier; inspect locally')
    for candidate in re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b',text):
        try:ip=ipaddress.ip_address(candidate)
        except ValueError:continue
        if not ip.is_global:raise ValueError('Possible private network address; inspect locally')

if __name__=='__main__':
    for path in sorted((ROOT/'data').rglob('*.json')):check_text(path.read_text())
    print('Public-data pattern check PASS; manual privacy review still required')
