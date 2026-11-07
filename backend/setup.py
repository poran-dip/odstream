import bz2
import os
import urllib.request


def download_openh264():
    """Download OpenH264 DLL if not present"""
    dll_name = "openh264-2.5.0-win64.dll"
    dll_path = dll_name  # Root directory

    if not os.path.exists(dll_path):
        url = f"http://ciscobinary.openh264.org/{dll_name}.bz2"

        print(f"Downloading {dll_name}...")
        urllib.request.urlretrieve(url, f"{dll_path}.bz2")

        # Extract bz2
        with bz2.open(f"{dll_path}.bz2", "rb") as f_in, open(dll_path, "wb") as f_out:
            f_out.write(f_in.read())

        os.remove(f"{dll_path}.bz2")
        print(f"Downloaded and extracted to {dll_path}")


if __name__ == "__main__":
    download_openh264()
