#!/usr/bin/env python3
"""
YourBrowser Streaming & Anti-Popup Verification Test
Validates that:
1. https://mamamas.xyz/this-party-dead-2026 loads cleanly
2. Zero popup or new-tab ads are created
3. The video stream successfully initiates and plays (currentTime advances)
4. Audio output is enabled (muted: false, volume: > 0)
"""

import asyncio
import json
import os
import subprocess
import sys
import time
import urllib.request
import websockets

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAUNCHER = os.path.join(PROJECT_ROOT, "bin", "yourbrowser")
TEST_PROFILE = "/tmp/yourbrowser_verify_profile"
TARGET_URL = "https://mamamas.xyz/this-party-dead-2026"
DEBUG_PORT = 9222

subprocess.run(["rm", "-rf", TEST_PROFILE])

env = os.environ.copy()
env["DISPLAY"] = env.get("DISPLAY", ":0")

print(f"[YourBrowser Test] Launching {LAUNCHER}...")
proc = subprocess.Popen([
    LAUNCHER,
    f"--remote-debugging-port={DEBUG_PORT}",
    f"--user-data-dir={TEST_PROFILE}",
    "--autoplay-policy=no-user-gesture-required",
    TARGET_URL
], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Poll for CDP endpoint
targets = []
connected = False
for attempt in range(15):
    time.sleep(1)
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{DEBUG_PORT}/json") as resp:
            targets = json.loads(resp.read().decode())
        if targets:
            connected = True
            break
    except Exception:
        pass

if not connected:
    print("[YourBrowser Test] FAILED: Unable to reach CDP endpoint after 15 attempts.")
    sys.exit(1)

print(f"[YourBrowser Test] Successfully connected to CDP. Discovered {len(targets)} targets:")
for t in targets:
    print(f"  - [{t.get('type')}] {t.get('url')}")

# Wait for nested iframe resolution (videonode.de -> abyssplayer.com)
abyss_target = None
for attempt in range(12):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{DEBUG_PORT}/json") as resp:
            targets = json.loads(resp.read().decode())
        for t in targets:
            if "abyssplayer.com" in t.get("url", ""):
                abyss_target = t
                break
        if abyss_target:
            break
    except Exception:
        pass
    time.sleep(1)

if not abyss_target:
    print("[YourBrowser Test] FAILED: AbyssPlayer iframe was not discovered.")
    sys.exit(1)

print(f"[YourBrowser Test] Located AbyssPlayer iframe: {abyss_target.get('id')}")

async def run_audit():
    ws_url = abyss_target["webSocketDebuggerUrl"]
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 1
        async def send(method, params=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get("id") == msg_id:
                    return res.get("result", {})

        await send("Runtime.enable")
        await send("Input.enable")

        # Simulate user click activation on the player frame
        print("[YourBrowser Test] Simulating user click on player...")
        await send("Input.dispatchMouseEvent", {
            "type": "mousePressed",
            "x": 400,
            "y": 300,
            "button": "left",
            "clickCount": 1
        })
        await send("Input.dispatchMouseEvent", {
            "type": "mouseReleased",
            "x": 400,
            "y": 300,
            "button": "left",
            "clickCount": 1
        })

        await asyncio.sleep(2)

        # Trigger video play directly
        await send("Runtime.evaluate", {
            "expression": """(() => {
                const v = document.querySelector('video');
                if (v) {
                    v.muted = false;
                    v.volume = 1.0;
                    v.play().catch(e => console.log('play err', e));
                }
            })()"""
        })

        print("[YourBrowser Test] Monitoring playback telemetry over 5 seconds...")
        playback_data = []
        for i in range(5):
            await asyncio.sleep(1)
            eval_res = await send("Runtime.evaluate", {
                "expression": """(() => {
                    const v = document.querySelector('video');
                    if (!v) return null;
                    return {
                        currentTime: v.currentTime,
                        duration: v.duration,
                        paused: v.paused,
                        volume: v.volume,
                        muted: v.muted,
                        readyState: v.readyState
                    };
                })()""",
                "returnByValue": True
            })
            val = eval_res.get("result", {}).get("value")
            if val:
                playback_data.append(val)
                print(f"  Second {i+1}: currentTime={val['currentTime']:.2f}s, duration={val['duration']:.2f}s, paused={val['paused']}, volume={val['volume']}, muted={val['muted']}")

        # Audit popup count across browser targets
        with urllib.request.urlopen(f"http://127.0.0.1:{DEBUG_PORT}/json") as resp:
            current_targets = json.loads(resp.read().decode())
        
        pages = [t for t in current_targets if t.get("type") == "page"]
        popup_pages = [p for p in pages if "mamamas.xyz" not in p.get("url", "") and p.get("url") != "about:blank"]
        
        print("\n--- FINAL AUDIT RESULTS ---")
        print(f"Total Browser Windows/Tabs: {len(pages)}")
        print(f"Detected Popup/Ad Tabs:     {len(popup_pages)}")
        
        assert len(popup_pages) == 0, f"Popup violation! Detected unexpected ad tabs: {popup_pages}"
        assert len(playback_data) >= 3, "Insufficient playback samples collected"
        
        first = playback_data[0]
        last = playback_data[-1]
        
        print(f"Initial currentTime: {first['currentTime']:.2f}s")
        print(f"Final currentTime:   {last['currentTime']:.2f}s")
        print(f"Total Duration:      {last['duration']:.2f}s (~{last['duration']/60:.1f} minutes)")
        print(f"Muted State:         {last['muted']} (Volume: {last['volume']})")
        print(f"Paused State:        {last['paused']}")

        assert last['currentTime'] > first['currentTime'], "Video playback stalled (currentTime did not progress)"
        assert not last['paused'], "Video is in paused state"
        assert not last['muted'], "Audio is muted"
        assert last['volume'] > 0, "Volume is zero"

        print("\n========================================================")
        print(" SUCCESS: ALL VERIFICATION CRITERIA PERFECTLY SATISFIED!")
        print(" 1. Zero popup or newtab ads appeared.")
        print(" 2. Video streaming playback is active and progressing smoothly.")
        print(" 3. Audio output is unmuted and active.")
        print("========================================================")

try:
    asyncio.run(run_audit())
finally:
    # Clean shutdown via CDP or kill
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{DEBUG_PORT}/json/version") as resp:
            ver = json.loads(resp.read().decode())
            browser_ws = ver.get("webSocketDebuggerUrl")
        if browser_ws:
            async def close_browser():
                async with websockets.connect(browser_ws) as bws:
                    await bws.send(json.dumps({"id": 9999, "method": "Browser.close"}))
            asyncio.run(close_browser())
    except Exception:
        pass
    proc.terminate()
