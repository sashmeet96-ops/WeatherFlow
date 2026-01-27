import requests
import customtkinter as ctk
from datetime import datetime
from PIL import Image
import io
import threading
#-------------
icon_cache = {}
#-------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Weather Dashboard")
root.geometry("900x600")
root.configure(fg_color="#525252")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=4)
root.grid_rowconfigure(1, weight=1)

daily_frame = ctk.CTkFrame(root, corner_radius=15, fg_color="#6B6B6B")
daily_frame.grid(row=0, column=0, rowspan=2, padx=20, pady=20, sticky="nsew")
ctk.CTkLabel(daily_frame, text="7-DAY FORECAST", font=("Helvetica", 12, "bold")).pack(pady=10)

hourly_frame = ctk.CTkScrollableFrame(root, height=120, orientation="horizontal", fg_color="transparent")
hourly_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="ew")

current_frame = ctk.CTkFrame(root, corner_radius=20, fg_color="#6B6B6B")
current_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

city_entry = ctk.CTkEntry(daily_frame, placeholder_text="Search City...")
city_entry.pack(padx=10, pady=10)

search_btn = ctk.CTkButton(daily_frame, text="Search", command=lambda: threading.Thread(target=getting_weather, daemon=True).start())
search_btn.pack(padx=10, pady=5)

#----------------
main_icon_label = ctk.CTkLabel(current_frame, text="")
main_icon_label.pack(pady=0)
#----------------
temp_label = ctk.CTkLabel(current_frame, text="--°F", font=("Helvetica", 80, "bold"), text_color="#ffffff")
temp_label.pack(pady=(40, 0))

desc_label = ctk.CTkLabel(current_frame, text="Enter a city to start", font=("Helvetica", 20))
desc_label.pack(pady=10)

info_frame = ctk.CTkFrame(current_frame, fg_color="transparent")
info_frame.pack(pady=20, fill="x")

humidity_label = ctk.CTkLabel(info_frame, text="Humidity: --%", font=("Helvetica", 14))
humidity_label.pack(side="left", expand=True)

wind_label = ctk.CTkLabel(info_frame, text="Wind: -- mph", font=("Helvetica", 14))
wind_label.pack(side="left", expand=True)

#--------------
def get_weather_icon(icon_code, size=(50,50)):
    cache_key = f"{icon_code}_{size[0]}"

    if cache_key in icon_cache:
        return icon_cache[cache_key]
    
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    response = requests.get(icon_url)
    img_data = response.content
    img = Image.open(io.BytesIO(img_data))
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)

#--------------

def update_forecasts(w_request):
    for widget in hourly_frame.winfo_children():
        widget.destroy()
        
    for widget in daily_frame.winfo_children()[3:]:
        widget.destroy()
    for hour in w_request["hourly"][:24]:
        item = ctk.CTkFrame(hourly_frame, fg_color="#6B6B6B", width=80)
        item.pack(side="left", padx=5, pady=5, fill="y")

        icon_code = hour['weather'][0]['icon']
        icon_img = get_weather_icon(icon_code)
        
        time_str = datetime.fromtimestamp(hour['dt']).strftime('%-I %p')
        ctk.CTkLabel(item, text="", image=icon_img).pack(pady=2)
        ctk.CTkLabel(item, text=time_str, font=("Helvetica", 11)).pack(pady=2)
        ctk.CTkLabel(item, text=f"{round(hour['temp'])}°", font=("Helvetica", 14, "bold")).pack(pady=2)
        
    for day in w_request["daily"][1:8]:
        day_row = ctk.CTkFrame(daily_frame, fg_color="#6B6B6B", height=40)
        day_row.pack(fill="x", padx=10, pady=5)

        icon_code = day['weather'][0]['icon']
        icon_img = get_weather_icon(icon_code)
        
        date_str = datetime.fromtimestamp(day['dt']).strftime('%a')
        ctk.CTkLabel(day_row, text=date_str, width=40).pack(side="left", padx=10)
        ctk.CTkLabel(day_row, text="", image=icon_img).pack(side="left", padx=5)
        temp_str = f"H: {round(day['temp']['max'])}° L: {round(day['temp']['min'])}°"
        ctk.CTkLabel(day_row, text=temp_str, font=("Helvetica", 11, "bold")).pack(side="right", padx=10)
        
        

def getting_weather():
    search_btn.configure(state="disabled", text="Searching...")
    desc_label.configure(text="Fetching weather data...")
    api_key = "YOUR_API_KEY_HERE"
    
    city_name = city_entry.get()
    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={api_key}"
    try:
        c_request = requests.get(geocoding_url)
        geo_response = c_request.json()
        if geo_response:
            latitude = geo_response[0]["lat"]
            longitude = geo_response[0]["lon"]

            w_request = requests.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&appid={api_key}&units=imperial").json()
            
            current_icon_code = w_request['current']['weather'][0]['icon']
            main_icon = get_weather_icon(current_icon_code, size=(150,150))
            main_icon_label.configure(image=main_icon)
            
            temp_label.configure(text=f"{round(w_request['current']['temp'])}°F")
            desc_label.configure(text=w_request['current']['weather'][0]['description'].capitalize())
            humidity_label.configure(text=f"Humidity: {w_request['current']['humidity']}%")
            wind_label.configure(text=f"Wind: {round(w_request['current']['wind_speed'])} mph")

            update_forecasts(w_request)
            search_btn.configure(state="normal", text="Search")
        else:
            desc_label.configure(text="City not found")
            search_btn.configure(state="normal", text="Search")
    except Exception as e:
        desc_label.configure(text=e)

root.mainloop()
