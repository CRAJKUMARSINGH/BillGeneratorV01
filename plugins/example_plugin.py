# plugins/example_plugin.py
"""
Example plugin showing how to register additional post-processing actions
without changing core code.
"""

def register():
    def sample_action(output_path):
        # Do nothing heavy — example hook
        return {"status": "sample_action_done", "path": str(output_path)}
    return {"sample_action": sample_action}