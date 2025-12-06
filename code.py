import board, displayio, time, gc, random, math, rgbmatrix, framebufferio, digitalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label

displayio.release_displays()

# Setup for Matrix Portal M4
matrix = rgbmatrix.RGBMatrix(
    width=64,  # Change width & height if you have an LED matrix with different dimensions
    height=32,
    bit_depth=6,
    rgb_pins=[
        board.MTX_R1,
        board.MTX_G1,
        board.MTX_B1,
        board.MTX_R2,
        board.MTX_G2,
        board.MTX_B2
    ],
    addr_pins=[
        board.MTX_ADDRA,
        board.MTX_ADDRB,
        board.MTX_ADDRC,
        board.MTX_ADDRD
    ],
    clock_pin=board.MTX_CLK,
    latch_pin=board.MTX_LAT,
    output_enable_pin=board.MTX_OE,
    tile=1,
    serpentine=False,
    doublebuffer=True,
)

display = framebufferio.FramebufferDisplay(matrix)
# end of Matrix Portal M4 setup

# Button Setup
button = digitalio.DigitalInOut(board.A1)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP  # Pull-up resistor (button press = False)

# Display state
display_on = True
waiting_for_click = False  # Track if we're waiting for a click to show next phrase
current_phrase = None  # Store the current phrase to repeat

WIDTH = display.width
HEIGHT = display.height

main_group = displayio.Group()
display.root_group = main_group

# Fonts
font_small = bitmap_font.load_font("/fonts/helvB08.bdf")
font_large = bitmap_font.load_font("/fonts/helvB12.bdf")

# COLOR VARIABLES
WHITE = 0xFFFFFF
SOFT_RED = 0xCC4444
DEEP_CORAL = 0xFF6F61
PEACH = 0xFFDAB9
WARM_GOLD = 0xFFD700
GOLDENROD = 0xDAA520
TANGERINE = 0xFFA07A

# Lean firework colors toward warm tones
firework_colors = [WHITE, GOLDENROD, WARM_GOLD, DEEP_CORAL, SOFT_RED, TANGERINE]

celebration_colors = [
    WHITE, GOLDENROD, WARM_GOLD, DEEP_CORAL,
    SOFT_RED, TANGERINE, PEACH
]

# Timing Parameters
SCROLL_DELAY = 0.025
SCROLL_STEP = 1

intro_message = ("Rise and Shine Eagle! Today's motivational words are...", "", "/graphics/baldwineagle.bmp", GOLDENROD)

motivational_phrases = [
    "You've got this today",
    "Believe in your strength",
    "Small steps create success",
    "Choose progress over perfection",
    "Your effort matters today",
    "Rise ready to learn",
    "You are capable always",
    "Show up for you",
    "Today is your opportunity",
    "Keep moving with purpose",
    "Let your courage lead",
    "Be kind to yourself",
    "Focus, breathe, and begin",
    "Work hard, stay hopeful",
    "Your mindset shapes today"
]


def create_scroll_group(logo_path, text1, text2, color=None):
    group = displayio.Group()
    logo_width = 0
    logo_spacing = 33
    logo_tilegrid = None

    if color:
        color1 = color
        color2 = color
    else:
        color1 = random.choice(celebration_colors)
        color2 = random.choice([c for c in celebration_colors if c != color1])

    if logo_path:
        try:
            logo_bitmap = displayio.OnDiskBitmap(logo_path)
            logo_tilegrid = displayio.TileGrid(
                logo_bitmap,
                pixel_shader=logo_bitmap.pixel_shader,
                x=2,
                y=0
            )
            group.append(logo_tilegrid)
            logo_width = logo_tilegrid.width
        except Exception as e:
            print(f"Error loading image {logo_path}: {e}")

    text_start = logo_width + logo_spacing if logo_path else 0

    if text2.strip() == "":
        label1 = Label(font_large, text=text1, color=color1)
        label1.x = text_start
        label1.y = 16
        group.append(label1)
        text_width = label1.bounding_box[2]
    else:
        label1 = Label(font_small, text=text1, color=color1)
        label1.x = text_start
        label1.y = 10
        group.append(label1)

        label2 = Label(font_small, text=text2, color=color2)
        label2.x = text_start
        label2.y = 22
        group.append(label2)

        text_width = max(
            label1.bounding_box[2],
            label2.bounding_box[2]
        )

    total_width = text_start + text_width

    # Adds second logo directly after text
    if logo_path and logo_tilegrid:
        try:
            logo_bitmap = displayio.OnDiskBitmap(logo_path)
            second_logo = displayio.TileGrid(
                logo_bitmap,
                pixel_shader=logo_bitmap.pixel_shader,
                x=text_start + text_width,
                y=0
            )
            group.append(second_logo)
            total_width += second_logo.width + 1
        except Exception as e:
            print(f"Error loading second logo image: {e}")

    return group, total_width


