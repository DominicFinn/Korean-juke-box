# Lofi Jukebox

A little Mac app, 아빠의 멋진 로파이 앱 (Dad's Cool Lofi App), that plays the loops in `../out` like a jukebox. All its text is in Korean, with each tape's English name underneath. Each tape plays a set number of times, then crossfades into the next. Oreo and Milo, the Finn cats (also in Seoul Sisters), sit on the windowsill and bounce along in time, and doze off when it's paused.

## Build and run

```
./build.sh
open "build/Lofi Jukebox.app"
```

`build.sh` compiles a release build, draws the app icon, bundles the cat art and bakes in the path to `../out`. Drag the app into Applications if you want it in Launchpad; it still finds the tapes.

## Using it

- New renders turn up on their own. The app checks the folder every couple of seconds, and if the tape that's playing gets re-rendered it swaps the new version in.
- Space plays and pauses, Cmd and the arrow keys skip tapes, and the keyboard's media keys work too.
- 반복 loops the current tape forever, which is handy for listening for the seam.
- ×2 번씩 sets how many times each tape plays before the next one.
- The folder button picks a different folder. Choosing the music-electro folder itself works too.

## How it's put together

- `Playback/`: an AVAudioEngine with two decks, so one tape fades out while the next fades in. Loops are scheduled with `.loops`, which repeats the buffer sample-accurately.
- `Library/`: reads `tracks.json` from render.py, or falls back to any WAVs in the folder.
- `Scene/`: the window scene. SwiftUI paints the still parts once into images, and Core Animation runs everything that moves (rain particles, the cats' beat-synced bounce, twinkling, flickering windows), so the app idles at around 1.5% CPU while it plays. The neon glow follows the music ten times a second.
- `Deck/`, `Shelf/`, `Theme/`: the cassette, the tape shelf, and the comic styling. Korean text uses Apple SD Gothic Neo and AppleMyungjo, which come with macOS.

`--snapshot <file.png>` saves a picture of the window after a few seconds and quits, which is useful for checking layout changes. It shows animations at rest, so the rain and notes don't appear.
