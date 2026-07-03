#!/usr/bin/env python3
"""Minimal dimension-vector validator for QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01.
No third-party dependencies.
"""
from fractions import Fraction

# dimension vectors are tuples (M, L, T)
D = {
    "hbar": (Fraction(1), Fraction(2), Fraction(-1)),
    "G": (Fraction(-1), Fraction(3), Fraction(-2)),
    "c": (Fraction(0), Fraction(1), Fraction(-1)),
    "m": (Fraction(1), Fraction(0), Fraction(0)),
    "m_comp": (Fraction(1), Fraction(0), Fraction(0)),
    "m_schwarz": (Fraction(1), Fraction(0), Fraction(0)),
    "lambda_C": (Fraction(0), Fraction(1), Fraction(0)),
    "r_s": (Fraction(0), Fraction(1), Fraction(0)),
}

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,n): return tuple(x*n for x in a)
def div(a,n): return tuple(x/n for x in a)

def fmt(v):
    labels = ["M", "L", "T"]
    parts = []
    for lab, exp in zip(labels, v):
        if exp == 0:
            continue
        parts.append(f"{lab}^{exp}" if exp != 1 else lab)
    return "1" if not parts else " ".join(parts)

checks = {
    "lambda_C = hbar/(m*c)": sub(D["hbar"], add(D["m"], D["c"])),
    "r_s = 2*G*m/c^2": sub(add(D["G"], D["m"]), mul(D["c"], 2)),
    "beta_B = r_s/lambda_C": sub(D["r_s"], D["lambda_C"]),
    "c_comp = hbar/(m_comp*lambda_C)": sub(D["hbar"], add(D["m_comp"], D["lambda_C"])),
    "c_schwarz = sqrt(2*G*m_schwarz/r_s)": div(sub(add(D["G"], D["m_schwarz"]), D["r_s"]), 2),
    "Xi_CS = c_comp^2/c_schwarz^2": (Fraction(0), Fraction(0), Fraction(0)),
    "L_B = hbar^2/(2*G*m_schwarz*m_comp^2)": sub(mul(D["hbar"], 2), add(add(D["G"], D["m_schwarz"]), mul(D["m_comp"], 2))),
}
expected = {
    "lambda_C = hbar/(m*c)": (0,1,0),
    "r_s = 2*G*m/c^2": (0,1,0),
    "beta_B = r_s/lambda_C": (0,0,0),
    "c_comp = hbar/(m_comp*lambda_C)": (0,1,-1),
    "c_schwarz = sqrt(2*G*m_schwarz/r_s)": (0,1,-1),
    "Xi_CS = c_comp^2/c_schwarz^2": (0,0,0),
    "L_B = hbar^2/(2*G*m_schwarz*m_comp^2)": (0,1,0),
}

ok = True
for name, actual in checks.items():
    exp = tuple(Fraction(x) for x in expected[name])
    passed = actual == exp
    ok &= passed
    print(f"{'PASS' if passed else 'FAIL'} | {name} | actual={fmt(actual)} | expected={fmt(exp)}")

raise SystemExit(0 if ok else 1)
