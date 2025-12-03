import gradio as gr
import asyncio

# -----------------------------
# Helper logic
# -----------------------------
def generate_steps(arr_str, target_str):
    """
    Returns: (steps_list, index_start, message)
    steps_list: list of tuples (html_visual, html_explanation)
    """
    # Validate and parse array
    try:
        arr = [int(x.strip()) for x in arr_str.split(",") if x.strip() != ""]
    except Exception:
        return [], 0, "Error: List must contain only integers separated by commas."

    # Validate target
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
                # highlighted current index
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
            return steps, 0, ""  # return early on found

        steps.append((" ".join(visual_boxes), explanation))

    # Not found step
    steps.append((
        " ".join([f"<span style='padding:8px;border:1px solid #ddd;border-radius:6px;margin:2px;display:inline-block'>{v}</span>" for v in arr]),
        "<b>✘ Target not found in the list.</b>"
    ))
    return steps, 0, ""


def clamp_index(i, steps):
    if not steps:
        return 0
    return max(0, min(i, len(steps) - 1))


def update_step(step_index, steps):
    """
    Regular synchronous updater used by Prev/Next/Generate/Reset.
    Returns (visual_html, explanation_html, new_index)
    """
    if not steps:
        return "", "", 0
    step_index = clamp_index(step_index, steps)
    visual, explain = steps[step_index]
    return visual, explain, step_index


# -----------------------------
# Async autoplay generator
# -----------------------------
async def play_generator(steps, current_index, autoplay_flag):
    """
    Async generator that yields UI updates (visual_html, explanation_html, index)
    It checks autoplay_flag (a boolean). If autoplay_flag is False, it stops.
    """
    # If nothing to play, return nothing
    if not steps:
        yield "", "", 0
        return

    i = clamp_index(current_index, steps)

    # If starting point is already at last step, just yield the current step
    if i >= len(steps):
        i = len(steps) - 1

    # Keep looping while autoplay_flag is True and we haven't hit the end
    while True:
        # If autoplay flag was turned off externally, stop playing
        if not autoplay_flag:
            # yield the current state so UI shows where we paused
            visual, explain = steps[i]
            yield visual, explain, i
            return

        # Show the current step
        visual, explain = steps[i]
        yield visual, explain, i

        # If last step, stop after showing it
        if i >= len(steps) - 1:
            return

        # wait before next step
        await asyncio.sleep(1.0)

        # advance index
        i += 1


# -----------------------------
# Gradio UI
# -----------------------------
with gr.Blocks(title="Linear Search Visualizer (Autoplay)") as demo:
    gr.Markdown("# 🔍 Linear Search Visualizer")
    gr.Markdown("Default array and target are loaded on start — change them if you want. Use Play/Pause/Next/Previous/Reset to control the animation.")

    # Inputs with defaults
    with gr.Row():
        arr_input = gr.Textbox(label="List (comma-separated)", value="4, 1, 9, 2, 7")
        target_input = gr.Textbox(label="Target", value="9")

    # Control buttons
    with gr.Row():
        generate_btn = gr.Button("Generate Steps")
        prev_btn = gr.Button("⬅ Previous")
        play_btn = gr.Button("▶ Play")
        pause_btn = gr.Button("⏸ Pause")
        reset_btn = gr.Button("🔄 Reset")
        next_btn = gr.Button("Next ➡")

    # Visual outputs
    visual_output = gr.HTML(value="")
    explanation_output = gr.HTML(value="")

    # State holders
    state_steps = gr.State([])          # list of steps
    state_index = gr.State(0)           # current index (int)
    state_autoplay = gr.State(False)    # autoplay flag (bool)

    # Generate steps handler
    def on_generate(arr_s, tgt_s):
        steps, idx, msg = generate_steps(arr_s, tgt_s)
        # If error, clear visuals and return message in explanation
        if msg:
            return [], 0, "", msg
        # return steps, index, visual_html, explanation_html
        visual, explain = ("", "")
        if steps:
            visual, explain = steps[0]
        return steps, 0, visual, explain

    generate_btn.click(
        fn=on_generate,
        inputs=[arr_input, target_input],
        outputs=[state_steps, state_index, visual_output, explanation_output]
    )

    # Prev button
    def on_prev(idx, steps):
        if not steps:
            return "", "", 0
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
        if not steps:
            return "", "", 0
        new_idx = clamp_index(idx + 1, steps)
        visual, explain = steps[new_idx]
        return visual, explain, new_idx

    next_btn.click(
        fn=on_next,
        inputs=[state_index, state_steps],
        outputs=[visual_output, explanation_output, state_index]
    )

    # Reset button: stop autoplay and go to 0
    def on_reset():
        return [], 0, "", ""  # clear steps, reset index, clear visuals/explanation

    reset_btn.click(
        fn=on_reset,
        outputs=[state_steps, state_index, visual_output, explanation_output]
    )

    # Pause button: sets autoplay flag to False
    def do_pause():
        return False, "<b>⏸ Paused</b>"

    pause_btn.click(
        fn=do_pause,
        outputs=[state_autoplay, explanation_output]
    )

    # Play button: first set autoplay flag True, then chain to the async generator
    def start_play_flag():
        # this sets the shared flag to True; the .then() will call the generator
        return True, "<b>▶ Playing...</b>"

    play_btn.click(
        fn=start_play_flag,
        outputs=[state_autoplay, explanation_output]
    ).then(
        # call the async generator to actually stream updates
        fn=play_generator,
        inputs=[state_steps, state_index, state_autoplay],
        outputs=[visual_output, explanation_output, state_index]
    )

    # When page loads, generate the default steps so something is visible immediately
    def initial_load(arr_s, tgt_s):
        steps, idx, msg = generate_steps(arr_s, tgt_s)
        if msg:
            return [], 0, "", msg
        visual, explain = ("", "")
        if steps:
            visual, explain = steps[0]
        return steps, 0, visual, explain

    demo.load(
        fn=initial_load,
        inputs=[arr_input, target_input],
        outputs=[state_steps, state_index, visual_output, explanation_output]
    )

demo.launch()
