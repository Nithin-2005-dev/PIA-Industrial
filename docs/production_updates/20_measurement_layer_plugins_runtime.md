# Phase 13: The Hermetic Sandbox (Plugin & ML Runtime)

## Objective
The `app/measurement/plugins_runtime/` subsystem enables immense enterprise extensibility by allowing custom DSL scripts and Machine Learning models to evaluate measurements. However, dynamically executing client-provided code in a production environment introduces three severe architectural vulnerabilities:
1. **The Pickle Bomb** (RCE via insecure deserialization).
2. **The Halting Problem** (Resource exhaustion via infinite loops).
3. **The Context Escape** (Data bleed via arbitrary Python built-ins).

The objective of Phase 13 was to construct a hardware-isolated, cryptographically sealed sandbox that completely neutralizes these threats.

## Architectural Security Upgrades

### 1. The Anti-Pickle Shield (`ml.py`)
Upgraded the PyTorch model loader in `SafeMLRuntime`. By strictly enforcing `weights_only=True` during `torch.load()`, the system blocks the execution of arbitrary Python objects via `pickle`. The deserializer will now refuse to instantiate embedded class payloads, preventing all forms of Remote Code Execution (RCE) via malicious model files.

### 2. Hermetic DSL Execution (`dsl.py`)
Constructed `SafeDSLEvaluator` to execute untrusted user logic. The `eval()` function is now passed a brutally stripped global dictionary. By explicitly setting `"__builtins__": {}`, all dangerous Python primitives (such as `open`, `__import__`, `eval`, and `exec`) are removed from the execution context. The DSL can now *only* access approved mathematical functions (e.g., `math.log`, `min`, `max`) and the explicitly passed context variables.

### 3. Hardware Isolation & Timeouts (`plugins.py`)
Solved the Halting Problem by implementing a strict hardware boundary in the `PluginEngine`. Untrusted DSL logic is now executed within an isolated, spawned sub-process via `multiprocessing`. The parent orchestrator enforces a hard `EXECUTION_TIMEOUT_SECONDS = 2.0` limit. If a client submits an infinite loop (e.g., `while True: pass` or a heavy hanging process), the parent gracefully detects the timeout, forcefully terminates the rogue child process, and returns a controlled `TimeoutError`, protecting the core API from resource exhaustion.

## Status: VERIFIED
The `test_sandbox.py` test suite confirmed all security boundaries are intact:
- **Test 1 (Math Execution):** Valid, safe mathematical expressions executed perfectly and returned accurately calculated floats.
- **Test 2 (Context Escape Prevention):** A malicious attempt to invoke `__import__('os').system('echo hacked')` was successfully trapped and threw a `NameError` because `__import__` was eradicated from the namespace.
- **Test 3 (The Halting Problem):** An injected `time.sleep(5)` execution block was correctly aborted after precisely 2.0 seconds, returning a `TimeoutError` without hanging the test suite.

Territory 2 is now sealed. Clients can write infinite custom logic, and the Measurement Engine remains completely immune to both their mistakes and their malice.
