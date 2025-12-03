import gradio as gr
import time
import threading

# GLOBAL autoplay flag
autoplay_flag = {"running": False}


# Generate step-by-step search data
def generate_steps(arr_str, target_str):
    # Validate and parse array
    try:
        arr = [int(x.strip()) for x in arr_str.split(",") if x.strip()]
    except:
        return [], 0, "Error: List must contain only integers."

    # Validate target
    if target_str.strip() == "":
        return [], 0, "Error: Target is required."

    try:
        target = int(target_str)
    except:
        return [], 0, "Error: Target must be an integer."

    steps = []

    # Create visualization for each step
    for i, val in enumerate(arr):
        visual_boxes = []
        for j, v in enumerate(arr):
            if i == j:
                visual_boxes.append(
                    f"<span style='background-color:#90EE90;padding:6px;border-radius:5px;font-weight:bold'>{v}</span>"
                )
            else:
                visual_boxes.append(
                    f"<span style='padding:6px;border:1px solid #ccc;border-radius:5px'>{v}</span>"
                )

        explanation = f"Step {i+1}: Compare target ({target}) with arr[{i}] = {val}"

        if val == target:
            explanation += "<br><br><b>✔ Target found!</b>"
            steps.append((" ".join(visual_boxes), explanation))
            return steps, 0, ""

        steps.append((" ".join(visual_boxes), explanation))

    # If not found
    steps.append((
        " ".join([f"<span style='padding:6px;border:1px solid #ccc;border-radius:5px'>{v}</span>" for v in arr]),
        "<b>✘ Target not found in the list.</b>"
    ))

    return steps, 0, ""


# Update which step to show
def update_step(step_index, steps):
    if not steps:
        return "", "", 0

    step_index = max(0, min(step_index, len(steps)-1))
    visual, explain = steps[step_index]
    return visual, explain, step_index


# AUTOPLAY LOOP (threaded)
def autoplay_loop(steps, state_index, visual_output, explanation_output, update_fn):
    while autoplay_flag["running"]:
        time.sleep(1)

        # Stop if no steps
        if not steps:
            break

        # If reached last step → stop autoplay
        if state_index["value"] >= len(steps) - 1:
            autoplay_flag["running"] = False
            break

        # Move to next step
        state_index["value"] += 1
        visual, explain, idx = update_fn(state_index["value"], steps)

        visual_output.update(visual)
        explanation_output.update(explain)


# Start Autoplay
def start_autoplay(steps, state_index):
    autoplay_flag["running"] = True

    # Run loop in background thread
    t = threading.Thread(
        target=autoplay_loop,
        args=(steps, state_index, visual_output, explanation_output, update_step),
        daemon=True
    )
    t.start()

    return "▶ Playing..."


# Pause autoplay
def pause_autoplay():
    autoplay_flag["running"] = False
    return "⏸ Paused"


# Reset autoplay and steps
def reset_steps():
    autoplay_flag["running"] = False
    return 0, "🔄 Reset. Click Play to start again."


# -----------------------------
#        UI
# -----------------------------

with gr.Blocks() as demo:
    gr.Markdown("# 🔍 Linear Search Visualizer (Auto-Play Enabled)")
    gr.Markdown("Now includes auto-play animation + default starting array.")

    # Inputs with DEFAULT VALUES
    with gr.Row():
        arr_input = gr.Textbox(
            label="List (comma-separated)",
            value="4, 1, 9, 2, 7",
        )
        target_input = gr.Textbox(
            label="Target",
            value="9",
        )

    generate_btn = gr.Button("Generate Steps")

    visual_output = gr.HTML("")
    explanation_output = gr.HTML("")

    # Navigation Buttons
    with gr.Row():
        prev_btn = gr.Button("⬅ Previous")
        play_btn = gr.Button("▶ Play")
        pause_btn = gr.Button("⏸ Pause")
        reset_btn = gr.Button("🔄 Reset")
        next_btn = gr.Button("Next ➡")

    # State variables
    state_steps = gr.State([])
    state_index = gr.State(0)

    # Generate Steps
    generate_btn.click(
        generate_steps,
        inputs=[arr_input, target_input],
        outputs=[state_steps, state_index, explanation_output],
    ).then(
        update_step,
        inputs=[state_index, state_steps],
        outputs=[visual_output, explanation_output, state_index],
    )

    # Previous Step
    prev_btn.click(
        lambda idx: idx - 1,
        inputs=state_index,
        outputs=state_index,
    ).then(
        update_step,
        inputs=[state_index, state_steps],
        outputs=[visual_output, explanation_output, state_index],
    )

    # Next Step
    next_btn.click(
        lambda idx, steps: idx + 1,
        inputs=[state_index, state_steps],
        outputs=state_index,
    ).then(
        update_step,
        inputs=[state_index, state_steps],
        outputs=[visual_output, explanation_output, state_index],
    )

    # Play
    play_btn.click(
        start_autoplay,
        inputs=[state_steps, state_index],
        outputs=explanation_output,
    )

    # Pause
    pause_btn.click(
        pause_autoplay,
        outputs=explanation_output,
    )

    # Reset
    reset_btn.click(
        reset_steps,
        outputs=[state_index, explanation_output],
    )

demo.launch()
