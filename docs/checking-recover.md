# Checking Recover

Part of [Tracking Selection Fix](../README.md). A vessel is recovered from the tracking station, then the top row of the list is clicked. Does a single click on it select its vessel? Played without this mod, then with it.

## The install

The same as for [Terminate](checking-terminate.md#the-install).

## The protocol

The save, [tracking-selection.sfs](../diag/tracking-selection.sfs): a sandbox game with, around Kerbin, a
capsule in orbit at 100 km (Capsule, a ship), a probe at 150 km (Puceron), a station at 200 km (Quad-Rocket), a
rover on the runway (Rover, the vessel it opens on), and a tracked asteroid (Ast. JCX-422), plus nine untracked
asteroids, which keep the game from finding new ones while the protocol runs. Every vessel filter is on. Copy it
into the folder of a sandbox game, and load it. Then leave the flight for the space centre, and open the tracking
station. On a first visit, it shows a welcome message: close it.

1. Click Rover.
2. Click *Recover*, and confirm; close the recovery report with its button.
3. Click the top row, Capsule, once.

**Played by a script.** [run-selection.py](../diag/automation/run-selection.py), with `--protocol recover`. It loads the save, goes to the space centre and to the tracking station as the game's buttons do, and closes a welcome message by its button if one shows. It clicks with the mouse tools of KSP-Util-MCPServer, in the middle of each row and button, which it finds with the server's `read_tracking_station`; and the first button of a confirmation dialog, found with `read_dialogs`. It closes the recovery report with the server's `close_screen`, as its button does.

A screenshot follows each step, the mouse resting right of the list. The images below are the left
part of the screen, 755 by 720 pixels, at 640 pixels wide: the list of tracked objects, its buttons at the
bottom (*Recover*, *Terminate* or *End Track*, *Fly*, from left to right; grey when they do not respond), and the
name of the object the view turns to, which shows for a few seconds at the top of the view (*Centrage : …*). A
selected row is darker than the others.

## On stock

Read off the screenshots below:

| Step | Row that looks selected | Message at the top of the view | Buttons that respond |
|---|---|---|---|
| 1. The tracking station | none | none | none |
| 2. Click on Rover | Rover | Centrage : Rover | Recover, Fly |
| 3. Recover | Capsule | none | none |
| 4. Click on the top row | Capsule | none | none |

The top row comes back dark after *Recover*, with no vessel selected, and the click on it changes nothing.

<p class="thumbs"><a href="../imgs/checking-recover/stock/1-tracking-station.jpg"><img src="../imgs/checking-recover/stock/1-tracking-station.jpg" width="96"></a> <a href="../imgs/checking-recover/stock/2-rover-clicked.jpg"><img src="../imgs/checking-recover/stock/2-rover-clicked.jpg" width="96"></a> <a href="../imgs/checking-recover/stock/3-recovered.jpg"><img src="../imgs/checking-recover/stock/3-recovered.jpg" width="96"></a> <a href="../imgs/checking-recover/stock/4-top-row-clicked.jpg"><img src="../imgs/checking-recover/stock/4-top-row-clicked.jpg" width="96"></a></p>

<details>
<summary>The 4 screenshots, on stock</summary>

The tracking station:

![The tracking station, on stock](../imgs/checking-recover/stock/1-tracking-station.jpg)

After the click on Rover:

![After the click on Rover, on stock](../imgs/checking-recover/stock/2-rover-clicked.jpg)

After Recover:

![After Recover, on stock](../imgs/checking-recover/stock/3-recovered.jpg)

After the click on the top row:

![After the click on the top row, on stock](../imgs/checking-recover/stock/4-top-row-clicked.jpg)

</details>

## With this mod

Read off the screenshots below:

| Step | Row that looks selected | Message at the top of the view | Buttons that respond |
|---|---|---|---|
| 1. The tracking station | none | none | none |
| 2. Click on Rover | Rover | Centrage : Rover | Recover, Fly |
| 3. Recover | none | none | none |
| 4. Click on the top row | Capsule | Centrage : Capsule | Terminate, Fly |

No row comes back dark after *Recover*, and the click on the top row selects Capsule.

<p class="thumbs"><a href="../imgs/checking-recover/fix/1-tracking-station.jpg"><img src="../imgs/checking-recover/fix/1-tracking-station.jpg" width="96"></a> <a href="../imgs/checking-recover/fix/2-rover-clicked.jpg"><img src="../imgs/checking-recover/fix/2-rover-clicked.jpg" width="96"></a> <a href="../imgs/checking-recover/fix/3-recovered.jpg"><img src="../imgs/checking-recover/fix/3-recovered.jpg" width="96"></a> <a href="../imgs/checking-recover/fix/4-top-row-clicked.jpg"><img src="../imgs/checking-recover/fix/4-top-row-clicked.jpg" width="96"></a></p>

<details>
<summary>The 4 screenshots, with this mod</summary>

The tracking station:

![The tracking station, with this mod](../imgs/checking-recover/fix/1-tracking-station.jpg)

After the click on Rover:

![After the click on Rover, with this mod](../imgs/checking-recover/fix/2-rover-clicked.jpg)

After Recover:

![After Recover, with this mod](../imgs/checking-recover/fix/3-recovered.jpg)

After the click on the top row:

![After the click on the top row, with this mod](../imgs/checking-recover/fix/4-top-row-clicked.jpg)

</details>
