# src/grader.py

def grade_phase_1(*args, **kwargs):
    # Dumps all inputs to a string so it never crashes during the validator's dry-run
    if "FLAG{fragmented_auth_bypassed}" in str(args) + str(kwargs):
        return 0.99
    return 0.01

def grade_phase_2(*args, **kwargs):
    if "FLAG{multi_layer_crypto_cracked}" in str(args) + str(kwargs):
        return 0.99
    return 0.01

def grade_phase_3(*args, **kwargs):
    if "FLAG{root_environment_secured}" in str(args) + str(kwargs):
        return 0.99
    return 0.01

def grade_phase_4(*args, **kwargs):
    if "FLAG{integrity_recovered}" in str(args) + str(kwargs):
        return 0.99
    return 0.01

def grade_phase_5(*args, **kwargs):
    if "FLAG{access_control_restored}" in str(args) + str(kwargs):
        return 0.99
    return 0.01

def grade_phase_6(*args, **kwargs):
    if "FLAG{threat_neutralized}" in str(args) + str(kwargs):
        return 0.99
    return 0.01