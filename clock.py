import time 
import threading


class Clock:
    def __init__(self, clock_speed=2):
        """
        Clock is used to track the time. clock_speed is the amount of time th simulation has passed in 1 second of the
        real world time
        """
        
        self.current_time = 0
        self.clock_speed = clock_speed
        self.is_running = False

    def background(self):
        while self.is_running:
            time.sleep(1)
            self.current_time += self.clock_speed

    def run(self):
        self.is_running = True
        self.background_task = threading.Thread(target=self.background)
        self.background_task.start()
    
    def stop(self):
        print("stop clock thread")
        self.is_running = False