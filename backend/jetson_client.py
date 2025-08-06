import requests


class JetsonClient:
    def __init__(self, base_url="http://jetson-nano:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10

    def check_connection(self):
        """Check if Jetson Nano is reachable"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_status(self):
        """Get status from Jetson Nano"""
        try:
            response = self.session.get(f"{self.base_url}/api/status")
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def start_camera(self):
        """Start camera on Jetson Nano"""
        try:
            response = self.session.get(f"{self.base_url}/api/camera/start")
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def stop_camera(self):
        """Stop camera on Jetson Nano"""
        try:
            response = self.session.get(f"{self.base_url}/api/camera/stop")
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def take_snapshot(self):
        """Take snapshot from Jetson Nano"""
        try:
            response = self.session.get(f"{self.base_url}/api/camera/snapshot")
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def start_recording(self):
        """Start recording on Jetson Nano"""
        try:
            response = self.session.get(f"{self.base_url}/api/camera/start_recording")
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def stop_recording(self):
        """Stop recording on Jetson Nano"""
        try:
            response = self.session.get(f"{self.base_url}/api/camera/stop_recording")
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def get_log_data(self):
        """Get log data from Jetson Nano"""
        try:
            response = self.session.get(f"{self.base_url}/api/camera/get_log_data")
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def send_data(self, data):
        """Send data to Jetson Nano"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/data",
                json=data,
                headers={"Content-Type": "application/json"},
            )
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def get_data(self):
        """Get data from Jetson Nano"""
        try:
            response = self.session.get(f"{self.base_url}/api/data")
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def update_base_url(self, new_url):
        """Update Jetson Nano base URL"""
        self.base_url = new_url
