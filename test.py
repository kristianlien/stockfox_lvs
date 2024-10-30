import time
import os
import msvcrt  # For Windows; use 'getch' on Unix systems

def console_clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_keypress():
    return msvcrt.kbhit()

def animate_fox():
    fox_frames = [
        "  ____\n  \\  /\\  |\\/|\n   \\/  \\_/ ..__.\n    \\__ _\\____/\n       \\_\\_\\",
        "   ____\n   /\\  \\ |\\/|\n   \\/  \\_/ ..__.\n    \\__ _\\____/\n       \\_\\_\\",
    ]

    frame_index = 0

    while True:
        console_clear()
        print("---------- StockFox ----------")
        print("2024 © Lien Vending Solutions")
        print("Version Beta 1.3")
        print("Made in Norway ♥")
        print("Support: stockfox@lienvending.solutions")
        print("")
        print(fox_frames[frame_index])  # Display current frame
        print("")
        print("Press any key to go back to the menu...")

        # Check for keypress
        if get_keypress():
            msvcrt.getch()  # Clear the keypress
            menu()
            return

        # Update the frame index
        frame_index = (frame_index + 1) % len(fox_frames)
        time.sleep(0.3)  # Control the speed of the animation

def menu():
    print("Returning to the menu...")  # Placeholder for your menu function

if __name__ == "__main__":
    animate_fox()
