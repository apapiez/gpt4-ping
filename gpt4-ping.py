import tkinter as tk
from tkinter import ttk
from ping3 import ping
import time
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class PingGraphApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Ping Graph")
        self.geometry("800x600")

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill="both")

        self.create_widgets()

        self.response_times = []
        self.is_pinging = False
        self.update_rate = 1

    def create_widgets(self):
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.pack(side="top", fill="x")

        self.address_label = ttk.Label(self.controls_frame, text="Server Address:")
        self.address_label.pack(side="left")

        self.address_entry = ttk.Entry(self.controls_frame)
        self.address_entry.pack(side="left", expand=True, fill="x")

        self.ping_button = ttk.Button(self.controls_frame, text="Start Ping", command=self.toggle_ping)
        self.ping_button.pack(side="left")

        self.clear_button = ttk.Button(self.controls_frame, text="Clear Graph", command=self.clear_graph)
        self.clear_button.pack(side="left")

        self.rate_label = ttk.Label(self.controls_frame, text="Update Rate (s):")
        self.rate_label.pack(side="left")

        self.rate_spinbox = ttk.Spinbox(self.controls_frame, from_=1, to=60, increment=1, width=5, command=self.set_update_rate)
        self.rate_spinbox.set(1)
        self.rate_spinbox.pack(side="bottom")

        self.ping_stats_frame = ttk.Frame(self.main_frame)
        self.ping_stats_frame.pack(side="top", fill="x")


        self.average_ping_label = ttk.Label(self.ping_stats_frame, text= "Average ping = 0 ms")
        self.average_ping_label.pack(side="left")

        self.ping_stdev_label = ttk.Label(self.ping_stats_frame, text="Ping Stdev = 0 ms")
        self.ping_stdev_label.pack(side="right")

        self.failed_pings_label = ttk.Label(self.ping_stats_frame, text="Percentage of failed pings = 0%")
        self.failed_pings_label.pack()


    

        self.figure = Figure(figsize=(7, 5), dpi=100)
        self.plot = self.figure.add_subplot(1, 1, 1)
        self.plot.set_title("Ping Response Time")
        self.plot.set_xlabel("Time (s)")
        self.plot.set_ylabel("Response Time (ms)")

        self.canvas = FigureCanvasTkAgg(self.figure, self.main_frame)
        self.canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)

    def toggle_ping(self):
        if self.is_pinging:
            self.is_pinging = False
            self.ping_button.config(text="Start Ping")
        else:
            self.is_pinging = True
            self.ping_button.config(text="Stop Ping")
            self.start_pinging()

    def clear_graph(self):
        self.response_times = []
        self.plot.clear()
        self.plot.set_title("Ping Response Time")
        self.plot.set_xlabel("Time (s)")
        self.plot.set_ylabel("Response Time (ms)")
        self.canvas.draw_idle()

    def set_update_rate(self):
        self.update_rate = float(self.rate_spinbox.get())

    def start_pinging(self):
        if not self.is_pinging:
            return

        address = self.address_entry.get()
        if not address:
            return
        
        try:
            response_time = ping(address)
            if response_time is None:
                # If the ping fails, set the response time to 0 ms
                response_time = 0
            else:
                response_time = ping(address) * 1000  # Convert seconds to milliseconds
        except:
            response_time = 0

        self.response_times.append(response_time)
        self.update_average_response_time_label()
        self.update_ping_stdev_label()
        self.update_percentage_failed_pings_label()

        self.plot.clear()
        self.plot.plot(self.response_times)
        self.plot.set_title("Ping Response Time")
        self.plot.set_xlabel("Time (s)")
        self.plot.set_ylabel("Response Time (ms)")

        self.canvas.draw_idle()

        threading.Timer(self.update_rate, self.start_pinging).start()

    def calculate_average_ping_time(self):
        total = 0
        for time in self.response_times:
            total += time
        result = total / len(self.response_times)
        result = str(result)[:4]
        return result

    def update_average_response_time_label(self):
        self.average_ping_label.config(text="Average ping = {} ms".format(self.calculate_average_ping_time()))

    def calculate_ping_stdev(self):
        average = float(self.calculate_average_ping_time())
        total = 0
        for time in self.response_times:
            #convert the time to a float
            time = float(time)
            total += (time - average)**2
        result = (total / len(self.response_times))**0.5
        result = str(result)[:4]
        return result

    def update_ping_stdev_label(self):
        self.ping_stdev_label.config(text="Ping Stdev = {} ms".format(self.calculate_ping_stdev()))

    def calculate_percentage_failed_pings(self):
        #calculate the percentage of entries in the response_times list that are 0
        total = 0
        n = len(self.response_times)
        for time in self.response_times:
            if float(time) < 0.001:
                total += 1
        result = (total / n) * 100
        result = str(result)[:4]
        return result

    def update_percentage_failed_pings_label(self):
        self.failed_pings_label.config(text="Percentage of failed pings = {}%".format(self.calculate_percentage_failed_pings()))
        




        


if __name__ == "__main__":
    app = PingGraphApp()
    app.mainloop()
