from pydub import AudioSegment

song = AudioSegment.from_wav("../audio2kafka/received_audio.wav")

song = song._spawn(song.raw_data, overrides={
    "frame_rate": int(song.frame_rate * (2.0 ** (2 / 12.0)))
}).set_frame_rate(song.frame_rate)

song.export("pitched_audio.wav", format="wav")