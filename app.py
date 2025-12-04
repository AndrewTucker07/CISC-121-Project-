import gradio as gr
import asyncio

# -----------------------------
# Helper logic
# -----------------------------
def generate_steps(arr_str, target_str):
    try:
        arr = [int(x.strip()) for x in arr_str.split(",") if x.strip() != ""]
    except:
        return [], 0, "Error: List must contain only integers separated by commas."

    if target_str.strip() == "":
        return [], 0, "Error: Target is required."

    try:
        target = int(target_str)
    except:
        return [], 0, "Error: Target must be an integer."

    steps = []

    for i, val in enumerate(arr):

        # Build arrow row
        arrow_row = []
        for j in range(len(arr)):
            arrow_row.append(
                "<span style='font-size:28px; width:40px; display:inline-block; text-align:center;'>"
                + ("⬇" if i == j else "")
                + "</span>"
            )

        # Build number row
        box_row = []
        for j, v in enumerate(arr):
            if i == j:
                box_row.append(
                    f"""
                    <span class='fade-step' style="
                        background:#90EE90;
                        padding:10px;
                        border-radius:8px;
                        margin:4px;
                        display:inline-block;
                        font-weight:800;
                        transition: all 0.4s ease;">
                        {v}
                    </span>
                    """
                )
            else:
                box_row.append(
                    f"""
                    <span class='fade-step' style="
                        padding:10px;
                        border:1px solid #ddd;
                        border-radius:8px;
                        margin:4px;
                        display:inline-block;
                        transition: all 0.4s ease;">
                        {v}
                    </span>
                    """
                )

        html_visual = f"""
        <div style="text-align:center;">
            {''.join(arrow_row)}
            <br>
            {''.join(box_row)}
        </div>
        """

        explanation = f"Step {i+1}: Compare target ({target}) with arr[{i}] = {val}"

        if val == target:
            explanation += "<br><br><b>✔ Target found!</b>"
            steps.append((html_visual, explanation))
            return steps, 0, ""

        steps.append((html_visual, explanation))

    # Not found
    final_row = "".join(
        f"<span class='fade-step' style='padding:10px;border:1px solid #ddd;border-radius:8px;margin:4px;display:inline-block;'>{v}</span>"
        for v in arr
    )

    steps.append((
        f"<div style='text-align:center;'>{final_row}</div>",
        "<b>✘ Target not found in the list.</b>"
    ))

    return steps, 0, ""


def clamp_index(i, steps):
    if not steps:
        return 0
    return max(0, min(i, len(steps) - 1))


# -----------------------------
# Autoplay generator
# -----------------------------
async def play_generator(steps, current_index):
    if not steps:
        yield "", "", 0
        return

    i = clamp_index(current_index, steps)

    while i < len(steps):
        visual, explain = steps[i]
        yield visual, explain, i
        i += 1
        await asyncio.sleep(1)


# -----------------------------
# UI
# -----------------------------
with gr.Blocks(title="Linear Search Visualizer") as demo:
    gr.Markdown("""
    <style>
    .fade-step {
        opacity: 0;
        animation: fadeIn 0.6s forwards;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>

    # 🔍 Linear Search Visualizer  
    Now with **arrow animation** + **smooth fading transitions**!
    """)

    # Inputs
    with gr.Row():
        arr_input = gr.Textbox(label="List (comma-separated)", value="4, 1, 9, 2, 7")
        target_input = gr.Textbox(label="Target", value="9")

    # Controls
    with gr.Row():
        generate_btn = gr.Button("Generate Steps")
        prev_btn = gr.Button("⬅ Previous")
        play_btn = gr.Button("▶ Play")
        next_btn = gr.Button("Next ➡")

    visual_output = gr.HTML("")
    explanation_output = gr.HTML("")

    state_steps = gr.State([])
    state_index = gr.State(0)

    # Generate steps
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

    # Prev
    def on_prev(idx, steps):
        if not steps:
            return "", "", 0
        new_idx = clamp_index(idx - 1, steps)
        return steps[new_idx][0], steps[new_idx][1], new_idx

    prev_btn.click(
        on_prev,
        [state_index, state_steps],
        [visual_output, explanation_output, state_index]
    )

    # Next
    def on_next(idx, steps):
        if not steps:
            return "", "", 0
        new_idx = clamp_index(idx + 1, steps)
        return steps[new_idx][0], steps[new_idx][1], new_idx

    next_btn.click(
        on_next,
        [state_index, state_steps],
        [visual_output, explanation_output, state_index]
    )

    # Play
    play_btn.click(
        lambda: None,
        None,
        None
    ).then(
        play_generator,
        inputs=[state_steps, state_index],
        outputs=[visual_output, explanation_output, state_index]
    )

    # Load defaults
    def initial_load(arr_s, tgt_s):
        steps, idx, msg = generate_steps(arr_s, tgt_s)
        if msg:
            return [], 0, "", msg
        visual, explain = steps[0]
        return steps, 0, visual, explain

    demo.load(
        initial_load,
        inputs=[arr_input, target_input],
        outputs=[state_steps, state_index, visual_output, explanation_output]
    )

demo.launch()
