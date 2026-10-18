from pathlib import Path

path = Path("assets/pallet3d-v10.js")
text = path.read_text(encoding="utf-8")

old_head = """    const pickDeckByProjection=(clientX,clientY)=>{\n      const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height||!inspectable.length)return null;"""
new_head = """    const deckInspectables=inspectable.filter(mesh=>mesh?.userData?.palletInspect?.kind==='deck');\n    const pickDeckByProjection=(clientX,clientY)=>{\n      const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height||!deckInspectables.length)return null;"""

old_loop = """      inspectable.forEach((mesh,i)=>{\n        const x=topXs[i]??mesh.position.x;"""
new_loop = """      deckInspectables.forEach((mesh,i)=>{\n        const x=topXs[i]??mesh.position.x;"""

old_select = """    const selectAt=(clientX,clientY)=>{if(!pickerEnabled)return false;const projected=pickDeckByProjection(clientX,clientY);if(projected)return showInspect(projected.object);const hit=pickAt(clientX,clientY);return hit?showInspect(hit.object):false;};"""
new_select = """    const selectAt=(clientX,clientY)=>{if(!pickerEnabled)return false;const hit=pickAt(clientX,clientY);if(hit)return showInspect(hit.object);if(mode==='top'){const projected=pickDeckByProjection(clientX,clientY);if(projected)return showInspect(projected.object);}return false;};"""

for old, new, label in [
    (old_head, new_head, "deck picker head"),
    (old_loop, new_loop, "deck picker loop"),
    (old_select, new_select, "selection order"),
]:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one {label} pattern, found {count}")
    text = text.replace(old, new, 1)

# Selection UI must stay disabled in the normal 3D mode.
required = "const pickerEnabled=mode==='top'||mode==='side'||mode==='explode';"
if required not in text:
    raise SystemExit("Picker mode guard changed unexpectedly")

path.write_text(text, encoding="utf-8")
print("Updated pallet part picker: real meshes first; deck fallback only in top view; normal 3D remains non-interactive.")
