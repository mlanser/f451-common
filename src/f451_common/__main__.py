"""Demo for using f451 Labs Common Module."""

from pathlib import Path
import f451_common.common as f451Common

# =========================================================
#                    D E M O   A P P
# =========================================================
def main():
    APP_DIR = Path(__file__).parent         # Find dir for this app
    settingsFile = "demo.toml"
    settings = f451Common.load_settings(APP_DIR.joinpath(settingsFile))

    print("\n====== [Demo of f451 Labs Common module] ======\n")

    print(f451Common.make_logo(
            40, 
            "Test", 
            "v0.0.0", 
            "Test (v0.0.0)"
        )
    )

    print("\n-----------------------------------------------\n")
    
    print(f"Reading values from '{settingsFile}' file:\n")
    for k, v in settings.items():
        print(f"  {k} = {v}")

    print("\n=============== [End of Demo] =================\n")


if __name__ == "__main__":
    main()