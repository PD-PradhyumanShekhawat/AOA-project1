#!/usr/bin/env python3
"""Audit expanded SatNet schedules against original request, visibility, and maintenance data.
Run from the repository root: python greedy_dsn/scripts/audit_original_constraints.py
"""
import csv, json, math, sys
from collections import defaultdict
from pathlib import Path

DATA = Path('greedy_dsn/data')
RESULTS = Path('greedy_dsn/results/expanded_model')
EPS = 1.1  # generated CSV timestamps are rounded to integer seconds

def read_csv(path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def overlap(a, b, c, d):
    return a < d and c < b  # half-open intervals

def load_requests(path):
    raw = json.loads(path.read_text(encoding='utf-8'))
    requests, duplicates = {}, []
    for week_key, entries in raw.items():
        for req in entries:
            key = (str(week_key), str(req.get('track_id', '')))
            if key in requests:
                duplicates.append(key)
            requests[key] = req
    return requests, duplicates

def load_maintenance(path):
    result = defaultdict(list)
    for row in read_csv(path):
        week, year = int(float(row['week'])), int(float(row['year']))
        key = (f'W{week}_{year}', row['antenna'].strip())
        a, b = float(row['starttime']), float(row['endtime'])
        if b > a:
            result[key].append((a, b))
    for intervals in result.values(): intervals.sort()
    return result

def check_schedule(label, rows, requests, maintenance):
    errors, seen = [], set()
    checked = resource_checks = visibility_checks = maintenance_checks = 0
    total_hours = 0.0
    for line, row in enumerate(rows, 2):
        wk, track = row.get('week_key', '').strip(), row.get('track_id', '').strip()
        prefix = f'{label} CSV line {line}, {wk}/{track}'
        req = requests.get((wk, track))
        if req is None:
            errors.append(f'{prefix}: request not found in problems.json'); continue
        checked += 1
        if (wk, track) in seen: errors.append(f'{prefix}: duplicate selected request')
        seen.add((wk, track))
        antennas = [x.strip() for x in row.get('antennas', '').split(';') if x.strip()]
        if not antennas:
            errors.append(f'{prefix}: no antennas listed'); continue
        options = {frozenset(map(str, opt)) for opt in req.get('resources', []) if isinstance(opt, list)}
        if frozenset(antennas) not in options:
            errors.append(f'{prefix}: antenna set {antennas} is not an allowed resource option')
        else: resource_checks += 1
        try:
            txs, txe = float(row['tx_start_epoch']), float(row['tx_end_epoch'])
            acts, acte = float(row['activity_start_epoch']), float(row['activity_end_epoch'])
            dh = float(row['duration_hours'])
            # sm, tm = float(row.get('setup_minutes', 0) or 0), float(row.get('teardown_minutes', 0) or 0)
            rs, re = float(req['time_window_start']), float(req['time_window_end'])
            requested, minimum = float(req['duration']), float(req['duration_min'])
            setup_s = float(req.get("setup_time", 0)) * 60
            teardown_s = float(req.get("teardown_time", 0)) * 60
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f'{prefix}: missing/invalid timing field ({exc})'); continue
        if not all(math.isfinite(x) for x in (txs, txe, acts, acte, dh, rs, re, requested, minimum, setup_s, teardown_s)):
            errors.append(f'{prefix}: non-finite timing value'); continue
        if not (txs < txe and acts <= txs and txe <= acte): errors.append(f'{prefix}: inconsistent activity/transmission bounds')
        if abs((txe-txs)/3600-dh) > EPS/3600: errors.append(f'{prefix}: duration_hours does not match transmission interval')
        if txs < rs-EPS or txe > re+EPS: errors.append(f'{prefix}: transmission outside request time window')
        if dh > requested+EPS/3600: errors.append(f'{prefix}: duration exceeds requested duration')
        if dh < minimum-EPS/3600: errors.append(f'{prefix}: duration below duration_min')
        if abs(dh-requested) > EPS/3600: errors.append(f'{prefix}: duration differs from requested duration (model assumes full duration)')
        # if abs(sm*60-setup_s) > EPS: errors.append(f'{prefix}: setup duration differs from source request')
        # if abs(tm*60-teardown_s) > EPS: errors.append(f'{prefix}: teardown duration differs from source request')
        if abs((txs-acts)-setup_s) > EPS: errors.append(f'{prefix}: activity start omits or misstates setup time')
        if abs((acte-txe)-teardown_s) > EPS: errors.append(f'{prefix}: activity end omits or misstates teardown time')
        total_hours += dh
        vpd = req.get('resource_vp_dict', {})
        for antenna in antennas:
            visibility_checks += 1
            visible = False
            for vp in vpd.get(antenna, []):
                try: vs, ve = float(vp['TRX ON']), float(vp['TRX OFF'])
                except (KeyError, TypeError, ValueError): continue
                if txs >= vs-EPS and txe <= ve+EPS:
                    visible = True; break
            if not visible: errors.append(f'{prefix}: transmission not contained in TRX ON/OFF visibility for {antenna}')
            maintenance_checks += 1
            for ms, me in maintenance.get((wk, antenna), []):
                if overlap(acts, acte, ms, me):
                    errors.append(f'{prefix}: activity overlaps maintenance for {antenna} [{ms}, {me}]')
    return {'schedule': label, 'rows': len(rows), 'requests_found_and_checked': checked,
            'unique_selected_requests': len(seen), 'resource_options_checked': resource_checks,
            'per_antenna_visibility_checks': visibility_checks,
            'per_antenna_maintenance_checks': maintenance_checks,
            'communication_hours_sum': round(total_hours, 6), 'error_count': len(errors), 'errors': errors[:100]}

def main():
    paths = [DATA/'problems.json', DATA/'maintenance.csv', RESULTS/'greedy_selected.csv', RESULTS/'milp_selected.csv']
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        print('Missing required files: '+', '.join(missing), file=sys.stderr)
        print('Run from repository root.', file=sys.stderr); sys.exit(2)
    requests, duplicates = load_requests(DATA/'problems.json')
    maintenance = load_maintenance(DATA/'maintenance.csv')
    result = {'source_request_count': len(requests),
              'duplicate_source_request_keys': [{'week_key': k[0], 'track_id': k[1]} for k in duplicates[:20]],
              'greedy': check_schedule('greedy', read_csv(RESULTS/'greedy_selected.csv'), requests, maintenance),
              'milp': check_schedule('milp', read_csv(RESULTS/'milp_selected.csv'), requests, maintenance),
              'scope_warning': 'Passing validates selected rows against checks implemented here and local source files. It does not establish candidate-set completeness or compliance with benchmark rules not represented in these files.'}
    out = RESULTS/'original_constraint_audit.json'
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    failed = bool(duplicates) or result['greedy']['error_count'] or result['milp']['error_count']
    print('\nORIGINAL-CONSTRAINT AUDIT FAILED' if failed else '\nIMPLEMENTED ORIGINAL-CONSTRAINT CHECKS PASSED')
    print('Candidate-set completeness and unmodeled benchmark rules still require separate review.')
    sys.exit(1 if failed else 0)

if __name__ == '__main__': main()