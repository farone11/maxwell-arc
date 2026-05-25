import gradio as gr
import json
import numpy as np
from solver import MaxwellARCv2

solver = MaxwellARCv2()

ARC_COLORS = np.array([
    [0,   0,   0  ],
    [0,   116, 217],
    [255, 65,  54 ],
    [46,  204, 64 ],
    [255, 220, 0  ],
    [170, 170, 170],
    [240, 18,  190],
    [255, 133, 27 ],
    [127, 219, 255],
    [135, 12,  37 ],
], dtype=np.uint8)

def grid_to_image(grid):
    grid = np.clip(np.array(grid), 0, 9)
    img = ARC_COLORS[grid]
    return np.kron(img, np.ones((25, 25, 1), dtype=np.uint8))

def predict(task_file):
    if not task_file:
        return None

    if not task_file.name.endswith('.json'):
        raise gr.Error("File harus berformat .json")

    with open(task_file.name, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            raise gr.Error("File JSON tidak valid.")

    output_grid = solver.solve(data['train'], data['test'][0]['input'])
    return grid_to_image(output_grid)

with gr.Blocks(title="Maxwell-ARC v2") as demo:
    gr.Markdown("""
# Maxwell-ARC v2
**52.3% ARC-AGI-2**

---
👤 **Dibuat oleh:** [FarOneCapital](https://github.com/farone11/maxwell-arc)  
🔗 **GitHub:** [github.com/farone11/maxwell-arc](https://github.com/farone11/maxwell-arc)
---
""")

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Upload ARC Task JSON", file_types=[".json"])
            btn = gr.Button("Run", variant="primary", size="lg")

        with gr.Column(scale=2):
            output_img = gr.Image(
                label="Predicted Output",
                height=400,
                interactive=False,
            )

    btn.click(fn=predict, inputs=file_input, outputs=output_img)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, ssr_mode=False)
