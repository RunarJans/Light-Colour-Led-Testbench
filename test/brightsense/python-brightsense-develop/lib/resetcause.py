import machine

def get_reset_cause_string():
    """
    Returns a human-readable string describing the reset cause.
    
    Returns:
        str: A string describing why the microcontroller was reset
    """
    cause = machine.reset_cause()
    
    reset_causes = {
        1: "PWRON_RESET",      # Power on reset or reset button
        3: "WDT_RESET",        # Watchdog timer reset
    }
    
    # Return the known cause or a generic unknown message
    return reset_causes.get(cause, f"UNKNOWN_RESET_{cause}")