def screen_fill_animation(duration=4.0):
    # Sparkly Red and Yellow Horizontal Stripes with Eagle Logo
    print("Sparkly Red and Yellow Stripes Animation with Eagle")
    animation_group = displayio.Group()
    main_group.append(animation_group)

    # Bright red and yellow colors
    RED = 0xFF0000
    YELLOW = 0xFFFF00

    stripe_height = 4

    # Create alternating red and yellow stripes and store them
    stripes = []
    for y in range(0, HEIGHT, stripe_height):
        # Alternate between red and yellow
        base_color = RED if (y // stripe_height) % 2 == 0 else YELLOW

        # Create stripe bitmap
        stripe_bmp = displayio.Bitmap(WIDTH, stripe_height, 1)
        stripe_pal = displayio.Palette(1)
        stripe_pal[0] = base_color
        stripe_tile = displayio.TileGrid(stripe_bmp, pixel_shader=stripe_pal, x=0, y=y)
        animation_group.append(stripe_tile)

        stripes.append({
            'palette': stripe_pal,
            'base_color': base_color,
            'brightness': 1.0
        })

    # Add eagle logo centered on top of stripes
    try:
        eagle_bitmap = displayio.OnDiskBitmap("/graphics/baldwineagle.bmp")
        eagle_width = eagle_bitmap.width
        eagle_height = eagle_bitmap.height

        # Center the eagle
        eagle_x = (WIDTH - eagle_width) // 2
        eagle_y = (HEIGHT - eagle_height) // 2

        eagle_tile = displayio.TileGrid(
            eagle_bitmap,
            pixel_shader=eagle_bitmap.pixel_shader,
            x=eagle_x,
            y=eagle_y
        )
        animation_group.append(eagle_tile)
    except Exception as e:
        print(f"Error loading eagle image: {e}")

    # Display the stripes with sparkle effect
    start_time = time.monotonic()
    frame = 0
    while time.monotonic() - start_time < duration:
        # Check button during animation
        button_action = check_for_quick_click()
        if button_action == "click":
            main_group.remove(animation_group)
            gc.collect()
            return "new_phrase"
        elif button_action == "toggle" and not display_on:
            break

        frame += 1

        # Create sparkle effect by varying brightness of stripes
        for i, stripe in enumerate(stripes):
            # Random sparkle: occasionally brighten or dim stripes
            if random.random() < 0.15:  # 15% chance per frame
                stripe['brightness'] = random.uniform(0.6, 1.0)
            else:
                # Gradually return to full brightness
                stripe['brightness'] = min(1.0, stripe['brightness'] + 0.05)

            # Apply brightness to color
            r = int(((stripe['base_color'] >> 16) & 0xFF) * stripe['brightness'])
            g = int(((stripe['base_color'] >> 8) & 0xFF) * stripe['brightness'])
            b = int((stripe['base_color'] & 0xFF) * stripe['brightness'])
            stripe['palette'][0] = (r << 16) | (g << 8) | b

        time.sleep(0.05)

    # Clean up
    main_group.remove(animation_group)
    gc.collect()
    return None


def check_for_quick_click():
    global display_on

    if not button.value:  # Button pressed
        press_start = time.monotonic()

        # Wait for release or check if it becomes a long hold
        while not button.value:
            elapsed = time.monotonic() - press_start

            # If held for 3 seconds, toggle display
            if elapsed >= 3.0:
                display_on = not display_on
                if display_on:
                    print("*** Display turned ON ***")
                    display.brightness = 1.0
                else:
                    print("*** Display turned OFF ***")
                    display.brightness = 0.0

                # Wait for release
                while not button.value:
                    time.sleep(0.1)

                return "toggle"

            time.sleep(0.05)

        # Button was released - check how long it was held
        hold_time = time.monotonic() - press_start
        if hold_time < 3.0:
            # It was a quick click!
            print(f"Button clicked! (held for {hold_time:.2f}s)")
            time.sleep(0.2)  # Debounce
            return "click"

    return None


def wait_for_single_click():
    global waiting_for_click
    print("Waiting for button click to show motivational phrase...")
    waiting_for_click = True

    while waiting_for_click:
        # Check for button press
        if not button.value:  # Button pressed
            press_start = time.monotonic()

            # Wait for release or check if it becomes a long hold
            while not button.value:
                elapsed = time.monotonic() - press_start

                # If held for 3 seconds, toggle display
                if elapsed >= 3.0:
                    display_on = not display_on
                    if display_on:
                        print("*** Display turned ON ***")
                        display.brightness = 1.0
                    else:
                        print("*** Display turned OFF ***")
                        display.brightness = 0.0

                    # Wait for release
                    while not button.value:
                        time.sleep(0.1)

                    if not display_on:
                        return False
                    # After turning display back on, keep waiting for click
                    break

                time.sleep(0.05)
            else:
                # Button was released - check how long it was held
                hold_time = time.monotonic() - press_start
                if hold_time < 3.0:
                    # It was a quick click!
                    print(f"Button clicked! (held for {hold_time:.2f}s)")
                    waiting_for_click = False
                    time.sleep(0.2)  # Debounce
                    return True

        time.sleep(0.05)

    return True


print("*** Running Matrix Portal M4 HUB75 Code! ***")

# Main Motivational words box Loop
while True:
    # Only run animations if display is on
    if not display_on:
        check_for_quick_click()
        time.sleep(0.1)
        continue

    # If we don't have a current phrase yet, wait for initial click
    if current_phrase is None:
        print("Waiting for first button click to start...")
        while current_phrase is None and display_on:
            button_action = check_for_quick_click()
            if button_action == "click":
                current_phrase = random.choice(motivational_phrases)
                print(f"First phrase selected: {current_phrase}")
            elif button_action == "toggle":
                if not display_on:
                    break
            time.sleep(0.05)

        if not display_on:
            continue

    # Play intro animation - check for new phrase request
    anim_result = screen_fill_animation(duration=4.0)
    if anim_result == "new_phrase":
        current_phrase = random.choice(motivational_phrases)
        print(f"New phrase selected: {current_phrase}")
        continue

    if not display_on:
        continue

    # Show intro message
    try:
        gc.collect()
        msg1, msg2, logo_path, color = intro_message
        scroll_group, content_width = create_scroll_group(logo_path, msg1, msg2, color)
        scroll_group.x = WIDTH
        main_group.append(scroll_group)

        interrupted = False
        while scroll_group.x > -content_width - 32:
            button_action = check_for_quick_click()
            if button_action == "click":
                current_phrase = random.choice(motivational_phrases)
                print(f"New phrase selected: {current_phrase}")
                interrupted = True
                break
            elif button_action == "toggle" and not display_on:
                interrupted = True
                break
            scroll_group.x -= SCROLL_STEP
            time.sleep(SCROLL_DELAY)

        # Always try to remove the scroll_group if it's in main_group
        try:
            main_group.remove(scroll_group)
        except ValueError:
            pass  # Already removed, no problem
        gc.collect()

        if not interrupted:
            time.sleep(0.5)
    except MemoryError:
        print("MemoryError! Trying to recover...")
        main_group = displayio.Group()
        display.root_group = main_group
        gc.collect()
        time.sleep(1)

    if not display_on:
        continue

    # Show the current motivational phrase continuously until button click
    print(f"Showing phrase continuously: {current_phrase}")
    phrase_interrupted = False

    while not phrase_interrupted and display_on:
        try:
            gc.collect()
            scroll_group, content_width = create_scroll_group("/graphics/baldwineagle.bmp", current_phrase, "",
                                                              GOLDENROD)
            scroll_group.x = WIDTH
            main_group.append(scroll_group)

            while scroll_group.x > -content_width - 32:
                button_action = check_for_quick_click()
                if button_action == "click":
                    # Pick a new phrase that's different from the current one
                    new_phrase = random.choice(motivational_phrases)
                    while new_phrase == current_phrase and len(motivational_phrases) > 1:
                        new_phrase = random.choice(motivational_phrases)
                    current_phrase = new_phrase
                    print(f"New phrase selected: {current_phrase}")
                    phrase_interrupted = True
                    break
                elif button_action == "toggle" and not display_on:
                    phrase_interrupted = True
                    break
                scroll_group.x -= SCROLL_STEP
                time.sleep(SCROLL_DELAY)

            # Always try to remove the scroll_group if it's in main_group
            try:
                main_group.remove(scroll_group)
            except ValueError:
                pass  # Already removed, no problem
            gc.collect()

            # Small pause before repeating the same phrase
            if not phrase_interrupted:
                time.sleep(0.5)

        except MemoryError:
            print("MemoryError! Trying to recover...")
            main_group = displayio.Group()
            display.root_group = main_group
            gc.collect()
            time.sleep(1)
