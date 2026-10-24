"""Plays the protocols of Tracking Selection Fix: Terminate, Recover, End Track, an object lost, a filter, and the
clicks that already worked.

It drives KSP through KSP-Util-MCPServer, a mod that answers HTTP requests on 127.0.0.1, and needs nothing but
Python 3: no AI, no package to install. Start KSP with KSP-Util-MCPServer installed, copy tracking-selection.sfs
and tracking-selection-lost.sfs into a sandbox game, then run:

    python run-selection.py --folder <your sandbox game> --out out

tracking-selection.sfs holds, around Kerbin, a capsule in orbit (Capsule, a ship), a probe (Puceron), a station
(Quad-Rocket), a rover on the runway (Rover, the active vessel), and a tracked asteroid (Ast. JCX-422), plus nine
untracked asteroids, which keep the game from finding new ones. tracking-selection-lost.sfs is the same, but one
of the untracked asteroids is lost a minute after the save's time. Each protocol loads its save from the space
centre (the game is opened there first when KSP is at its main menu), then goes to the tracking station as its
button does, and closes a welcome message by its button if one shows.

With a mod that shows its own rows in place of the tracking station's list, read_tracking_station reads that
mod's rows, and "click the top row" clicks the row of the vessel on top of the station's own list, which the mod
hides: Capsule, in every protocol.

The script plays the game as it stands: the mods installed and the size of the window are set before KSP starts.
It clicks with the server's mouse tools, mouse_move and mouse_click, which move the game's pointer and press its
buttons as a mouse does, and finds what it clicks with read_tracking_station (the rows of the list and the
buttons, with where they lie on screen) and read_dialogs (the buttons of a confirmation dialog). The confirmation
button is the first button of the dialog. The filter buttons are found by moving the pointer along the top bar
and reading which interface objects lie under it.

Terminate (--protocol terminate): click Puceron; click Terminate and confirm; click the top row.
Recover (--protocol recover): click Rover; click Recover and confirm; close the recovery report; click the top row.
End Track (--protocol end-track): click Ast. JCX-422; click its End Track button and confirm; click the top row.
An object lost (--protocol lost-object): load tracking-selection-lost.sfs, click nothing until KSP.log says that
an object is lost; click the top row.
A filter (--protocol filter): click Quad-Rocket; right-click the Ships filter, which shows ships alone; click the
top row; click Fly.
The clicks that already worked (--protocol clicks): click Capsule; click it again; double-click Puceron.

A screenshot is taken after every step, as a PNG the size of the window, the pointer resting on empty space. With
Pillow installed, each is also cropped as the pages show it, 640 pixels wide, as a JPEG: in the tracking station,
its left part, from the list to the middle of the screen; in flight, the top middle quarter of the window, the
altimeter and the vessel. The script prints each
point it clicks with the object under it, and writes them to runs.json with what read_tracking_station reads after
each step. KSP is left running at the end.
"""
import argparse
import json
import os
import time
import urllib.request

URL = None

# The crop of the tracking station: the left part of the window, from the list of tracked objects to a little past
# the middle, where the name of the object the view centres on shows (760 of 1280 pixels).
STATION_CROP_WIDTH = 0.59

# How long the view takes to turn to a vessel and the interface to settle after a click, in seconds.
SETTLE = 2.0


