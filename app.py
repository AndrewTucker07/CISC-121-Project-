import gradio as gr

# Generate search steps (list + explanation)
def generate_steps(arr_str, target_str):
    # Validate input
    try:
        arr = [int(x.strip()) for x in arr_str.split(",") if x.strip() != ""]
    except:
        return [], "Error: Your list must contain only integers."

    if target_str.strip() == "":
        return [], "Error: Target is required."

    try:
        target = int(target_str)
    except:
        return [], "Error: Target must be an integer."

    steps = []
    for i, val in enumerate(arr):
        visual = []
        for j, v in enumerate(arr):
            if i == j:
                visual.append(f"🟩 **{v}**")  # Highlight current index
            else:
                visual.append(f"⬜ {v}")

        explanation = f"Step {i+1}: Compare target ({target}) with arr[{i}] = {val}"

        if val == target:
            explanation += "\n\n✔ **Target found!**"
            steps.append((visual, explanation))
            break

        steps.append((visual, explanation))

    if steps and arr[steps[-1][0].index(f'🟩 **{arr[-1]}**')] != target:
        steps.append(([f"⬜ {v}" for v in arr], "✘ Target not found."))

    return steps, ""


# Update step on button click
def update_step(step_index, steps):
    if not steps:
        return "", ""

    step_index = max(0, min(step_index, len(steps)-1))

    visual_boxes = " ".join(steps[step_index][0])
    explanation = steps[step_index][1]

    return visual_boxes, explanation, step_index


# Store steps globally in the session
state_steps = gr.State([])
state_index = gr.State(0)


with gr.Blocks() as demo:
    gr.Markdown("# 🔍 Linear Search Visualizer")
    gr.Markdown("Step-by-step animation with arrows to move forward/backward.")

    with gr.Row():
        arr_input = gr.Textbox(label="List (comma-separated)", placeholder="e.g., 4, 1, 9, 2")
        target_input = gr.Textbox(label="Target", placeholder="e.g., 9")

    generate_btn = gr.Button("Generate Steps")

    visual_output = gr.Markdown("⬜ No data yet")
    explanation_output = gr.Markdown("")

    with gr.Row():
        prev_btn = gr.Button("⬅ Previous")
        next_btn = gr.Button("Next ➡")

    # Generate all steps
    generate_btn.click(
        generate_steps,
        inputs=[arr_input, target_input],
        outputs=[state_steps, explanation_output]
    ).then(
        update_step,
        inputs=[state_index, state_steps],
        outputs=[visual_output, explanation_output, state_index]
    )

    # Previous button
    prev_btn.click(
        lambda i: max(i - 1, 0),
        inputs=state_index,
        outputs=state_index
    ).then(
        update_step,
        inputs=[state_index, state_steps],
        outputs=[visual_output, explanation_output, state_index]
    )

    # Next button
    next_btn.click(
        lambda i, steps: min(i + 1, len(steps) - 1),
        inputs=[state_index, state_steps],
        outputs=state_index
    ).then(
        update_step,
        inputs=[state_index, state_steps],
        outputs=[visual_output, explanation_output, state_index]
    )

demo.launch()
