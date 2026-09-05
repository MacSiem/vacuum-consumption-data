"""Fit one identifiable exposure axis. Never decompose a whole-cycle refill implicitly."""
from statistics import median
from tools.validate import validate_record


def fit_coefficient(observations):
    if len(observations)<3:raise ValueError('Need at least three training observations')
    contexts=[];ratios=[];cycles=set();scopes=set();units=set()
    for row in observations:
        validate_record(row)
        if row['kind']!='observation' or row['source_class']!='empirical':raise ValueError('Measured observations required')
        m=row['measurement']
        if m['split']!='train':raise ValueError('Holdout must not enter fitting')
        cycle=(m['series_id'],m['cycle_id'])
        if cycle in cycles:raise ValueError('Duplicate training cycle')
        cycles.add(cycle);contexts.append(row['context']);scopes.add(m['scope']);units.add(m['exposure_unit'])
        ratios.append(m['observed_ml']/m['exposure'])
    if any(c!=contexts[0] for c in contexts) or len(scopes)!=1 or len(units)!=1:raise ValueError('Mixed model/settings/scope/exposure')
    unit=next(iter(units));scope=next(iter(scopes))
    if scope=='whole_cycle' and unit!='cycle':raise ValueError('Whole-cycle data does not isolate area/time/wash consumption')
    return {'coefficient':median(ratios),'unit':{'m2':'ml/m2','min':'ml/min','action':'ml/action','cycle':'ml/cycle'}[unit],'scope':scope,'sample_count':len(ratios),'training_ratio_min':min(ratios),'training_ratio_max':max(ratios),'runtime_eligible':False,'exposure_domain':{'min':min(r['measurement']['exposure'] for r in observations),'max':max(r['measurement']['exposure'] for r in observations)}}
