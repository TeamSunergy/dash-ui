from kivy.graphics import Color


def hex_to_rgb(hex_color):
    # Convert HEX color code to red, green, and blue rgb values
    if hex_color[:1] == '#':
        hex_color = hex_color.lstrip('#')

    r, g, b = bytes.fromhex(hex_color)
    return (
         float(format(r / 255.0, '.1f')),
         float(format(g / 255.0, '.1f')),
         float(format(b / 255.0, '.1f')),
         1.0) # alpha


def setup_colors(colors_hex):
    """
    colors = {}
    colors_hex = {
                  'white': '#ffffff',
                  'red': '#000000',
                  'green': '#111111',
                  'gray_0': '#222222',
                  'gray_1': '#232323',
                  'yellow': '#333333',
                  'blue': '#444444'}

    """

    for key, color in colors_hex.items():
        colors[key] = Color(hex_to_rgb(color))
        # print(colors[key])

    #print(colors)