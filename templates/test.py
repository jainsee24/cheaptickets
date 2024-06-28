from pynput import mouse
import time
import threading

# Create a mouse controller object
mouse_controller = mouse.Controller()

# Scroll down function
def scroll_down(amount=1):
    mouse_controller.scroll(0, -amount)

# Function to automatically scroll every second
def auto_scroll():
    while True:
        scroll_down()
        time.sleep(0.1)

# Start the auto-scrolling in a separate thread
scroll_thread = threading.Thread(target=auto_scroll)
scroll_thread.daemon = True  # This makes sure the thread exits when the main program exits
scroll_thread.start()

# Mouse event listener
def on_move(x, y):
    # This function can be used to add additional logic if needed
    pass

# Start listening to mouse events (not strictly needed for auto-scroll but can be used for future enhancements)
with mouse.Listener(on_move=on_move) as listener:
    # Keep the script running
    try:
        listener.join()
    except KeyboardInterrupt:
        listener.stop()
