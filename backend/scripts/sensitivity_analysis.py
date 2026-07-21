"""
M56.1 — Sensitivity Analysis

Conducts One-at-a-Time (OAT) sensitivity analysis on the new
scientific calibration models (Confidence-Weighted Power Mean,
Robust Scaling, Information Entropy, etc.).
"""

import math
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class SensitivityResult:
    input_name: str
    base_value: float
    perturbed_value: float
    output_base: float
    output_perturbed: float
    sensitivity_coefficient: float
    
def calculate_sensitivity(
    func: Callable[..., float],
    inputs: dict[str, Any],
    target_var: str,
    perturbation: float = 0.1
) -> SensitivityResult:
    
    # Base output
    base_output = func(**inputs)
    
    # Perturb
    perturbed_inputs = inputs.copy()
    base_input = perturbed_inputs[target_var]
    perturbed_inputs[target_var] = base_input * (1.0 + perturbation)
    
    perturbed_output = func(**perturbed_inputs)
    
    # Delta
    delta_in = perturbed_inputs[target_var] - base_input
    delta_out = perturbed_output - base_output
    
    # Coefficient: (dOutput / Output) / (dInput / Input)
    if base_output != 0 and delta_in != 0:
        coefficient = (delta_out / base_output) / (delta_in / base_input)
    else:
        coefficient = 0.0
        
    return SensitivityResult(
        input_name=target_var,
        base_value=base_input,
        perturbed_value=perturbed_inputs[target_var],
        output_base=base_output,
        output_perturbed=perturbed_output,
        sensitivity_coefficient=coefficient,
    )

def power_mean_health(coverage: float, concentration: float, bus: float, p: float = 0.3) -> float:
    w1, w2, w3 = 0.4, 0.4, 0.2
    v1 = max(0.01, coverage / 100.0)
    v2 = max(0.01, concentration / 100.0)
    v3 = max(0.01, bus / 100.0)
    total_w = w1 + w2 + w3
    power_sum = w1 * (v1**p) + w2 * (v2**p) + w3 * (v3**p)
    return ((power_sum / total_w) ** (1/p)) * 100.0

if __name__ == "__main__":
    print("========================================")
    print(" M56.1 SENSITIVITY ANALYSIS (OAT)")
    print("========================================")
    
    inputs = {"coverage": 50.0, "concentration": 50.0, "bus": 50.0, "p": 0.3}
    print(f"Base Configuration: {inputs}")
    print(f"Base Health Output: {power_mean_health(**inputs):.2f}\n")
    
    print(f"{'Input Var':<15} | {'Base In':<10} | {'Pert In':<10} | {'Base Out':<10} | {'Pert Out':<10} | {'Sens Coeff':<10}")
    print("-" * 75)
    
    for var in ["coverage", "concentration", "bus", "p"]:
        res = calculate_sensitivity(power_mean_health, inputs, var, 0.10)
        print(f"{res.input_name:<15} | {res.base_value:<10.3f} | {res.perturbed_value:<10.3f} | {res.output_base:<10.3f} | {res.output_perturbed:<10.3f} | {res.sensitivity_coefficient:<10.3f}")
    
    print("\n[OK] Sensitivity Analysis Complete")
