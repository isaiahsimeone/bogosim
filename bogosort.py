import tkinter as tk
import random
import time

import numpy as np
import simpleaudio as sa

SIM_HEIGHT = 500 * 1.4
SIM_WIDTH = 1000 * 1.4
FINISH_WAIT = 1

window = tk.Tk()

# https://compucademy.net/retro-sound-effects-in-python/
def get_sound(note, duration, volume=0.4):
    time_vector = np.linspace(0, duration, int(duration * 8000), False)
    # frequency = 440 * 2 ** ((note - 49) / 12)  # 440Hz is key 49 on a piano
    frequency = 220 * 2 ** (note / 48)
    # Generate audio samples
    audio = np.sin(frequency * time_vector * 2 * np.pi)
    # normalize to 16-bit range
    audio *= volume * 32767 / np.max(np.abs(audio))

    # Fade out the end
    release_time = 0.05  # Seconds
    if duration >= release_time:
        release_samples = int(np.ceil(release_time * 8000))
        fade_curve = np.linspace(volume, 0.0, num=release_samples)
        audio[-release_samples:] *= fade_curve

    # convert to 16-bit data
    audio = audio.astype(np.int16)
    return audio


def play(blip):
    wave_object = sa.WaveObject(blip, 1, 2, 8000)
    play_object = wave_object.play()
    play_object.wait_done()


def play_multi(blips):
    for blip in blips:
        play(blip)


def success_chime():
    p = 0.12
    tune = [get_sound(60, p), get_sound(50, p), get_sound(60, p), get_sound(60, 0.5)]
    tune += [get_sound(60, p), get_sound(50, p), get_sound(60, p), get_sound(60, 0.5)]
    tune += [get_sound(60, p), get_sound(50, p), get_sound(60, p), get_sound(60, p), get_sound(50, p), get_sound(60, p),
             get_sound(60, 0.6)]

    play_multi(tune)

    return p * 12 + 0.5 * 2 + 0.6


class SimulationCanvas:
    def __init__(self):
        self.canvas = tk.Canvas(window, bg="black", height=SIM_HEIGHT, width=SIM_WIDTH)
        self.rectangles = []
        self.colours = ["white"]
        self.numbers = [1]
        self.addNewRectangle()
        self.addNewRectangle()
        self.drawRectangles()

        self.streak = 0
        self.start_time = 0
        self.absolute_start_time = time.time()
        self.iterations = 1
        self.streak_text = tk.Label(window)
        self.runtime_text = tk.Label(window)
        self.iterations_text = tk.Label(window)
        self.absolute_start_time_text = tk.Label(window)

    def fullShuffle(self):
        random.shuffle(self.numbers)

    def shuffle(self):
        # select two random blocks and swap them
        rand1 = random.randrange(0, len(self.numbers))
        rand2 = random.randrange(0, len(self.numbers))
        self.colours[rand1] = 'red'
        self.colours[rand2] = 'red'
        self.update()
        time.sleep(0.0001)
        temp = self.numbers[rand2]
        self.numbers[rand2] = self.numbers[rand1]
        self.numbers[rand1] = temp

    def isSorted(self):
        current_streak = 1
        for i in range(0, len(self.numbers)):
            # First element is in ascending order always
            if i == 0:
                self.colours[i] = "green"
            # Green if larger than previous number
            elif self.numbers[i] > self.numbers[i - 1]:
                self.colours[i] = "green"
                current_streak += 1
                if current_streak > self.streak:
                    self.streak = current_streak
                if i > len(self.numbers)*0.4:
                    play(get_sound((i + 2) * 100, 0.05))
            else:
                # Not in sorted order. Out of order block flashes red
                self.colours[i] = "red"
                self.update()
                # Reset everything to white
                for i in range(0, len(self.numbers)):
                    self.colours[i] = "white"
                return False
            time.sleep(0.0001)
            self.update()
        self.update()
        return True

    def bogosort(self):
        self.start_time = time.time()
        self.shuffle()
        self.update()
        # Do bogosort
        while not self.isSorted():
            self.iterations += 1
            self.shuffle()
            self.update()


        # Found solution
        self.update()
        chime_time_taken = success_chime()
        time.sleep(FINISH_WAIT)
        # Pause the total runtime clock by adding the time taken by the chime
        self.absolute_start_time += FINISH_WAIT + chime_time_taken
        # Reset everything
        self.start_time = 0
        self.streak = 0
        self.iterations = 0

    def increaseProblemSize(self):
        self.numbers.append(len(self.numbers) + 1)
        self.addNewRectangle()
        self.colours.append("white")
        self.update()

    def drawRectangles(self):
        block_width = SIM_WIDTH / len(self.numbers)

        i = 0
        for h in self.numbers:
            self.canvas.delete(self.rectangles[i])
            self.rectangles[i] = self.canvas.create_rectangle(block_width * i, SIM_HEIGHT, block_width * (i + 1),
                                                              SIM_HEIGHT - 30 * h, fill=self.colours[i])
            i += 1

    def addNewRectangle(self):
        self.rectangles.append(self.canvas.create_rectangle(0, 0, 0, 0))

    def update(self):
        self.drawRectangles()
        self.canvas.pack()
        self.canvas.update()

        # Update bottom pane stats
        self.iterations_text.config(text="Iterations: " + str(self.iterations))
        self.streak_text.config(text="Longest Streak: " + str(self.streak))
        self.runtime_text.config(text="Runtime: " + convert_to_preferred_format(time.time() - self.start_time))
        self.absolute_start_time_text.config(
            text="Total Time Spent Bogosorting: " + convert_to_preferred_format(time.time() - self.absolute_start_time))
        self.iterations_text.pack()
        self.streak_text.pack()
        self.runtime_text.pack()
        self.absolute_start_time_text.pack(side="right")


sim = SimulationCanvas()


def convert_to_preferred_format(sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return "%04d:%02d:%02d" % (h, m, s)


def task():
    sim.fullShuffle()
    sim.bogosort()
    sim.increaseProblemSize()
    window.after(200, task)


def main():
    window.after(200, task)
    window.mainloop()


if __name__ == "__main__":
    main()
