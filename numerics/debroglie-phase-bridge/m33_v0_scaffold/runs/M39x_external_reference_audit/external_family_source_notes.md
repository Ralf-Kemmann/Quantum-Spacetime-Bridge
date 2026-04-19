# M.3.9x — External Family Source Notes

## ER1_RING

- family_type: ring
- source_model: free_particle_on_ring
- role_hint: external_control
- description: Freies Teilchen auf einem Ring als externer Sanity-/Kontrollfall
- generation_mode: direct_p_from_ring_quantization
- generation_formula: p_m = hbar * 2*pi*m / L
- ordering_mode: ascending_p2
- pairing_mode: index_rule
- index_rule: adjacent_m

### parameters

- hbar: 1.0
- L: 1.0
- m_min: -3
- m_max: 3
- exclude_zero_mode: False

## ER2_CAVITY

- family_type: rectangular_cavity
- source_model: rectangular_em_cavity_resonator
- role_hint: external_main_test
- description: Rechteckiger EM-Hohlraumresonator als externer Haupttest
- generation_mode: proxy_p2_from_cavity_k2
- generation_formula: p2_mnp = hbar^2 * ((m*pi/a)^2 + (n*pi/b)^2 + (p*pi/d)^2)
- ordering_mode: ascending_p2
- pairing_mode: sorted_neighbor

### parameters

- hbar: 1.0
- a: 1.0
- b: 1.3
- d: 1.7
- max_m: 2
- max_n: 2
- max_p: 2
- exclude_zero_triplet: True

## ER3_MEMBRANE

- family_type: circular_membrane
- source_model: circular_membrane_bessel_modes
- role_hint: external_hard_bias_test
- description: Kreisförmige Membran über Bessel-Nullstellen als harter externer Bias-Test
- generation_mode: proxy_p2_from_bessel_zeros
- generation_formula: p2_mn = hbar^2 * x_mn^2 / radius^2
- ordering_mode: ascending_p2
- pairing_mode: index_rule
- index_rule: fixed_m_adjacent_n

### parameters

- hbar: 1.0
- radius: 1.0
- max_m: 2
- max_n: 3
