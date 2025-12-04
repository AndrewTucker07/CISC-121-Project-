import gradio as gr
import asyncio

# -----------------------------
# Helper logic
# -----------------------------
def generate_steps(arr_str, target_str):
    try:
        arr = [int(x.strip()) for x in arr_str.split(",") if x.strip() != ""]
    except Exception:
        return [], 0, "Error: List must contain only integers separated by commas."

    if target_str.strip() == "":
        return [], 0, "Error: Target is required."

    try:
        target = int(target_str)
    except Exception:
        return [], 0, "Error: Target must be an integer."

    steps = []
    for i, val in enumerate(arr):
        visual_boxes = []
        for j, v in enumerate(arr):
            if i == j:
                visual_boxes.append(
                    f"<span style='background:#90EE90;padding:8px;border-radius:6px;margin:2px;display:inline-block;font-weight:700'>{v}</span>"
                )
            else:
                visual_boxes.append(
                    f"<span style='padding:8px;border:1px solid #ddd;border-radius:6px;margin:2px;display:inline-block'>{v}</span>"
                )

        explanation = f"Step {i+1}: Compare target ({target}) with arr[{i}] = {val}"
        if val == target:
            explanation += "<br><br><b>✔ Target found!</b>"
            steps.append((" ".join(visual_boxes), explanation))
            return steps, 0, ""

        steps.append((" ".join(visual_boxes), explanation))

    steps.append((
        " ".join([f"<span style='padding:8px;border:1px solid #ddd;border-radius:6px;margin:2px;display:inline-block'>{v}</span>" for v in arr]),
        "<b>✘ Target not found.</b>"
    ))
    return steps, 0, ""


def clamp_index(i, steps):
    if not steps:
        return 0
    return max(0, min(i, len(steps) - 1))


# -----------------------------
# Async autoplay generator
# -----------------------------
async def play_generator(steps, current_index):
    if not steps:
        yield "", "", 0
        return

    i = clamp_index(current_index, steps)

    while True:
        visual, explain = steps[i]
        yield visual, explain, i

        if i >= len(steps) - 1:
            return

        await asyncio.sleep(1.0)
        i += 1


# -----------------------------
# Gradio UI
# -----------------------------
with gr.Blocks(title="Linear Search Visualizer (Autoplay)") as demo:
    gr.Markdown("# 🔍 Linear Search Visualizer")
    gr.Markdown("Default array + target are shown automatically. Click **Play** for animation.")

    with gr.Row():
        arr_input = gr.Textbox(label="List", value="4, 1, 9, 2, 7")
        target_input = gr.Textbox(label="Target", value="9")

    with gr.Row():
        generate_btn = gr.Button("Generate Steps")
        prev_btn = gr.Button("⬅ Previous")
        play_btn = gr.Button("▶ Play")
        next_btn = gr.Button("Next ➡")

    visual_output = gr.HTML("")
    explanation_output = gr.HTML("")

    state_steps = gr.State([])
    state_index = gr.State(0)

    # Generate
    def on_generate(arr_s, tgt_s):
        steps, idx, msg = generate_steps(arr_s, tgt_s)
        if msg:
            return [], 0, "", msg
        visual, explain = steps[0]
        return steps, 0, visual, explain

    generate_btn.click(
        on_generate,
        inputs=[arr_input, target_input],
        outputs=[state_steps, state_index, visual_output, explanation_output]
    )

    # Previous
    def on_prev(idx, steps):
        if not steps:
            return "", "", 0
        new = clamp_index(idx - 1, steps)
        return steps[new][0], steps[new][1], new

    prev_btn.click(
        on_prev,
        inputs=[state_index, state_steps],
        outputs=[visual_output, explanation_output, state_index]
    )

    # Next
    def on_next(idx, steps):
        if not steps:
            return "", "", 0
        new = clamp_index(idx + 1, steps)
        return steps[new][0], steps[new][1], new

    next_btn.click(
        on_next,
        inputs=[state_index, state_steps],
        outputs=[visual_output, explanation_output, state_index]
    )

    # Play animation
    play_btn.click(
        fn=play_generator,
        inputs=[state_steps, state_index],
        outputs=[visual_output, explanation_output, state_index]
    )

    # Load default state automatically
    def initial(arr_s, tgt_s):
        steps, idx, msg = generate_steps(arr_s, tgt_s)
        visual, explain = steps[0]
        return steps, 0, visual, explain

    demo.load(
        initial,
        inputs=[arr_input, target_input],
        outputs=[state_steps, state_index, visual_output, explanation_output]
    )

demo.launch()
