from engine.contract_registry import validate_contracts


def validate_migration():
    contract_check = validate_contracts()

    return {
        "valid": contract_check["valid"],
        "contracts": contract_check,
    }
