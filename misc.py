import time

def timer(t, message="Time's up!"):
    """
    Function Takes second input and pauses program
    for that amount of time

    Optional parameter:
        message: default "Time's up!"
        string to print upon conclusion of the function
        if message == None, nothing will be printed
    """
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")  # Overwrite previous output
        time.sleep(1)
        t -= 1
    if (message != None):
        print(message)

