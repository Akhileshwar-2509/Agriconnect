from typing import Dict, List, Tuple
import csv
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
AKG_FILE = os.path.join(DATA_DIR, 'akg_seed.csv')

class AllelopathyKG:
    def __init__(self) -> None:
        self.rules: List[Dict] = []
        self._covers: set[str] = set()
        if os.path.exists(AKG_FILE):
            with open(AKG_FILE, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['weight'] = float(row.get('weight', 0.0))
                    row['persistence_days'] = int(row.get('persistence_days', 0))
                    self.rules.append(row)
                    if row.get('source_type') == 'cover':
                        self._covers.add(row['source'])
        else:
            # minimal defaults if file missing
            self.rules = []

    def all_covers(self) -> List[str]:
        return sorted(self._covers) or ["rye", "mustard", "clover"]

    def inhibition_score(self, source: str, target: str) -> float:
        score = 0.0
        for r in self.rules:
            if r['source'] == source and r['target'] == target and r['relation'] == 'inhibits':
                score += r['weight']
        return score

    def persistence_days(self, source: str) -> int:
        best = 0
        for r in self.rules:
            if r['source'] == source and r.get('persistence_days'):
                best = max(best, int(r['persistence_days']))
        return best

    def rule_cards_for_context(self, main_crop: str, weeds: List[str]) -> List[Dict]:
        cards = []
        for r in self.rules:
            if r['relation'] in ('inhibits', 'releases', 'tolerates', 'degrades') and (r['target'] in weeds or r['target'] == main_crop):
                cards.append({
                    'source': r['source'],
                    'relation': r['relation'],
                    'target': r['target'],
                    'weight': r['weight'],
                    'evidence': r.get('evidence', ''),
                    'persistence_days': r.get('persistence_days', 0)
                })
        return cards[:10]
