"""Verifica que reanudar una corrida conserva su trayectoria y sus registros."""
import csv
import hashlib
import json
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import torch
from build_dataset import draw_creature


class TrainingRecovery(unittest.TestCase):
    def test_resume_matches_uninterrupted_training(self):
        project = Path(__file__).resolve().parents[1]
        (project / "tmp").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=project / "tmp", prefix="training_check_") as directory:
            root = Path(directory)
            data = root / "data" / "processed"
            data.mkdir(parents=True)
            raw = root / "data/raw"
            raw.mkdir()
            records = []
            rng = random.Random(42)
            for index in range(8):
                image, traits = draw_creature(rng)
                image.save(data / f"{index}.png")
                records.append({"sha256_pixels": hashlib.sha256(image.tobytes()).hexdigest(), **traits})
            (raw / "manifest.json").write_text(json.dumps({"images": records}), encoding="utf-8")
            common = [sys.executable, str(project / "train.py"), "--data", str(data),
                      "--out", str(root / "runs"), "--bs", "4", "--nz", "8", "--ngf", "4",
                      "--ndf", "4", "--threads", "1", "--ckpt_every", "1",
                      "--g_arch", "resize", "--moment_weight", "10", "--conditional", "--reconstruction_weight", "10",
                      "--eye_weight", "15"]
            subprocess.run([*common, "--name", "full", "--epochs", "2"], check=True, capture_output=True)
            subprocess.run([*common, "--name", "split", "--epochs", "1"], check=True, capture_output=True)
            split = root / "runs/split"
            config_path = split / "config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["epochs"] = 2
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with (split / "losses.csv").open("a", encoding="utf-8") as stream:
                stream.write("999,2,0,0,0,0\n")
            with (split / "metrics.csv").open("a", encoding="utf-8") as stream:
                stream.write("2,0,0,0,0,0,0\n")
            with (split / "regularization.csv").open("a", encoding="utf-8") as stream:
                stream.write("999,2,0,0,0\n")
            subprocess.run([*common, "--name", "split", "--epochs", "2", "--resume"],
                           check=True, capture_output=True)
            full = torch.load(root / "runs/full/ckpt/last.pt", weights_only=False, map_location="cpu")
            recovered = torch.load(split / "ckpt/last.pt", weights_only=False, map_location="cpu")
            for network in ["G", "D"]:
                for key, tensor in full[network].items():
                    self.assertTrue(torch.equal(tensor, recovered[network][key]), f"{network}.{key}")
            def rows(path):
                with path.open(newline="", encoding="utf-8") as stream:
                    return list(csv.DictReader(stream))
            self.assertEqual(rows(root / "runs/full/losses.csv"), rows(split / "losses.csv"))
            self.assertEqual(rows(root / "runs/full/regularization.csv"), rows(split / "regularization.csv"))
            self.assertEqual([int(row["epoch"]) for row in rows(split / "metrics.csv")], [0, 1, 2])
            refused = subprocess.run([*common, "--name", "full", "--epochs", "2"], capture_output=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn(b"FileExistsError", refused.stderr)


if __name__ == "__main__":
    unittest.main()
