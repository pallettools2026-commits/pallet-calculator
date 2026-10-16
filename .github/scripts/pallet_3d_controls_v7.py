from pathlib import Path

path=Path('index.html')
text=path.read_text(encoding='utf-8')
if 'pallet3dControlsV7' in text:
    raise SystemExit('pallet3dControlsV7 already installed')

# Add reset button next to rotate/zoom.
old='<div class="previewActions"><button id="rotatePallet" type="button">↻ &nbsp; Поворот 3D</button><button id="zoomPallet" type="button">⌕ &nbsp; Приблизить</button></div>'
new='<div class="previewActions"><button id="rotatePallet" type="button">↻ &nbsp; Поворот 3D</button><button id="zoomPallet" type="button">⌕ &nbsp; Приблизить</button><button id="resetPalletView" type="button">⌂ &nbsp; Сбросить вид</button></div>'
if old not in text:
    raise SystemExit('preview actions not found')
text=text.replace(old,new,1)

# Make Explode button read Assemble while exploded.
old_btn='<button type="button" data-p3d-mode="explode" class="${pallet3DState.mode===\'explode\'?\'active\':\'\'}">Разнести</button>'
new_btn='<button type="button" data-p3d-mode="explode" class="${pallet3DState.mode===\'explode\'?\'active\':\'\'}">${pallet3DState.mode===\'explode\'?\'Собрать\':\'Разнести\'}</button>'
if old_btn in text:
    text=text.replace(old_btn,new_btn,1)

# Toggle explode instead of reselecting explode forever.
old_handler="root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{pallet3DState.mode=btn.dataset.p3dMode;renderDynamicPallet(L,W)}));"
new_handler="root.querySelectorAll('[data-p3d-mode]').forEach(btn=>btn.addEventListener('click',()=>{const next=btn.dataset.p3dMode;pallet3DState.mode=(next==='explode'&&pallet3DState.mode==='explode')?'3d':next;renderDynamicPallet(L,W)}));"
if old_handler not in text:
    raise SystemExit('mode handler not found')
text=text.replace(old_handler,new_handler,1)

# Add reset behavior after zoom listener.
needle='document.getElementById("zoomPallet")?.addEventListener("click",()=>{document.getElementById("previewStage")?.classList.toggle("zoomed");});'
insert=needle+'\n/* pallet3dControlsV7 */\ndocument.getElementById("resetPalletView")?.addEventListener("click",()=>{pallet3DState.angle=-28;pallet3DState.mode="3d";pallet3DState.selected="all";document.getElementById("previewStage")?.classList.remove("zoomed");rerenderPallet3D();});\ndocument.getElementById("previewStage")?.addEventListener("dblclick",e=>{if(e.target.closest("button"))return;pallet3DState.angle=-28;pallet3DState.mode="3d";pallet3DState.selected="all";document.getElementById("previewStage")?.classList.remove("zoomed");rerenderPallet3D();});'
if needle not in text:
    raise SystemExit('zoom listener not found')
text=text.replace(needle,insert,1)

css=r'''
/* pallet3dControlsV7 */
.previewActions{display:flex;flex-wrap:wrap;gap:10px}
.previewActions button{flex:0 1 auto}
#resetPalletView{background:#f7faf8;color:#36594c;border:1px solid #dbe6e0}
#resetPalletView:hover{background:#eef5f1}
@media(max-width:560px){.previewActions button{flex:1 1 calc(50% - 6px)}#resetPalletView{flex-basis:100%}}
'''
style_end=text.rfind('</style>')
if style_end<0:
    raise SystemExit('style end not found')
text=text[:style_end]+css+'\n'+text[style_end:]

path.write_text(text,encoding='utf-8')
print('pallet3dControlsV7 installed')
