#!/usr/bin/env python3
"""Apply the Android-only landscape and immersive-display configuration."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
ANDROID = ROOT / "android"
MANIFEST = ANDROID / "app" / "src" / "main" / "AndroidManifest.xml"
ANDROID_NS = "http://schemas.android.com/apk/res/android"
ET.register_namespace("android", ANDROID_NS)

if not MANIFEST.is_file():
    raise SystemExit(f"AndroidManifest.xml não encontrado: {MANIFEST}")

tree = ET.parse(MANIFEST)
root = tree.getroot()
activity = next(
    (
        node
        for node in root.iter("activity")
        if node.get(f"{{{ANDROID_NS}}}name", "").endswith("MainActivity")
    ),
    None,
)
if activity is None:
    raise SystemExit("Activity MainActivity não encontrada no AndroidManifest.xml")

activity.set(f"{{{ANDROID_NS}}}screenOrientation", "landscape")
activity.set(
    f"{{{ANDROID_NS}}}configChanges",
    "orientation|screenSize|screenLayout|keyboardHidden",
)
tree.write(MANIFEST, encoding="utf-8", xml_declaration=True)

java_file = next(ANDROID.glob("app/src/main/java/**/MainActivity.java"), None)
if java_file is None:
    raise SystemExit("MainActivity.java não encontrado no projeto Android gerado")

source = java_file.read_text(encoding="utf-8")
match = re.search(r"^package\s+([\w.]+);", source, re.MULTILINE)
if not match:
    raise SystemExit("Não foi possível identificar o package da MainActivity")

package = match.group(1)
java_file.write_text(
    f'''package {package};

import android.os.Bundle;
import android.view.View;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {{
    private void enableImmersiveLandscape() {{
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
        );
    }}

    @Override
    public void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        enableImmersiveLandscape();
    }}

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {{
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {{
            enableImmersiveLandscape();
        }}
    }}
}}
''',
    encoding="utf-8",
)
print("Configuração Android aplicada: paisagem fixa, tela imersiva e toque preservado.")