def call(tool, **args):
    """Calls one tool of KSP-Util-MCPServer and returns its answer, decoded from JSON when it is JSON."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                       "params": {"name": tool, "arguments": args}}).encode()
    request = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=900) as response:
        result = json.loads(response.read())["result"]
    text = result["content"][0].get("text", "") if result["content"] else ""
    if result.get("isError"):
        raise RuntimeError(tool + ": " + text)
    try:
        return json.loads(text)
    except ValueError:
        return text


def log(*parts):
    print(time.strftime("%H:%M:%S"), *parts, flush=True)


def summary(station):
    """What read_tracking_station reads, in short: the vessel selected, the rows lit, the buttons that respond."""
    brief = {"selected": station["selected"],
             "lit": [row["vessel"] for row in station["rows"] if row["lit"]],
             "rows": [row["vessel"] for row in station["rows"]],
             "respond": [name for name, button in station["buttons"].items() if button.get("responds")]}
    if station.get("listReplaced"):
        # Another mod shows its own rows: the station's own list, hidden, is the one the protocols are about.
        brief["stationLit"] = [row["vessel"] for row in station["stationRows"] if row["lit"]]
        brief["stationRows"] = [row["vessel"] for row in station["stationRows"]]
    return brief


class Run:
    """One protocol played: its screenshots, the points it clicked, and the station after each step."""

    def __init__(self, out, ksp_folder):
        self.out = out
        self.ksp_folder = ksp_folder
        self.steps = []
        answer = call("mouse_move", x=0, y=100)
        self.width, self.height = answer["window"]["width"], answer["window"]["height"]
        # Empty space in the tracking station, right of the list, below the top bar, above the bottom buttons.
        self.rest = (round(self.width * 0.75), round(self.height * 0.5))

    def park(self, seconds=SETTLE):
        """Rests the pointer on empty space, and lets the game settle."""
        call("mouse_move", x=self.rest[0], y=self.rest[1])
        time.sleep(seconds)

    def station(self):
        return call("read_tracking_station")

    def shot(self, name):
        """Rests the pointer, takes a screenshot named after the step, crops it as the pages show it, and records
        the station as read_tracking_station reads it, when in the tracking station."""
        self.park()
        path = os.path.abspath(os.path.join(self.out, name + ".png"))
        call("screenshot", path=path, return_image=False)
        step = {"step": name, "screenshot": name + ".png"}
        scene = call("get_state")["scene"]
        if scene == "TRACKSTATION":
            step["station"] = summary(self.station())
            box = (0, 0, round(self.width * STATION_CROP_WIDTH), self.height)
        else:
            step["scene"] = scene
            # The top middle of the window: the altimeter, and the vessel at the centre.
            box = (self.width // 4, 0, self.width * 3 // 4, self.height // 2)
        self.steps.append(step)
        log(name, json.dumps(step.get("station", scene), ensure_ascii=False))
        crop_image(path, os.path.join(self.out, "cropped", name + ".jpg"), box)

    def click(self, x, y, what, button="left", count=1):
        """Clicks (or double-clicks) at x, y, and records the point and the object that takes the click there."""
        # The pointer goes there first: what lies under it before the click, the click itself changing it.
        objects = call("mouse_move", x=x, y=y)["ui"]
        under = objects[0].get("clickHandler") if objects else None
        call("mouse_click", x=x, y=y, button=button, count=count)
        self.steps.append({"click": what, "x": x, "y": y, "button": button, "count": count, "under": under})
        log("%s %s at %d, %d (%s), over %s" % (button, "double click" if count == 2 else "click", x, y, what, under))

    def click_row(self, vessel, count=1):
        """Clicks the middle of the row of a vessel."""
        rows = [row for row in self.station()["rows"] if row["vessel"] == vessel]
        if not rows:
            raise RuntimeError("no row for " + vessel)
        self.click(rows[0]["x"], rows[0]["y"], "row of " + vessel, count=count)

    def click_top_row(self):
        """Clicks the middle of the top row. When another mod shows its own rows in place of the station's list,
        clicks the row of the vessel on top of the station's own list, hidden: the row the protocols are about."""
        station = self.station()
        rows = station["rows"]
        if not rows:
            raise RuntimeError("the list is empty")
        if station.get("listReplaced"):
            vessel = station["stationRows"][0]["vessel"]
            row = [r for r in rows if r["vessel"] == vessel]
            if not row:
                raise RuntimeError("no row shown for " + vessel)
            self.click(row[0]["x"], row[0]["y"], "row of " + vessel + ", on top of the station's own list")
            return
        self.click(rows[0]["x"], rows[0]["y"], "top row, " + rows[0]["vessel"])

    def click_button(self, name):
        """Clicks the middle of a button of the tracking station: Fly, Recover, Terminate."""
        button = self.station()["buttons"][name]
        if not button.get("responds"):
            raise RuntimeError(name + " does not respond")
        self.click(button["x"], button["y"], name + " button")

    def confirm(self, dialog):
        """Clicks the first button of the confirmation dialog of that name, once it shows."""
        for _ in range(20):
            found = [d for d in call("read_dialogs") if d["name"] == dialog]
            if found:
                button = found[0]["buttons"][0]
                self.click(button["x"], button["y"], "%s, button %s" % (dialog, button["label"]))
                return
            time.sleep(0.25)
        raise RuntimeError("no dialog " + dialog)

    def filter_point(self, name):
        """The middle of the button of a filter of the top bar."""
        wanted = "Button " + name
        # The buttons touch the top of the screen, in its middle half: their run along the third row of pixels,
        # then the run down the column through its middle.
        xs = [x for x in range(self.width // 4, self.width * 3 // 4)
              if wanted in [o["name"] for o in call("mouse_move", x=x, y=2)["ui"]]]
        if not xs:
            raise RuntimeError("no button of the filter " + name)
        x = (xs[0] + xs[-1]) // 2
        ys = [y for y in range(0, self.height // 4)
              if wanted in [o["name"] for o in call("mouse_move", x=x, y=y)["ui"]]]
        return x, (ys[0] + ys[-1]) // 2

    def log_count(self, text):
        """How many lines of KSP.log contain text."""
        with open(os.path.join(self.ksp_folder, "KSP.log"), "rb") as f:
            return sum(1 for line in f.read().decode("utf-8", "replace").splitlines() if text in line)

    def wait_flight(self):
        """Waits until the flight is up, after Fly or a double click."""
        for _ in range(120):
            state = call("get_state")
            if state["scene"] == "FLIGHT" and state.get("vessel"):
                self.steps.append({"flying": state["vessel"]["name"]})
                log("flying", state["vessel"]["name"])
                time.sleep(5)
                return
            time.sleep(1)
        raise RuntimeError("no flight after Fly")


def crop_image(source, target, box):
    """Crops a screenshot to box (left, top, right, bottom; None for the whole image) and saves it 640 pixels
    wide as a JPEG. Does nothing without Pillow."""
    try:
        from PIL import Image
    except ImportError:
        return
    image = Image.open(source).convert("RGB")
    if box is not None:
        image = image.crop(box)
    image = image.resize((640, round(image.height * 640 / image.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    image.save(target, quality=88)


def start(options, out, save):
    """Loads the save into flight, from the space centre, then goes to the tracking station. Returns the run."""
    state = call("get_state")
    if state["scene"] == "MAINMENU":
        call("open_game", folder=options.folder)
    elif state["scene"] not in ("SPACECENTER", "FLIGHT"):
        call("go_to_scene", scene="SPACECENTER")
    # Right after the game opens, the server may not take the load yet: try again a few seconds later.
    for attempt in range(3):
        try:
            call("load_save", folder=options.folder, save=save)
            break
        except Exception as e:
            if attempt == 2:
                raise
            log("load_save failed, trying again:", e)
            time.sleep(5)
    run = Run(out, call("get_state")["kspFolder"])
    run.park(1)
    call("go_to_scene", scene="TRACKSTATION")
    # On a first visit, a welcome message: closed by its button.
    closed = call("close_screen", dialogs_only=True)
    run.steps.append({"closed": closed})
    # The name of the body the view centres on shows a few seconds at the top of the screen.
    run.park(5)
    run.shot("1-tracking-station")
    return run


def terminate(options, out):
    run = start(options, out, options.save)
    run.click_row("Puceron")
    run.shot("2-puceron-clicked")
    run.click_button("Terminate")
    run.confirm("TerminateMission")
    run.shot("3-terminated")
    run.click_top_row()
    run.shot("4-top-row-clicked")
    return run.steps


def recover(options, out):
    run = start(options, out, options.save)
    run.click_row("Rover")
    run.shot("2-rover-clicked")
    run.click_button("Recover")
    run.confirm("Recover Vessel")
    time.sleep(3)
    closed = call("close_screen")
    run.steps.append({"closed": closed})
    log("closed:", closed)
    run.shot("3-recovered")
    run.click_top_row()
    run.shot("4-top-row-clicked")
    return run.steps


def end_track(options, out):
    run = start(options, out, options.save)
    run.click_row("Ast. JCX-422")
    run.shot("2-asteroid-clicked")
    # For an object the player does not own, the Terminate button reads End Track.
    run.click_button("Terminate")
    run.confirm("StopTrackingObject")
    run.shot("3-tracking-ended")
    run.click_top_row()
    run.shot("4-top-row-clicked")
    return run.steps


def lost_object(options, out):
    lost = "has been untracked for too long and is now lost"
    run = start(options, out, options.save + "-lost")
    before = run.log_count(lost)
    for _ in range(180):
        if run.log_count(lost) > before:
            break
        time.sleep(1)
    else:
        raise RuntimeError("no object lost after 3 minutes")
    run.steps.append({"log": "an object lost"})
    log("an object lost")
    run.shot("2-object-lost")
    run.click_top_row()
    run.shot("3-top-row-clicked")
    return run.steps


def filter_ships(options, out):
    run = start(options, out, options.save)
    run.click_row("Quad-Rocket")
    run.shot("2-quad-rocket-clicked")
    x, y = run.filter_point("Ships")
    run.click(x, y, "Ships filter", button="right")
    run.shot("3-ships-right-clicked")
    run.click_top_row()
    run.shot("4-top-row-clicked")
    run.click_button("Fly")
    run.wait_flight()
    run.shot("5-fly-clicked")
    return run.steps


def clicks(options, out):
    run = start(options, out, options.save)
    run.click_row("Capsule")
    run.shot("2-capsule-clicked")
    run.click_row("Capsule")
    run.shot("3-capsule-clicked-again")
    run.click_row("Puceron", count=2)
    run.wait_flight()
    run.shot("4-puceron-double-clicked")
    return run.steps


PROTOCOLS = {"terminate": terminate, "recover": recover, "end-track": end_track, "lost-object": lost_object,
             "filter": filter_ships, "clicks": clicks}


def main():
    global URL
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--folder", required=True, help="the sandbox game under saves/ the saves were copied into")
    parser.add_argument("--save", default="tracking-selection",
                        help="the save, without .sfs; the lost object protocol loads <save>-lost")
    parser.add_argument("--protocol", choices=list(PROTOCOLS) + ["all"], default="all")
    parser.add_argument("--out", required=True, help="the folder for runs.json and the screenshots")
    parser.add_argument("--port", type=int, default=8770, help="the port of KSP-Util-MCPServer")
    options = parser.parse_args()
    URL = "http://127.0.0.1:%d/mcp/" % options.port

    names = list(PROTOCOLS) if options.protocol == "all" else [options.protocol]
    runs = {}
    for name in names:
        out = os.path.join(options.out, name)
        os.makedirs(out, exist_ok=True)
        log("protocol", name)
        runs[name] = PROTOCOLS[name](options, out)
        with open(os.path.join(options.out, "runs.json"), "w", newline="\n") as f:
            json.dump(runs, f, indent=1, ensure_ascii=False)
    log("done")


if __name__ == "__main__":
    main()
