import subprocess

input_file = "music.mp3"

def parse_time(t):
    m, s = map(int, t.split(":"))
    return m * 60 + s

uinput = input("Enter timestamps: ")
timestamps = [parse_time(t) for t in uinput.split()]

for i in range(len(timestamps) - 1):
    start = timestamps[i]
    duration = timestamps[i + 1] - timestamps[i]

    output = f"output_{i}.mp3"

    subprocess.run([
        "ffmpeg",
        "-i", input_file,
        "-ss", str(start),
        "-t", str(duration),
        "-acodec", "copy",
        output
    ])