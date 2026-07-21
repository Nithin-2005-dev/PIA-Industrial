import re

with open('app/cognitive/registry.py', 'r') as f:
    text = f.read()

# Replace dependencies=[] in CapabilityContract
text = re.sub(r'dependencies=\[\]', r'requires=[],\n                produces=[]', text)

with open('app/cognitive/registry.py', 'w') as f:
    f.write(text)

# Also apply the specific produces and requires
replacements = {
    'TopContributors': ('requires=[],\n                produces=[],', 'requires=[],\n                produces=["contributors_metrics"],'),
    'BusFactor': ('requires=[],\n                produces=[],', 'requires=["ownership_metrics", "contributors_metrics"],\n                produces=["bus_factor_metrics"],'),
    'Health': ('requires=[],\n                produces=[],', 'requires=["bus_factor_metrics", "ownership_metrics"],\n                produces=["health_metrics"],'),
    'Forecast': ('requires=[],\n                produces=[],', 'requires=["health_metrics"],\n                produces=["forecast_metrics"],'),
    'Ownership': ('requires=[],\n                produces=[],', 'requires=["contributors_metrics"],\n                produces=["ownership_metrics"],')
}

for cap, (old, new) in replacements.items():
    # Find the CapabilityCard block for cap
    start = text.find(f'name="{cap}"')
    if start != -1:
        end = text.find('))', start)
        block = text[start:end]
        block = block.replace(old, new)
        text = text[:start] + block + text[end:]

with open('app/cognitive/registry.py', 'w') as f:
    f.write(text)
