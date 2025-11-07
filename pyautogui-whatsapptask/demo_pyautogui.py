import pyautogui
import pyperclip
import time

# #  to check position
# print("Move your mouse over the WhatsApp search bar within 5 seconds...")
# time.sleep(5)
# print("Your mouse position is:", pyautogui.position())

# time.sleep(3)  # Time to prepare

# Open WhatsApp Desktop
pyautogui.press('win')
time.sleep(1)
pyperclip.copy("WhatsApp")
pyautogui.hotkey('ctrl', 'v')
time.sleep(1)
pyautogui.press('enter')
time.sleep(1)

# Search for the group
pyperclip.copy("SE - AI-B3 - 1")
# pyautogui.hotkey('ctrl', 'f')  # or click manually
# pyautogui.click(274, 247)
# time.sleep(1)
pyautogui.hotkey('ctrl', 'v')
pyautogui.press('enter')
time.sleep(2)
pyautogui.click(274, 247)

# Send the message
pyperclip.copy("Pyautogui demo whatsapp task Completed")
pyautogui.hotkey('ctrl', 'v')
time.sleep(1)
pyautogui.press('enter')
time.sleep(2)
pyautogui.hotkey('alt', 'f4')