import hashlib
import json


def check_step_cap(step_count: int, max_steps: int) -> tuple[bool, str | None]:
    """Return (should_terminate, reason) if step cap exceeded."""
    if step_count >= max_steps:
        return True, "step_cap"
    return False, None


def check_cost_cap(total_cost: float, max_cost_usd: float) -> tuple[bool, str | None]:
    """Return (should_terminate, reason) if cost cap exceeded."""
    if total_cost > max_cost_usd:
        return True, "cost_cap"
    return False, None


def check_stuck(recent_steps: list[tuple[str, str]], threshold: int = 3) -> tuple[bool, str | None]:
    """Return (should_terminate, reason) if the same tool+args repeats threshold times.

    recent_steps is a list of (tool_name, args_hash) tuples in chronological order.
    """
    if len(recent_steps) < threshold:
        return False, None

    last = recent_steps[-1]
    count = 1
    for i in range(len(recent_steps) - 2, -1, -1):
        if recent_steps[i] == last:
            count += 1
        else:
            break
    if count >= threshold:
        return True, "stuck"
    return False, None


def hash_args(args: dict | None) -> str:
    """Create a stable hash of tool arguments for stuck detection."""
    if args is None:
        return ""
    return hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest()[:16]
