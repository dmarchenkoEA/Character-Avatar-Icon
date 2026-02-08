"""
Interactive UI for tweaking avatar compositor settings.
"""

import gradio as gr
from avatar_compositor import composite_avatar, PortalGradient, AvatarConfig


def generate_avatar(
    character_image,
    fill_type,
    fill_image,
    gradient_start,
    gradient_end,
    character_scale,
    character_rotation,
    character_x_offset,
    character_y_offset,
    mask_x_offset,
    mask_y_offset,
    portal_x_offset,
    portal_y_offset,
    face_position,
    add_white_bg
):
    if character_image is None:
        return None

    # Determine fill based on fill_type
    if fill_type == "Image" and fill_image is not None:
        fill = fill_image
    else:
        fill = PortalGradient(
            start_color=gradient_start,
            end_color=gradient_end
        )

    # Calculate character size from scale
    base_width, base_height = 408, 731
    char_width = int(base_width * character_scale)
    char_height = int(base_height * character_scale)

    config = AvatarConfig(
        output_size=(340, 341),
        portal_size=(340, 376),
        mask_size=(340, 472),
        portal_offset=(int(portal_x_offset), int(portal_y_offset)),
        mask_offset=(int(mask_x_offset), int(mask_y_offset)),
        character_offset=(int(character_x_offset), int(character_y_offset)),
        character_size=(char_width, char_height),
        character_rotation=character_rotation,
        face_position=face_position
    )

    result = composite_avatar(
        character_source=character_image,
        fill=fill,
        config=config
    )

    # Optionally add white background for preview
    if add_white_bg:
        from PIL import Image
        bg = Image.new("RGBA", result.size, (255, 255, 255, 255))
        result = Image.alpha_composite(bg, result)

    return result


with gr.Blocks(title="Avatar Compositor") as app:
    gr.Markdown("# Avatar Compositor")
    gr.Markdown("Upload a character image and tweak the settings to generate an avatar.")

    with gr.Row():
        with gr.Column(scale=1):
            character_input = gr.Image(type="pil", label="Character Image", image_mode="RGBA")

            gr.Markdown("### Portal Fill")
            fill_type = gr.Radio(["Gradient", "Image"], value="Gradient", label="Fill Type")
            fill_image = gr.Image(type="pil", label="Fill Image (if Image selected)", image_mode="RGB")

            gr.Markdown("### Gradient Colors (if Gradient selected)")
            gradient_start = gr.ColorPicker(value="#CE782D", label="Gradient Start (top-right)")
            gradient_end = gr.ColorPicker(value="#E1A371", label="Gradient End (bottom-left)")

            gr.Markdown("### Character Settings")
            character_scale = gr.Slider(0.5, 3.0, value=1.1, step=0.05, label="Character Scale")
            character_rotation = gr.Slider(-10, 10, value=3.0, step=0.5, label="Rotation (degrees)")
            face_position = gr.Slider(0.0, 1.0, value=0.0, step=0.05, label="Face Position (0=top, 1=bottom)")

            gr.Markdown("### Character Offset")
            character_x_offset = gr.Slider(-150, 150, value=-70, step=1, label="X Offset")
            character_y_offset = gr.Slider(-200, 200, value=-40, step=1, label="Y Offset")

            gr.Markdown("### Mask Offset")
            mask_x_offset = gr.Slider(-100, 100, value=0, step=1, label="Mask X")
            mask_y_offset = gr.Slider(-200, 100, value=-48, step=1, label="Mask Y")

            gr.Markdown("### Portal Offset")
            portal_x_offset = gr.Slider(-100, 100, value=0, step=1, label="Portal X")
            portal_y_offset = gr.Slider(-100, 100, value=38, step=1, label="Portal Y")

            gr.Markdown("### Preview Options")
            add_white_bg = gr.Checkbox(value=True, label="Add white background (for preview)")

        with gr.Column(scale=1):
            output_image = gr.Image(label="Generated Avatar", type="pil")
            generate_btn = gr.Button("Generate Avatar", variant="primary")

    # Connect all inputs to the generate function
    all_inputs = [
        character_input,
        fill_type,
        fill_image,
        gradient_start,
        gradient_end,
        character_scale,
        character_rotation,
        character_x_offset,
        character_y_offset,
        mask_x_offset,
        mask_y_offset,
        portal_x_offset,
        portal_y_offset,
        face_position,
        add_white_bg
    ]

    generate_btn.click(fn=generate_avatar, inputs=all_inputs, outputs=output_image)

    # Auto-generate on any change
    for input_component in all_inputs:
        input_component.change(fn=generate_avatar, inputs=all_inputs, outputs=output_image)


if __name__ == "__main__":
    app.launch()
