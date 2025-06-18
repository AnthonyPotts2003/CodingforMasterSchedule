# create_test_trigger.py
import os

trigger_path = r"G:\My Drive\Project Dashboard\Schedule System\Temp\trigger.txt"
os.makedirs(os.path.dirname(trigger_path), exist_ok=True)

with open(trigger_path, 'w') as f:
    f.write("EXPORT_COMPLETE\n")
    f.write("TRADE_EMAIL:False\n")
    f.write("CUSTOMER_EMAIL:False\n")
    f.write("TIMESTAMP:2025-06-12 10:35:00\n")
    f.write("JSON_DATA:schedule_data.json\n")

print(f"Created trigger file at: {trigger_path}")