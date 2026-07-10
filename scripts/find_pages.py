import subprocess
import os

pdf_path = "/home/skeome/Development/Balance_Engine/source_materials/lovellpanzooryktologia.pdf"

pages = [100, 200, 300, 400, 500, 600, 650, 700, 750]

for p in pages:
    cmd1 = f"pdftoppm -f {p} -l {p} {pdf_path} /tmp/sample_page_{p} -png"
    subprocess.run(cmd1, shell=True)
    img = f"/tmp/sample_page_{p}-{'0' * (len(str(p)) == 3 and 0 or (len(str(p)) == 1 and 2 or 1))}{p}.png"
    # Actually pdftoppm outputs /tmp/sample_page_100-100.png or similar.
    # We can just glob it.
    import glob
    imgs = glob.glob(f"/tmp/sample_page_{p}-*.png")
    if imgs:
        cmd2 = f"tesseract {imgs[0]} stdout -l eng 2>/dev/null | head -n 10"
        res = subprocess.check_output(cmd2, shell=True).decode('utf-8', errors='ignore')
        print(f"=== PAGE {p} ===")
        print(res.strip())
