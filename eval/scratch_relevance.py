import json
import re

from kairos.decompose.rule_splitter import RuleBasedSplitter
from kairos.index.store import IndexStore

STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'it', 'its', 'itself', 'they',
    'them', 'their', 'theirs', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',
    'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
    'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now',
    # Conversational filler words
    'need', 'help', 'want', 'please', 'tell', 'know', 'could', 'would', 'like', 'give', 'check',
    'actually', 'also', 'instead', 'make', 'sure', 'see', 'find', 'get', 'much', 'many', 'offer'
}

def extract_content_words(text: str) -> set[str]:
    tokens = re.findall(r'[a-zA-Z0-9]+', text.lower())
    return {t for t in tokens if t not in STOPWORDS and len(t) > 1}

store = IndexStore()
store.load()
splitter = RuleBasedSplitter()

T_DENSE = 0.60

with open('data/replay/dev/scenarios.jsonl', encoding='utf-8') as f:
    for line in f:
        turn = json.loads(line)
        ttype = turn.get('turn_type')
        tid = turn.get('turn_id')
        if ttype == 'presentation_only':
            continue
        full_text = ' '.join(c['text'] for c in turn['chunks'])
        legs = splitter.split(full_text)
        
        print(f"\n--- Turn {tid} ({ttype}): {full_text} ---")
        for leg in legs:
            content_words = extract_content_words(leg.text)
            res = store.dense_index.search(leg.text, top_k=3)
            best_chunk = None
            best_score = 0.0
            best_matches = []
            
            for cid, score in res:
                chunk = store.chunks_map.get(cid)
                if not chunk:
                    continue
                c_text = chunk.text.lower()
                matches = [w for w in content_words if w in c_text]
                if score >= T_DENSE and len(matches) > 0:
                    best_chunk = chunk
                    best_score = score
                    best_matches = matches
                    break
                    
            if best_chunk:
                print(f"  PASS: Leg '{leg.text}' -> {best_chunk.chunk_id} (score={best_score:.4f}, matches={best_matches})")
            else:
                top_s = res[0][1] if res else 0.0
                top_c = res[0][0] if res else 'None'
                print(f"  ABSTAIN: Leg '{leg.text}' -> top={top_c} (score={top_s:.4f}, words={list(content_words)})")
