import json

data = json.load(open('dashboard_data.json', encoding='utf-8'))
print("Keys in dashboardData:", list(data.keys()))
print("\nStats keys:", list(data.get('stats', {}).keys()))
print("\nAnalysis stats keys:", list(data.get('analysis_stats', {}).keys()))
print("\nQualitative themes:", len(data.get('qualitative_themes', [])))
print("Total Cases:", len(data.get('cases', [])))
print("Total Unlinked Deliveries:", len(data.get('unlinked_deliveries', [])))

# Sample a case
case0 = data['cases'][0]
print("\nSample Case Keys:", list(case0.keys()))
if case0.get('visits'):
    print("Sample Visit Keys:", list(case0['visits'][0].keys()))
if any(c.get('delivery') for c in data['cases']):
    del_c = [c for c in data['cases'] if c.get('delivery')][0]
    print("Sample Delivery Keys:", list(del_c['delivery'].keys()))
