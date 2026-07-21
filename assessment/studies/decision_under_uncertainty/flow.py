DU_FLOW = {
    "DU1": {
        "rules": [
            {"if": {"value": 0}, "goto": "END_RESERVED"}
        ],
        "default": "DU2",
    },
    "DU2": {"default": "DU3"},
    "DU3": {"default": "DU4"},
    "DU4": {
        "rules": [
            {"if": {"value": 0}, "goto": "WORK_BRANCH_RESERVED"},
            {"if": {"value": 1}, "goto": "MIXED_BRANCH_RESERVED"},
            {"if": {"value": 2}, "goto": "LIFE_BRANCH_RESERVED"},
        ],
        "default": "END_RESERVED",
    },
}