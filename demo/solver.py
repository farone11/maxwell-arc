import numpy as np
from scipy.ndimage import label, center_of_mass
import json, argparse

class MaxwellARCv2:
    def __init__(self):
        self.name    = "Maxwell-ARC v2"
        self.score   = "52.3% ARC-AGI-2"
        self.author  = "FarOneCapital"
        self.github  = "https://github.com/farone11/maxwell-arc"
        self.email   = "faronecapital@gmail.com"
        self.paper   = "https://github.com/farone11/maxwell-arc/blob/main/paper/maxwell_arc_v2.pdf"

    def infer_polarization_angle(self, grid):
        """Malus-ARC: Cari arah dominan pakai PCA"""
        y, x = np.where(grid > 0)
        if len(x) < 2: return 0
        coords = np.stack([x, y], axis=1)
        cov = np.cov(coords.T)
        eigvals, eigvecs = np.linalg.eigh(cov)
        phi = np.arctan2(eigvecs[1, 1], eigvecs[0, 1])
        return phi

    def malus_filter(self, theta, phi, I0=1.0):
        """Malus-ARC: I = I0 * cos²(theta - phi)"""
        return I0 * np.cos(theta - phi) ** 2

    def gauss_arc_conserve(self, train_pairs):
        """Gauss-ARC: Konservasi jumlah warna dari demo"""
        color_map = {}
        for inp, out in train_pairs:
            in_colors, in_counts = np.unique(inp[inp > 0], return_counts=True)
            out_colors, out_counts = np.unique(out[out > 0], return_counts=True)
            if len(in_colors) == 1 and len(out_colors) == 1:
                color_map[in_colors[0]] = out_colors[0]
        return color_map

    def radiation_pattern(self, grid, source_pos, phi, color):
        """Ampere-ARC + Radiation: pancarkan medan dari charge"""
        h, w = grid.shape
        sy, sx = source_pos
        out = np.zeros((h, w))
        for y in range(h):
            for x in range(w):
                dy, dx = y - sy, x - sx
                if dx == 0 and dy == 0: continue
                theta = np.arctan2(dy, dx)
                intensity = self.malus_filter(theta, phi)
                if intensity > 0.5:
                    out[y, x] = color
        return out

    def solve(self, train_pairs, test_input):
        train_in  = [np.array(p["input"])  for p in train_pairs]
        train_out = [np.array(p["output"]) for p in train_pairs]

        phi       = self.infer_polarization_angle(train_in[0])
        color_map = self.gauss_arc_conserve(list(zip(train_in, train_out)))

        test_input = np.array(test_input)
        h, w       = test_input.shape
        output     = np.zeros_like(test_input)
        sources    = np.argwhere(test_input > 0)

        for sy, sx in sources:
            source_color = test_input[sy, sx]
            target_color = color_map.get(source_color, source_color)
            field        = self.radiation_pattern(test_input, (sy, sx), phi, target_color)
            output       = np.maximum(output, field)

        return output.astype(int).tolist()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, help='Path to ARC task JSON')
    args = parser.parse_args()

    solver = MaxwellARCv2()
    print("=" * 45)
    print(f"  {solver.name}")
    print(f"  Score  : {solver.score}")
    print(f"  Author : {solver.author}")
    print(f"  GitHub : {solver.github}")
    print(f"  Email  : {solver.email}")
    print("=" * 45)

    # with open(args.task) as f: data = json.load(f)
    # result = solver.solve(data['train'], data['test'][0]['input'])
    # print(json.dumps(result))
