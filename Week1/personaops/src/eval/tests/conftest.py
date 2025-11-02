import pytest
import json
from pathlib import Path

@pytest.fixture
def sample_output():
    """Load a sample output from goldens directory"""
    golden_path = Path(__file__).parent.parent / 'goldens' / 'sample_output.json'
    if not golden_path.exists():
        # Create a sample output if none exists
        sample = {
            "title": "Unleash Your Typing Superpowers with KBD-X",
            "body": "Get ready to boost your productivity with the clever new KBD-X keyboard! You'll love how our hot-swap switches let you customize your typing experience faster than you can say 'mechanical marvel.' Wink wink, devs – your fingers are about to meet their new best friend.",
            "style": "witty_marketer",
            "citations": ["context: Brand: KBD-X", "context: target: productivity", "context: USP: hot-swap switches"]
        }
        golden_path.parent.mkdir(exist_ok=True)
        golden_path.write_text(json.dumps(sample, indent=2), encoding='utf-8')
        
    return json.loads(golden_path.read_text(encoding='utf-8'))