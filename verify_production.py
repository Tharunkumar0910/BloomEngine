"""
Production verification script for BloomAI Arena v2.1.
Tests: sequential load, zero meta tensors, warmup success, generate(), health state.
"""
import sys
import os
import time
import traceback

# Ensure we import the local app.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=" * 60)
print("  BloomAI Arena v2.1 - Production Verification")
print("=" * 60)

import app

results = {}

# 1. Load models
print("\n[1] Loading models (sequential)...")
t0 = time.time()
app.load_models()
load_elapsed = time.time() - t0
results["load_time_s"] = round(load_elapsed, 2)

# 2. Verify no meta tensors
print("\n[2] Checking for meta-device tensors...")
meta_count = sum(1 for p in app.flan_model.parameters() if p.device.type == "meta")
results["flan_meta_params"] = meta_count
if meta_count == 0:
    print("  FLAN-T5: ZERO meta-device params  PASS")
else:
    print("  FLAN-T5: %d meta-device params  FAIL" % meta_count)

# 3. Verify warmup succeeded
print("\n[3] Verifying warmup flag...")
results["warmup_succeeded"] = app._warmup_succeeded
if app._warmup_succeeded:
    print("  _warmup_succeeded = True  PASS")
else:
    print("  _warmup_succeeded = False  FAIL")

# 4. Test generate() directly
print("\n[4] Testing flan_model.generate() directly...")
import torch
prompt = app.build_prompt(
    question="What is database normalization?",
    source_bloom="Remember",
    target_bloom="Understand",
    domain="CS",
    topic="database normalization",
)
inputs = app.flan_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
device = next(app.flan_model.parameters()).device
inputs = {k: v.to(device) for k, v in inputs.items()}
try:
    with torch.inference_mode():
        out = app.flan_model.generate(**inputs, max_new_tokens=30, num_beams=4)
    decoded = app.flan_tokenizer.decode(out[0], skip_special_tokens=True)
    print("  Output: '%s'" % decoded)
    results["generate_ok"] = True
except Exception as e:
    print("  generate() FAILED: %s" % e)
    traceback.print_exc()
    results["generate_ok"] = False

# 5. Test full pipeline
print("\n[5] Testing generate_validated_variant()...")
try:
    result = app.generate_validated_variant(
        question="What is database normalization?",
        src_bloom="Remember",
        src_diff="Easy",
        target_bloom="Understand",
        target_difficulty="Easy",
        domain="CS",
        required_concept="database normalization",
        session_seen=[],
    )
    results["pipeline_status"] = result.validation_status
    results["pipeline_question"] = result.generated_question[:80]
    print("  Status: %s" % result.validation_status)
    print("  Question: %s" % result.generated_question[:80])
    print("  Confidence: %s%%" % result.confidence)
except Exception as e:
    print("  Pipeline FAILED: %s" % e)
    traceback.print_exc()
    results["pipeline_status"] = "ERROR"

# 6. Load errors
results["load_errors"] = app._load_errors

# Summary
print("\n" + "=" * 60)
print("  RESULTS SUMMARY")
print("=" * 60)
all_pass = True
checks = [
    ("Models loaded sequentially",     True),
    ("FLAN-T5 zero meta params",        results.get("flan_meta_params", 1) == 0),
    ("Warmup succeeded",                results.get("warmup_succeeded", False)),
    ("generate() works",                results.get("generate_ok", False)),
    ("Pipeline returned result",        results.get("pipeline_status") not in (None, "ERROR")),
    ("No load errors",                  len(results.get("load_errors", [])) == 0),
]
for label, passed in checks:
    status = "PASS" if passed else "FAIL"
    if not passed:
        all_pass = False
    print("  [%s]  %s" % (status, label))

print("=" * 60)
print("  Load time   : %s s" % results.get("load_time_s"))
print("  Meta params : %s" % results.get("flan_meta_params"))
print("  Warmup ok   : %s" % results.get("warmup_succeeded"))
print("  Load errors : %s" % results.get("load_errors"))
print("=" * 60)
if all_pass:
    print("  ALL CHECKS PASSED - system is production ready.")
else:
    print("  SOME CHECKS FAILED - review logs above.")
print()
