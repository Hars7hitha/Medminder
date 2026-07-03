from orchestrator import handle_intent

print("=== MedMinder Agent ===\n")

# Test 1: View schedule
print("--- Today's Schedule ---")
print(handle_intent("view_schedule"))

# Test 2: Add safe drug
print("\n--- Adding Lisinopril ---")
print(handle_intent("add_med", {"drug": "Lisinopril", "dose": "10mg", "times": ["09:00"]}))

# Test 3: Add drug with interaction (Warfarin conflicts with Aspirin)
print("\n--- Adding Warfarin (should be blocked) ---")
print(handle_intent("add_med", {"drug": "Warfarin", "dose": "5mg", "times": ["20:00"]}))

# Test 4: Caregiver summary
print("\n--- Caregiver Summary ---")
print(handle_intent("caregiver_summary"))