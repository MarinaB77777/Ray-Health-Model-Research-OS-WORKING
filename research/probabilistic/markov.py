from __future__ import annotations

from .numerics import beta_quantile


def markov_dirichlet(payload: dict) -> dict:
    sequences = payload.get("sequences")
    states = payload.get("states")
    if not isinstance(sequences, list) or not sequences:
        raise ValueError("MARKOV_SEQUENCES_REQUIRED")
    if not isinstance(states, list) or len(states) < 2:
        raise ValueError("MARKOV_STATES_REQUIRED")
    state_names = [str(value) for value in states]
    if len(set(state_names)) != len(state_names):
        raise ValueError("MARKOV_STATES_MUST_BE_UNIQUE")
    index = {state: position for position, state in enumerate(state_names)}
    count = [[0 for _ in state_names] for _ in state_names]
    for raw_sequence in sequences:
        if not isinstance(raw_sequence, list) or len(raw_sequence) < 2:
            raise ValueError("EACH_MARKOV_SEQUENCE_REQUIRES_TWO_STATES")
        sequence = [str(value) for value in raw_sequence]
        if any(value not in index for value in sequence):
            raise ValueError("MARKOV_SEQUENCE_CONTAINS_UNKNOWN_STATE")
        for left, right in zip(sequence, sequence[1:]):
            count[index[left]][index[right]] += 1
    prior = float(payload.get("prior_concentration", 1.0))
    mass = float(payload.get("credible_mass", 0.95))
    if prior <= 0 or not 0.5 < mass < 1.0:
        raise ValueError("MARKOV_PRIOR_OR_INTERVAL_INVALID")
    tail = (1.0 - mass) / 2.0
    rows = []
    for from_index, state in enumerate(state_names):
        posterior = [prior + value for value in count[from_index]]
        total = sum(posterior)
        transitions = []
        for to_index, alpha in enumerate(posterior):
            other = total - alpha
            transitions.append({
                "to_state": state_names[to_index],
                "observed_count": count[from_index][to_index],
                "estimate": alpha / total,
                "credible_interval": {
                    "mass": mass,
                    "lower": beta_quantile(tail, alpha, other),
                    "upper": beta_quantile(1.0 - tail, alpha, other),
                },
            })
        rows.append({"from_state": state, "transitions": transitions, "row_observations": sum(count[from_index])})
    return {
        "model": "first_order_time_homogeneous_markov_chain",
        "states": state_names,
        "transition_rows": rows,
        "assumptions": ["first_order_markov_property", "time_homogeneous_transitions", "independent_sequences_conditional_on_model"],
    }
