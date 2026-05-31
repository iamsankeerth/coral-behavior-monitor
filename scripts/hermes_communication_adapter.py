import subprocess

class HermesCommunicationSeam:
    """
    Abstract interface Seam for outbound Hermes messaging.
    """
    def send_message(self, target: str, text: str) -> tuple:
        raise NotImplementedError("Adapters must implement send_message()")

class HermesCliAdapter(HermesCommunicationSeam):
    """
    Production Adapter that invokes the native Hermes CLI via shell subprocess.
    """
    def send_message(self, target: str, text: str) -> tuple:
        if not target:
            return False, "Delivery target is empty."
        try:
            res = subprocess.run(
                ["hermes", "send", "--to", target, text],
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return True, "Message delivered successfully via Hermes CLI!"
        except subprocess.CalledProcessError as e:
            return False, f"Hermes CLI error (Exit Code {e.returncode}): {e.stderr.strip() or e.stdout.strip()}"
        except Exception as e:
            return False, f"Failed to invoke Hermes executable: {e}"

class InMemoryMessageLogger(HermesCommunicationSeam):
    """
    Test/Verification Adapter that logs notifications to memory and disk instead of shelling out.
    Used for standalone test suites and non-interactive environments.
    """
    def __init__(self):
        self.sent_messages = []

    def send_message(self, target: str, text: str) -> tuple:
        self.sent_messages.append({"target": target, "text": text})
        print(f"[MOCK MESSAGE PUSHED to {target}]: {text}")
        return True, "Message captured in-memory successfully (Test Adapter)!"
