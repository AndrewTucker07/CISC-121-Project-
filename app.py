import gradio as gr
import asyncio



def generate_steps(arr_str, target_str):
    # array input
    try:
        arr = [int(x.strip()) for x in arr_str.split(",") if x.strip() != ""]
    except:
        return [], 0, "Error: List must contain only integers separated by commas."

    # Parse target
    if target_str.strip() == "":
        return [], 0, "Error: Target is required."

    try:
        target = int(target_str)
    except:
        return [], 0, "Error: Target must be an integer."

    steps = []

    # Build each search step
    for i, val in enumerate(arr):
        visual_boxes = []

        # Build the array boxes
        for j, v in enumerate(arr):
            if i == j:
                # highlight current index
                visual_boxes.append(
                    f"<span style='background:#90EE90;padding:8px;border-radius:6px;margin:2px;display:inline-block;font-weight:700'>{v}</span>"
                )
            else:
                # normal index
                visual_boxes.append(
                    f"<span style='padding:8px;border:1px solid #ddd;border-radius:6px;margin:2px;display:inline-block'>{v}</span>"
                )

        # Explanation text
        explanation = f"Step {i+1}: Compare target ({target}) with arr[{i}] = {val}"

        # If found
        if val == target:
            explanation += "<br><br><b>✔ Target found!</b>"
            steps.append((" ".join(visual_boxes), explanation))
            return steps, 0, ""

        steps.append((" ".join(visual_boxes), explanation))

    # If not found
    steps.append((
        " ".join([f"<span style='padding:8px;border:1px solid #ddd;border-radius:6px;margin:2px;display:inline-block'>{v}</span>" for v in arr]),
        "<b>✘ Target not found.</b>"
    ))
    return steps, 0, ""


def clamp_index(i, steps):
    # keep index in bounds
    if not steps:
        return 0
    return max(0, min(i, len(steps) - 1))


def update_step(step_index, steps):
    # return current step safely
    if not steps:
        return "", "", 0
    step_index = clamp_index(step_index, steps)
    visual, explain = steps[step_index]
    return visual, explain, step_index



# Autoplay generator

async def play_generator(steps, current_index, autoplay_flag):
    # no steps → show nothing
    if not steps:
        yield "", "", 0
        return

    i = clamp_index(current_index, steps)

    # loop through steps while autoplay is on
    while True:

        # if autoplay turned off → stop
        if not autoplay_flag:
            visual, explain = steps[i]
            yield visual, explain, i
            return

        # show current step
        visual, explain = steps[i]
        yield visual, explain, i

        # stop at end
        if i >= len(steps) - 1:
            return

        await asyncio.sleep(1.0)   # wait 1 second
        i += 1                      # move to next step


# Gradio UI

with gr.Blocks(title="Linear Search Visualizer (Autoplay)") as demo:
    gr.Markdown("# 🔍 Linear Search Visualizer")
    gr.Markdown("Default array and target load automatically.")

    # Default values
    with gr.Row():
        arr_input = gr.Textbox(label="List", value="4, 1, 9, 2, 7")
        target_input = gr.Textbox(label="Target", value="9")

    # Buttons
    with gr.Row():
        generate_btn = gr.Button("Generate Steps")
        prev_btn = gr.Button("⬅ Previous")
        play_btn = gr.Button("▶ Play")
        next_btn = gr.Button("Next ➡")

    # Outputs
    visual_output = gr.HTML(value="")
    explanation_output = gr.HTML(value="")

    # State
    state_steps = gr.State([])
    state_index = gr.State(0)
    state_autoplay = gr.State(False)

    # Generate steps
    def on_generate(arr_s, tgt_s):
        steps, idx, msg = generate_steps(arr_s, tgt_s)

        if msg:
            return [], 0, "", msg

        # show first step
        visual, explain = steps[0] if steps else ("", "")
        return steps, 0, visual, explain

    generate_btn.click(
        fn=on_generate,
        inputs=[arr_input, target_input],
        outputs=[state_steps, state_index, visual_output, explanation_output]
    )

    # Previous button
    def on_prev(idx, steps):
        if not steps: return "", "", 0
        new_idx = clamp_index(idx - 1, steps)
        visual, explain = steps[new_idx]
        return visual, explain, new_idx

    prev_btn.click(
        fn=on_prev,
        inputs=[state_index, state_steps],
        outputs=[visual_output, explanation_output, state_index]
    )

    # Next button
    def on_next(idx, steps):
        if not steps: return "", "", 0
        new_idx = clamp_index(idx + 1, steps)
        visual, explain = steps[new_idx]
        return visual, explain, new_idx

    next_btn.click(
        fn=on_next,
        inputs=[state_index, state_steps],
        outputs=[visual_output, explanation_output, state_index]
    )


    # Play button
    def start_play_flag():
        return True, "<b>▶ Playing...</b>"

    play_btn.click(
        fn=start_play_flag,
        outputs=[state_autoplay, explanation_output]
    ).then(
        fn=play_generator,
        inputs=[state_steps, state_index, state_autoplay],
        outputs=[visual_output, explanation_output, state_index]
    )

    # Load default steps on startup
    def initial_load(arr_s, tgt_s):
        steps, idx, msg = generate_steps(arr_s, tgt_s)
        if msg:
            return [], 0, "", msg
        visual, explain = steps[0] if steps else ("", "")
        return steps, 0, visual, explain

    demo.load(
        fn=initial_load,
        inputs=[arr_input, target_input],
        outputs=[state_steps, state_index, visual_output, explanation_output]
    )

demo.launch()
