## Info
- I'm aware that `ritoskin_extractor` does not work for additional folders for skins (e.g., aniviaegg, aniviaiceblock, auroraspirits). I'm working on it when I have time.
- Just use `ritoskin_gui` for now, it works for all additional folders, but if you want chroma skins, you should blindly use random skin number to get it. (eg. if skin10.bin is a skin, skin11.bin will be a chroma for it, just look at splash arts to understand which skin and chroma is which)
- You are free to open PRs to solve it (can be a python script, idk).

### for nerds

1. **Champion Folder**: The first folder with a champion name (e.g., `aphelios`) is processed by matching it to the corresponding `.json` file in the `champion_data` folder.
2. **Additional Folders**: After processing the main champion folder, all following folders (e.g., `apheliosturret`) are treated as additional to the main champion until another champion is found. 
- Potential solution or idk:
   - Truncate the champion's base name from the folder name (e.g., `aphelios` from `apheliosturret`).
   - Process the folder as if it were part of the main champion, following the same steps for skin extraction and numbering.
   - When another folder matching a new champion's name from the `champion_data` is encountered (e.g., `ashe`), the process restarts with the new champion and his additional folders.

- It will be a pain, because you need to keep the folder structure.
