"""Validate known options and conditional relationships without inventing combinations."""

def check_settings(catalog, settings):
    dimensions={d['name']:d for d in catalog['dimensions']}
    reasons=[]
    for key,value in settings.items():
        if key not in dimensions:reasons.append('unknown_setting:'+key);continue
        if value not in dimensions[key]['options']:reasons.append('unknown_option:'+key)
    for key in dimensions:
        if key not in settings:reasons.append('missing_setting:'+key)
    for rule in catalog['rules']:
        if all(settings.get(k)==v for k,v in rule['when'].items()):
            if any(settings.get(k) not in values for k,values in rule['allowed'].items()):reasons.append('incompatible_settings:'+rule['id'])
    if not catalog['relationships_complete']:reasons.append('setting_relationships_unverified')
    return {'compatible':not reasons,'reason_codes':reasons}
