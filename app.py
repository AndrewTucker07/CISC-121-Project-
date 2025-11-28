import gradio as gr

# Linear Search algorithm (returns steps + result)
def linear_search(arr_str, target_str):
    # Input validation
    try:
        arr = [int(x.strip()) for x in arr_str.split(",") if x.strip() != ""]
    except:
        return "Error: Your list must contain only integers separated by commas."

    if target_str.strip() == "":
        return "Error: Please enter a target value."

    try:
        target = int(target_str)
    except:
        return "Error: Target must be an integer."

    steps = []
    for i, value in enumerate(arr):
        steps.append(f"Step {i+1}: Compare target ({target}) with arr[{i}] = {value}")
        if value == target:
            steps.append(f"✔ Target found at index {i}")
            return "\n".join(steps)

    steps.append("✘ Target not found in the list.")
    return "\n".join(steps)


# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🔍 Linear Search Visualizer")
    gr.Markdown("Enter a **list of numbers** and a **target**, and watch Linear Search compare step-by-step.")

    with gr.Row():
        arr_input = gr.Textbox(
            label="List (comma-separated)",
            placeholder="e.g., 3, 10, 5, 8, 2"
        )
        target_input = gr.Textbox(
            label="Target value",
            placeholder="e.g., 8"
        )

    search_btn = gr.Button("Run Linear Search")

    output_box = gr.Textbox(
        label="Search Steps",
        lines=12
    )

    search_btn.click(
        linear_search,
        inputs=[arr_input, target_input],
        outputs=output_box
    )

demo.launch()
